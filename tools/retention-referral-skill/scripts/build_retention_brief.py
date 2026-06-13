#!/usr/bin/env python3
"""
build_retention_brief.py — VNRE Stage 08 (Retention & Referral) engine.

Deterministic scoring layer for the `vnre-retention-referral` skill. Mirrors the
daily-lead-attention pattern: an MCP/pull step dumps Follow Up Boss database
contacts (past clients + sphere) to JSON; this script merges them with the VNRE
sold-history JSON, detects outreach "moments" (equity, anniversary, move-window,
referral, re-engage), scores + dedupes them against a state file, and writes a
markdown brief with drafted outreach in DVN's voice for approval.

No network. Pure stdlib. All tuning constants live at the top.
"""
import argparse
import json
import re
from datetime import date, datetime

# ----------------------------------------------------------------- TUNING
APPRECIATION_RATE = 0.05        # KC metro est. annual appreciation
EQUITY_GAIN_THRESHOLD = 50_000  # flag an Equity Update when est. value gain >= this
EQUITY_REFRESH_DAYS = 365       # don't repeat an equity update inside this window
ANNIVERSARY_WINDOW_DAYS = 14    # +/- days around a closing anniversary to flag
MILESTONE_YEARS = {1, 3, 5, 7, 10, 15, 20}  # anniversaries worth extra weight
MOVE_WINDOW_YEARS = (7, 11)     # tenure band where move-likelihood rises
REFERRAL_DUE_DAYS = 180         # past client, no contact this long -> referral ask
REENGAGE_COI_DAYS = 365         # sphere contact gone cold this long -> re-engage
SUPPRESS_CONTACT_DAYS = 30      # never surface anyone contacted within this window
CAP = 40                        # max contacts per brief

TIER_WEIGHT = {"past_client": 3, "coi": 2, "other": 1}
MOMENT_WEIGHT = {
    "equity": 5, "anniversary": 4, "move_window": 4,
    "referral": 3, "reengage": 2,
}

# ----------------------------------------------------------------- helpers
def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def parse_date(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s[:len(fmt) + 2] if "T" in fmt else s[:10], fmt).date()
        except ValueError:
            continue
    m = re.search(r"(20\d\d)", s)  # bare year fallback (sold list)
    return date(int(m.group(1)), 6, 30) if m else None

def days_between(a, b):
    return (a - b).days if a and b else None

def tier_of(contact):
    blob = " ".join([contact.get("stage", "")] + contact.get("tags", [])).lower()
    if "past client" in blob or "pastclient" in blob or "closed" in blob:
        return "past_client"
    if "coi" in blob or "sphere" in blob or "agent coi" in blob:
        return "coi"
    return "other"

def usd(n):
    return f"${n:,.0f}"

# ----------------------------------------------------------------- merge
def merge_sold(contact, sold_index):
    """Backfill closeDate / salePrice / address from the sold-history list."""
    if contact.get("closeDate") and contact.get("salePrice"):
        return contact
    key = norm(contact.get("lastName", "")) + norm(contact.get("address", ""))
    if not norm(contact.get("address")):
        key_alt = norm(contact.get("lastName", ""))
        hit = sold_index.get(key) or sold_index.get(key_alt)
    else:
        hit = sold_index.get(key)
    if hit:
        contact.setdefault("address", hit.get("address"))
        contact.setdefault("city", hit.get("city"))
        if not contact.get("closeDate"):
            contact["closeDate"] = hit.get("closeDate") or str(hit.get("year", ""))
        if not contact.get("salePrice") and hit.get("salePrice"):
            contact["salePrice"] = hit.get("salePrice")
    return contact

def build_sold_index(sold):
    idx = {}
    for d in sold:
        name = d.get("family") or d.get("lastName") or d.get("name") or ""
        last = name.split()[-1] if name else ""
        idx[norm(last) + norm(d.get("address", ""))] = d
        idx.setdefault(norm(last), d)
    return idx

