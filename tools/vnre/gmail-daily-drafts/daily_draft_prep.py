#!/usr/bin/env python3
"""
Gmail Daily Draft Prep — DVN automation
Runs daily at 6:30 AM via launchd. No dependencies on Claude desktop being open.

Logic:
  1. Authenticate Gmail via stored OAuth token (fails loud if expired).
  2. Fetch inbox messages from the last N hours (configurable, default 24).
  3. Filter out newsletters, no-reply senders, receipts, calendar invites,
     and threads where DVN already sent the last message.
  4. Score by category: active clients > leads > coaching clients >
     vendors/partners > other.
  5. Cap at draft_cap (default 15), sorted highest-priority first.
  6. Call Claude API to generate a reply draft in DVN's voice for each one.
  7. Save each reply as a native Gmail draft on the correct thread.
  8. Write a plain-text daily summary log.

Re-auth: python3 daily_draft_prep.py --reauth
"""

import argparse
import base64
import json
import logging
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from pathlib import Path

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ---------------------------------------------------------------------------
# Paths — all relative to this script so it works wherever it's deployed
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"
AUTH_DIR = BASE_DIR / "auth"
CREDENTIALS_PATH = AUTH_DIR / "credentials.json"
TOKEN_PATH = AUTH_DIR / "token.json"
ENV_PATH = BASE_DIR / ".env"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

TODAY = datetime.now().strftime("%Y-%m-%d")
LOG_PATH = LOG_DIR / f"{TODAY}-draft-prep.log"
SUMMARY_PATH = LOG_DIR / f"{TODAY}-summary.txt"

DVN_EMAIL = "david@vannoyre.com"

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.modify",
]

# ---------------------------------------------------------------------------
# Logging — goes to file AND stdout (launchd captures stdout)
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("draft-prep")


# ---------------------------------------------------------------------------
# .env loader — simple, no dependencies
# ---------------------------------------------------------------------------
def load_env() -> None:
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def load_config() -> dict:
    if not CONFIG_PATH.exists():
        log.error("Config file not found: %s", CONFIG_PATH)
        sys.exit(1)
    with open(CONFIG_PATH, encoding="utf-8") as f:
        cfg = json.load(f)
    return cfg


# ---------------------------------------------------------------------------
# Gmail auth
# ---------------------------------------------------------------------------
def get_gmail_service(reauth: bool = False):
    creds = None

    if not reauth and TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token and not reauth:
            try:
                creds.refresh(Request())
                log.info("Gmail token refreshed.")
            except Exception as exc:
                log.error(
                    "GMAIL AUTH EXPIRED — could not auto-refresh: %s\n"
                    "  Fix: run   python3 %s --reauth\n"
                    "  Then complete the browser OAuth flow. Token saves automatically.",
                    exc, __file__,
                )
                sys.exit(2)
        else:
            if not CREDENTIALS_PATH.exists():
                log.error(
                    "No OAuth credentials file found at %s\n"
                    "  Steps:\n"
                    "    1. Go to https://console.cloud.google.com → APIs & Services → Credentials\n"
                    "    2. Create an OAuth 2.0 Client ID (Application type: Desktop app)\n"
                    "    3. Download the JSON and save it to %s\n"
                    "    4. Run: python3 %s --reauth",
                    CREDENTIALS_PATH, CREDENTIALS_PATH, __file__,
                )
                sys.exit(2)
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
            log.info("Gmail authorized via browser.")

        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w", encoding="utf-8") as f:
            f.write(creds.to_json())
        log.info("Token saved to %s", TOKEN_PATH)

    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# Gmail helpers
# ---------------------------------------------------------------------------
def get_header(headers: list[dict], name: str) -> str:
    name_lower = name.lower()
    for h in headers:
        if h["name"].lower() == name_lower:
            return h["value"]
    return ""


def extract_email_address(raw: str) -> str:
    """'John Smith <john@example.com>' → 'john@example.com'"""
    m = re.search(r"<([^>]+)>", raw)
    return (m.group(1) if m else raw).strip().lower()


def extract_display_name(raw: str) -> str:
    """'John Smith <john@example.com>' → 'John Smith'"""
    name = re.sub(r"\s*<[^>]+>", "", raw).strip().strip('"').strip("'")
    return name or extract_email_address(raw)


def extract_plain_text(part: dict) -> str:
    """Recursively pull text/plain from a Gmail message part tree."""
    mime = part.get("mimeType", "")
    if mime == "text/plain":
        data = part.get("body", {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    for sub in part.get("parts", []):
        text = extract_plain_text(sub)
        if text:
            return text
    return ""


def extract_html_as_text(part: dict) -> str:
    """Fallback: pull text/html and strip tags."""
    mime = part.get("mimeType", "")
    if mime == "text/html":
        data = part.get("body", {}).get("data", "")
        if data:
            html = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
            return re.sub(r"<[^>]+>", " ", html)
    for sub in part.get("parts", []):
        text = extract_html_as_text(sub)
        if text:
            return text
    return ""


def get_body(msg: dict, max_chars: int = 4000) -> str:
    payload = msg.get("payload", {})
    text = extract_plain_text(payload) or extract_html_as_text(payload)
    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text[:max_chars]


def is_calendar_invite(msg: dict) -> bool:
    def _scan(part: dict) -> bool:
        if "calendar" in part.get("mimeType", "") or "ical" in part.get("mimeType", ""):
            return True
        return any(_scan(p) for p in part.get("parts", []))
    return _scan(msg.get("payload", {}))


# ---------------------------------------------------------------------------
# Filter helpers
# ---------------------------------------------------------------------------
def matches_any(value: str, patterns: list[str]) -> bool:
    vl = value.lower()
    for p in patterns:
        try:
            if re.search(p.lower(), vl):
                return True
        except re.error:
            if p.lower() in vl:
                return True
    return False


def needs_reply(
    sender_email: str,
    subject: str,
    msg: dict,
    config: dict,
) -> tuple[bool, str]:
    """
    Returns (should_draft, skip_reason).
    skip_reason is empty string when should_draft is True.
    """
    if matches_any(sender_email, config.get("no_reply_patterns", [])):
        return False, "no-reply sender"

    blocked = [b.lower() for b in config.get("sender_blocklist", [])]
    if sender_email in blocked:
        return False, "blocklist"

    allowlist = [a.lower() for a in config.get("sender_allowlist", [])]
    if allowlist and sender_email not in allowlist:
        return False, "not on allowlist"

    if matches_any(subject, config.get("subject_block_keywords", [])):
        return False, "blocked subject keyword"

    if is_calendar_invite(msg):
        return False, "calendar invite"

    return True, ""


# ---------------------------------------------------------------------------
# Priority scoring
# ---------------------------------------------------------------------------
CATEGORY_SCORES = {
    "active_client": 100,
    "lead": 80,
    "coaching_client": 60,
    "vendor_partner": 40,
    "other": 20,
}


def classify(sender_email: str, subject: str, body: str, config: dict) -> tuple[str, int]:
    sl = sender_email.lower()
    text = f"{subject} {body}".lower()

    def _match_list(key: str) -> bool:
        return any(
            entry.lower() in sl or re.search(re.escape(entry.lower()), sl)
            for entry in config.get(key, [])
            if entry
        )

    if _match_list("active_clients"):
        return "active_client", CATEGORY_SCORES["active_client"]
    if _match_list("leads"):
        return "lead", CATEGORY_SCORES["lead"]
    if _match_list("coaching_clients"):
        return "coaching_client", CATEGORY_SCORES["coaching_client"]
    if _match_list("vendors_partners"):
        return "vendor_partner", CATEGORY_SCORES["vendor_partner"]

    # Keyword inference
    if any(kw in text for kw in ["listing", "offer", "contract", "closing", "transaction", "showing", "appointment"]):
        return "lead", CATEGORY_SCORES["lead"]
    if any(kw in text for kw in ["coaching", "session", "coach call", "my numbers", "accountability"]):
        return "coaching_client", CATEGORY_SCORES["coaching_client"]

    return "other", CATEGORY_SCORES["other"]


# ---------------------------------------------------------------------------
# Already-replied check
# ---------------------------------------------------------------------------
def dvn_sent_last_message(service, thread_id: str, after_internal_date_ms: int) -> bool:
    """
    Returns True if the most recent message in the thread AFTER the flagged message
    was sent by DVN — meaning he already replied.
    """
    try:
        thread = service.users().threads().get(
            userId="me", id=thread_id, format="metadata",
            metadataHeaders=["From", "Date"],
        ).execute()
        messages = thread.get("messages", [])
        # Filter to messages AFTER the flagged one
        later = [
            m for m in messages
            if int(m.get("internalDate", 0)) > after_internal_date_ms
        ]
        if not later:
            return False
        latest = max(later, key=lambda m: int(m.get("internalDate", 0)))
        latest_from = get_header(latest.get("payload", {}).get("headers", []), "From")
        latest_email = extract_email_address(latest_from)
        return latest_email == DVN_EMAIL.lower()
    except HttpError:
        return False


def get_existing_draft_thread_ids(service) -> set[str]:
    """Cache thread IDs that already have a draft so we don't double-draft."""
    thread_ids: set[str] = set()
    try:
        result = service.users().drafts().list(userId="me", maxResults=200).execute()
        for draft in result.get("drafts", []):
            try:
                d = service.users().drafts().get(
                    userId="me", id=draft["id"], format="minimal"
                ).execute()
                tid = d.get("message", {}).get("threadId")
                if tid:
                    thread_ids.add(tid)
            except HttpError:
                pass
    except HttpError:
        pass
    return thread_ids


# ---------------------------------------------------------------------------
# Draft generation — Claude API
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """\
You write email replies on behalf of David Van Noy Jr. (DVN).

DVN's voice — mandatory:
- Direct, blunt, declarative. Zero hedging.
- Short sentences. Active voice. Strong verbs.
- Start from the first word — no warm-up, no pleasantries.
- Bullets only when structure genuinely helps execution.
- Confident, professional — never apologetic or mealy-mouthed.

BANNED phrases (never use any of these):
"I'd be happy to", "Great question", "It's important to note",
"Just to clarify", "I hope this helps", "Thank you for reaching out",
"Sounds good", "Absolutely", any motivational cliché, any softening qualifier.

DVN context:
- Broker/Owner, Van Noy Real Estate (VNRE), Kansas City Metro
  (Johnson County KS, Jackson County MO).
- 23+ years, $500M+ closed. Solo listing operation.
- DVN Coaching: 10–12 producing agents at ~$1k/mo.
- Listings-focused. Runs on discipline and systems, not motivation.

Tone by email category:
- active_client: execution-focused, professional, clear next steps.
- lead: confident, direct about the value. No chasing, no pressure.
- coaching_client: accountability-forward, identity-driven, high standards.
- vendor_partner: efficient, professional, no small talk.
- other: default professional + blunt.

Output: email body only. No subject line. No signature. Nothing else.\
"""


def generate_draft_body(
    sender_name: str,
    sender_email: str,
    subject: str,
    body: str,
    category: str,
    client: anthropic.Anthropic,
) -> str:
    user_msg = (
        f"Email from: {sender_name} <{sender_email}>\n"
        f"Subject: {subject}\n"
        f"Category: {category}\n\n"
        f"--- Original email ---\n{body}\n--- End ---\n\n"
        f"Write DVN's reply. Direct, brief. Address the specific ask."
    )
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_msg}],
    )
    return response.content[0].text.strip()