# ----------------------------------------------------------------- moments
def detect(contact, today, state):
    """Return list of (moment, weight, detail, draft) for one contact."""
    out = []
    name = (contact.get("firstName") or contact.get("name") or "there").split()[0]
    addr = contact.get("address") or "your home"
    city = contact.get("city") or ""
    where = f"{addr}{', ' + city if city else ''}"
    tier = tier_of(contact)
    close = parse_date(contact.get("closeDate"))
    last = parse_date(contact.get("lastContactDate"))
    last_days = days_between(today, last)
    price = contact.get("salePrice")
    cid = str(contact.get("id") or norm(contact.get("lastName", "")) + norm(addr))
    seen = state.get(cid, {})

    years = round((today - close).days / 365.25, 1) if close else None

    # Equity update
    if close and price and years and years >= 1:
        est_value = price * ((1 + APPRECIATION_RATE) ** years)
        gain = est_value - price
        last_equity = parse_date(seen.get("equity"))
        fresh = (not last_equity) or (days_between(today, last_equity) or 999) >= EQUITY_REFRESH_DAYS
        if gain >= EQUITY_GAIN_THRESHOLD and fresh:
            detail = f"owned ~{years}y · est. value {usd(est_value)} · est. gain {usd(gain)}"
            draft = (f"{name} — homes like yours on {addr} are up roughly {usd(gain)} since you "
                     f"bought. Want a no-pressure value update? — DVN")
            out.append(("equity", MOMENT_WEIGHT["equity"] + min(gain / 50_000, 4), detail, draft))

    # Anniversary
    if close:
        anniv = close.replace(year=today.year)
        delta = abs((anniv - today).days)
        if delta <= ANNIVERSARY_WINDOW_DAYS and years and years >= 1:
            yr = today.year - close.year
            w = MOMENT_WEIGHT["anniversary"] + (2 if yr in MILESTONE_YEARS else 0)
            detail = f"{yr}-year home anniversary ({close.isoformat()})"
            draft = (f"{name} — {yr} years in the {city or addr} house this week. Hope it still "
                     f"feels like home. Anything changing for you in the next 12 months? — DVN")
            out.append(("anniversary", w, detail, draft))

    # Move-window
    if years and MOVE_WINDOW_YEARS[0] <= years <= MOVE_WINDOW_YEARS[1]:
        detail = f"owned ~{years}y — typical move window"
        draft = (f"{name} — you're right in the window most folks start thinking about the next "
                 f"move. Want me to run what {addr} would sell for today? — DVN")
        out.append(("move_window", MOMENT_WEIGHT["move_window"], detail, draft))

    # Referral ask (past clients gone quiet)
    if tier == "past_client" and (last_days is None or last_days >= REFERRAL_DUE_DAYS):
        ld = "no contact on file" if last_days is None else f"last contact {last_days}d ago"
        detail = f"past client · {ld}"
        draft = (f"{name} — quick one: who's the next person you know making a move? I'll take "
                 f"the same care of them I took of you. — DVN")
        out.append(("referral", MOMENT_WEIGHT["referral"], detail, draft))

    # Re-engage cold sphere
    if tier == "coi" and last_days is not None and last_days >= REENGAGE_COI_DAYS:
        detail = f"sphere · cold {last_days}d"
        draft = (f"{name} — been too long. No agenda — just checking in. What's new with you? — DVN")
        out.append(("reengage", MOMENT_WEIGHT["reengage"], detail, draft))

    return out, tier, last_days, cid

# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pull", required=True)
    ap.add_argument("--sold")
    ap.add_argument("--state", default="")
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--out-json", default="")
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--cap", type=int, default=CAP)
    args = ap.parse_args()

    today = parse_date(args.today)
    contacts = json.load(open(args.pull))
    contacts = contacts.get("contacts", contacts) if isinstance(contacts, dict) else contacts
    sold = json.load(open(args.sold)) if args.sold else []
    sold = sold.get("deals", sold) if isinstance(sold, dict) else sold
    sold_index = build_sold_index(sold)
    state = {}
    if args.state:
        try:
            state = json.load(open(args.state))
        except (OSError, ValueError):
            state = {}

    rows, suppressed = [], 0
    for c in contacts:
        c = merge_sold(c, sold_index)
        moments, tier, last_days, cid = detect(c, today, state)
        if not moments:
            continue
        if last_days is not None and last_days < SUPPRESS_CONTACT_DAYS:
            suppressed += 1
            continue
        top = max(moments, key=lambda m: m[1])
        score = top[1] * TIER_WEIGHT.get(tier, 1)
        rows.append({
            "id": cid,
            "name": (c.get("firstName", "") + " " + c.get("lastName", "")).strip() or c.get("name", "?"),
            "address": c.get("address", ""), "city": c.get("city", ""),
            "tier": tier, "primary": top[0], "score": round(score, 1),
            "moments": [{"type": m[0], "detail": m[2], "draft": m[3]} for m in moments],
        })

    rows.sort(key=lambda r: r["score"], reverse=True)
    capped, tail = rows[:args.cap], max(0, len(rows) - args.cap)

    # ----- write markdown
    SECTION = [("equity", "💰 Equity Updates"), ("anniversary", "🏡 Home Anniversaries"),
               ("move_window", "📦 Move-Window Check-ins"), ("referral", "🔁 Referral Asks"),
               ("reengage", "👋 Re-engage Sphere")]
    lines = [f"# VNRE Retention & Referral Brief — {today.isoformat()}", "",
             f"Surfaced **{len(capped)}** contacts" + (f" (+{tail} in tail)" if tail else "") +
             f" · suppressed {suppressed} (contacted < {SUPPRESS_CONTACT_DAYS}d).",
             f"_Appreciation {int(APPRECIATION_RATE*100)}%/yr · equity flag ≥ {usd(EQUITY_GAIN_THRESHOLD)} "
             f"· move window {MOVE_WINDOW_YEARS[0]}–{MOVE_WINDOW_YEARS[1]}y · referral due {REFERRAL_DUE_DAYS}d._",
             "", "> Drafts are in DVN voice. Approve/edit before sending; nothing goes out automatically.", ""]
    for key, title in SECTION:
        bucket = [r for r in capped if any(m["type"] == key for m in r["moments"])]
        if not bucket:
            continue
        lines.append(f"## {title} ({len(bucket)})")
        for r in bucket:
            m = next(mm for mm in r["moments"] if mm["type"] == key)
            where = (r["address"] + (", " + r["city"] if r["city"] else "")) or "—"
            lines += [f"- **{r['name']}** — {where} · {m['detail']}", f"  > {m['draft']}"]
        lines.append("")
    md = "\n".join(lines).rstrip() + "\n"
    open(args.out_md, "w").write(md)

    if args.out_json:
        json.dump({"today": today.isoformat(), "surfaced": capped, "tail": tail,
                   "suppressed": suppressed}, open(args.out_json, "w"), indent=2)

    print(f"surfaced {len(capped)} (+{tail} tail), suppressed {suppressed} -> {args.out_md}")


if __name__ == "__main__":
    main()