# ---------------------------------------------------------------------------
# Gmail draft creation
# ---------------------------------------------------------------------------
def create_draft(
    service,
    thread_id: str,
    to_raw: str,
    subject: str,
    body: str,
    in_reply_to: str,
) -> str:
    """Creates a Gmail draft in the correct thread. Returns the draft ID."""
    reply_subject = subject if subject.lower().startswith("re:") else f"Re: {subject}"

    msg = MIMEText(body, "plain", "utf-8")
    msg["To"] = to_raw
    msg["Subject"] = reply_subject
    if in_reply_to:
        msg["In-Reply-To"] = in_reply_to
        msg["References"] = in_reply_to

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw, "threadId": thread_id}},
    ).execute()
    return draft["id"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Gmail Daily Draft Prep")
    parser.add_argument(
        "--reauth", action="store_true",
        help="Force re-authorization of Gmail OAuth (opens browser).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Classify and generate drafts but do NOT save them to Gmail.",
    )
    args = parser.parse_args()

    load_env()

    log.info("=" * 60)
    log.info("Gmail Daily Draft Prep — %s", TODAY)
    if args.dry_run:
        log.info("DRY RUN — no drafts will be saved to Gmail")
    log.info("=" * 60)

    config = load_config()

    # ---- Gmail auth ----
    service = get_gmail_service(reauth=args.reauth)
    log.info("Gmail authenticated.")

    # ---- Anthropic auth ----
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error(
            "ANTHROPIC_API_KEY not set.\n"
            "  Add it to %s:\n"
            "    ANTHROPIC_API_KEY=sk-ant-...\n"
            "  Get a key: https://console.anthropic.com",
            ENV_PATH,
        )
        sys.exit(2)
    anthropic_client = anthropic.Anthropic(api_key=api_key)

    # ---- Fetch inbox messages ----
    lookback_hours = config.get("lookback_hours", 24)
    draft_cap = config.get("draft_cap", 15)

    since_dt = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
    since_sec = int(since_dt.timestamp())

    query = f"in:inbox after:{since_sec} -from:me -is:draft"
    log.info("Gmail query: %s", query)

    try:
        result = service.users().messages().list(
            userId="me", q=query, maxResults=150,
        ).execute()
    except HttpError as exc:
        log.error("Gmail API error fetching messages: %s", exc)
        sys.exit(1)

    raw_messages = result.get("messages", [])
    log.info("Inbox messages in last %dh: %d", lookback_hours, len(raw_messages))

    if not raw_messages:
        log.info("Nothing in inbox. Done.")
        _write_empty_summary()
        return

    # ---- Pre-fetch existing drafts to avoid duplicates ----
    existing_draft_threads = get_existing_draft_thread_ids(service)
    log.info("Existing draft threads: %d", len(existing_draft_threads))

    # ---- Filter and score ----
    candidates = []
    skipped = []

    for msg_ref in raw_messages:
        msg_id = msg_ref["id"]
        try:
            msg = service.users().messages().get(
                userId="me", id=msg_id, format="full"
            ).execute()
        except HttpError as exc:
            log.warning("Skipping msg %s — fetch error: %s", msg_id, exc)
            continue

        headers = msg.get("payload", {}).get("headers", [])
        sender_raw = get_header(headers, "From")
        sender_email = extract_email_address(sender_raw)
        sender_name = extract_display_name(sender_raw)
        subject = get_header(headers, "Subject") or "(no subject)"
        message_id_hdr = get_header(headers, "Message-ID")
        thread_id = msg.get("threadId", "")
        internal_date_ms = int(msg.get("internalDate", 0))

        # Already has a draft
        if thread_id in existing_draft_threads:
            skipped.append((sender_email, subject, "existing draft"))
            continue

        # Standard filters
        ok, reason = needs_reply(sender_email, subject, msg, config)
        if not ok:
            skipped.append((sender_email, subject, reason))
            continue

        # DVN already sent the last message in this thread
        if dvn_sent_last_message(service, thread_id, internal_date_ms):
            skipped.append((sender_email, subject, "already replied"))
            continue

        body = get_body(msg)
        category, score = classify(sender_email, subject, body, config)

        candidates.append({
            "msg_id": msg_id,
            "thread_id": thread_id,
            "message_id_hdr": message_id_hdr,
            "sender_raw": sender_raw,
            "sender_email": sender_email,
            "sender_name": sender_name,
            "subject": subject,
            "body": body,
            "category": category,
            "score": score,
            "internal_date_ms": internal_date_ms,
        })

    log.info(
        "After filtering: %d candidates, %d skipped",
        len(candidates), len(skipped),
    )
    for s in skipped:
        log.debug("  SKIP [%s] %s — %s", s[2], s[0], s[1])

    # ---- Sort + cap ----
    candidates.sort(key=lambda x: x["score"], reverse=True)
    if len(candidates) > draft_cap:
        log.info("Capping at %d (dropping %d)", draft_cap, len(candidates) - draft_cap)
        candidates = candidates[:draft_cap]

    # ---- Generate and save drafts ----
    created = []
    failed = []

    for i, c in enumerate(candidates, 1):
        log.info(
            "[%d/%d] %s | %s (%s)",
            i, len(candidates), c["sender_name"], c["subject"], c["category"],
        )

        # Generate body
        try:
            draft_body = generate_draft_body(
                sender_name=c["sender_name"],
                sender_email=c["sender_email"],
                subject=c["subject"],
                body=c["body"],
                category=c["category"],
                client=anthropic_client,
            )
        except Exception as exc:
            log.error("  Claude API error: %s", exc)
            failed.append(c)
            continue

        if args.dry_run:
            log.info("  [DRY RUN] Draft body preview:\n%s", draft_body[:300])
            created.append({**c, "draft_id": "DRY_RUN", "draft_body": draft_body})
            continue

        # Save to Gmail
        try:
            draft_id = create_draft(
                service=service,
                thread_id=c["thread_id"],
                to_raw=c["sender_raw"],
                subject=c["subject"],
                body=draft_body,
                in_reply_to=c["message_id_hdr"],
            )
            log.info("  Draft saved (id=%s)", draft_id)
            created.append({**c, "draft_id": draft_id, "draft_body": draft_body})
        except HttpError as exc:
            log.error("  Gmail draft creation failed: %s", exc)
            failed.append(c)

    # ---- Write summary ----
    _write_summary(created, failed, skipped, lookback_hours, args.dry_run)

    log.info("")
    log.info("Done. %d drafts created, %d failed.", len(created), len(failed))
    log.info("Summary: %s", SUMMARY_PATH)


# ---------------------------------------------------------------------------
# Summary log
# ---------------------------------------------------------------------------
def _write_summary(created: list, failed: list, skipped: list, lookback_hours: int, dry_run: bool) -> None:
    lines = [
        f"Gmail Draft Prep — {TODAY}",
        f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Lookback: {lookback_hours}h{'  [DRY RUN — nothing saved]' if dry_run else ''}",
        f"Drafts created: {len(created)}  |  Failed: {len(failed)}  |  Skipped: {len(skipped)}",
        "",
        "=" * 60,
        "DRAFTS CREATED",
        "=" * 60,
        "",
    ]

    if not created:
        lines.append("(none)")
    else:
        for d in created:
            gist = d["draft_body"].replace("\n", " ").strip()[:120]
            lines += [
                f"FROM:      {d['sender_name']} <{d['sender_email']}>",
                f"SUBJECT:   {d['subject']}",
                f"PRIORITY:  {d['category']} (score={d['score']})",
                f"GIST:      {gist}…",
                "-" * 40,
                "",
            ]

    if failed:
        lines += ["", "=" * 60, "FAILED (no draft created)", "=" * 60, ""]
        for f_ in failed:
            lines.append(f"  {f_['sender_email']} | {f_['subject']}")
        lines.append("")

    SUMMARY_PATH.write_text("\n".join(lines), encoding="utf-8")


def _write_empty_summary() -> None:
    SUMMARY_PATH.write_text(
        f"Gmail Draft Prep — {TODAY}\n"
        f"Run at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        "No messages in inbox for the lookback window.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
