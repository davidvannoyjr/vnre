#!/usr/bin/env python3
"""
build_briefing.py — VNRE Monday Executive Briefing engine.

Deterministic layer for the `monday-briefing` skill. It does the boring,
repeatable work so Claude can spend its judgment where it counts:

  MCP pull tools  ->  _data/pull-*.json   (raw dumps, this script does NOT fetch)
  build_briefing.py  ->  filter / tag / dedup / KPI math  ->  briefing.json + skeleton.md
  Claude          ->  ranking, friction calls, Top 3, DVN voice  ->  Gmail draft

What this script owns (no network, pure stdlib):
  * Calendar: tag each event (listing / coaching / closing / prospecting / other),
    scope to the WEEK AHEAD (Mon-Sun), flag dead/unblocked weekday time.
  * Gmail: keep client / recruiting / money threads, drop newsletters + automated noise.
  * Drive: docs modified in the lookback window = movement signal (title + folder + date).
  * Granola: surface action items + anything flagged as a client issue / commitment.
  * FUB: pass through the Hot/Watch regressing-or-stalling leads from the existing
    fub_lead_attention_pull output (this script does NOT re-score leads).
  * KPI: appointment count vs the 100-day target (40 appointments) -> required pace + gap.
  * Housekeeping: delete _data/pull-*.json older than RETAIN_DAYS.

What Claude owns (the chief-of-staff pass): which opportunities rank top, what is
real friction vs noise, the Top-3 forcing-function call, and the final voice.

All tuning constants live at the top. Self-check: `python3 build_briefing.py --selftest`.
"""
import argparse
import glob
import json
import os
import re
from datetime import date, datetime, timedelta

# ----------------------------------------------------------------- TUNING
LOOKBACK_DAYS = 7                 # email / drive / granola window
RETAIN_DAYS = 14                  # delete _data/pull-*.json older than this
KPI_TARGET_APPTS = 40             # 100-day target: 40 listing appointments
KPI_WINDOW_DAYS = 100             # the campaign window the target is measured over

WORKDAY_START = 8                 # 8 AM  -> dead-time scan runs WORKDAY_START..WORKDAY_END
WORKDAY_END = 18                  # 6 PM
DEAD_BLOCK_HOURS = 3.0            # an unbooked weekday gap >= this many hours = flag it

# Event tagging — first matching category wins (order matters).
EVENT_TAGS = [
    ("listing_appt",  ["listing appt", "listing appointment", "la:", "listing presentation",
                       "list appt", "seller appt", "seller consult", "cma", "plp", "pre-listing"]),
    ("closing",       ["closing", "close ", "settlement", "transaction", "under contract",
                       "inspection", "appraisal", "walkthrough", "walk-through", "title"]),
    ("coaching",      ["coaching", "coach call", "1:1", "1-on-1", "mastermind", "agent call",
                       "dvn coaching", "client call"]),
    ("prospecting",   ["prospecting", "prospect block", "lead gen", "lead-gen", "calls block",
                       "dials", "fsbo", "expired", "circle", "power hour", "hunt"]),
]

# Gmail noise — drop a thread if the FROM or SUBJECT smells automated / bulk.
NOISE_FROM = [
    "noreply", "no-reply", "donotreply", "do-not-reply", "notifications@", "notification@",
    "mailer", "newsletter", "marketing@", "info@", "updates@", "news@", "team@", "hello@",
    "support@", "alerts@", "digest", "automated", "via ", "unsubscribe",
]
NOISE_SUBJECT = [
    "newsletter", "unsubscribe", "your receipt", "order confirmation", "shipped",
    "weekly digest", "daily digest", "webinar", "sale ends", "% off", "flash sale",
    "you have a new", "view in browser", "verify your email", "password reset",
]
# Gmail keep — money / client / recruiting signals. These override soft-noise.
MONEY_HINTS = ["invoice", "commission", "wire", "payment", "dispute", "past due", "balance",
               "refund", "escrow", "earnest", "payoff", "1099", "settlement statement", "cda"]
CLIENT_HINTS = ["offer", "contract", "closing", "inspection", "appraisal", "listing",
                "showing", "counter", "addendum", "repair", "walkthrough", "under contract",
                "your home", "our home", "the house", "buyer", "seller"]
RECRUIT_HINTS = ["coaching", "join", "recruit", "interview", "agent opportunity", "your team",
                 "brokerage", "onboard", "split", "cap ", "mentor", "considering a move"]

# Granola: lines that look like an action item or a client-issue / commitment.
ACTION_HINTS = ["action item", "todo", "to-do", "to do:", "follow up", "follow-up", "next step",
                "i'll ", "i will ", "we'll ", "send ", "draft ", "schedule ", "call ", "owe ",
                "by friday", "by monday", "deadline", "due "]
ISSUE_HINTS = ["concern", "upset", "frustrat", "unhappy", "complaint", "issue", "problem",
               "risk", "delay", "fell through", "backed out", "dispute", "angry", "worried",
               "not happy", "disappointed", "escalat", "threat"]

CATEGORY_LABEL = {
    "listing_appt": "Listing Appt",
    "closing": "Closing / Transaction",
    "coaching": "Coaching",
    "prospecting": "Prospecting Block",
    "other": "Other",
}


# ----------------------------------------------------------------- helpers
def low(s):
    return (s or "").lower()


def any_hit(text, needles):
    t = low(text)
    return any(n in t for n in needles)


def parse_dt(s):
    """Tolerant ISO / date parser. Returns datetime or None."""
    if not s:
        return None
    s = str(s).strip()
    # all-day events arrive as plain YYYY-MM-DD
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M%z",
                "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    # last-ditch: strip trailing Z / offset and microseconds
    try:
        cleaned = re.sub(r"(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$", "", s)
        return datetime.fromisoformat(cleaned)
    except ValueError:
        return None


def week_ahead_bounds(today):
    """Mon-Sun block for the briefing. On a Monday -> this week; otherwise the
    coming Monday's week, since the brief is the look-forward."""
    if today.weekday() == 0:
        start = today
    else:
        start = today + timedelta(days=(7 - today.weekday()))
    return start, start + timedelta(days=6)


def load(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def as_list(obj, *keys):
    """Pull a list out of a pull file whether it's a bare list or wrapped under a key."""
    if obj is None:
        return []
    if isinstance(obj, list):
        return obj
    if isinstance(obj, dict):
        for k in keys:
            if isinstance(obj.get(k), list):
                return obj[k]
        for v in obj.values():
            if isinstance(v, list):
                return v
    return []


# ----------------------------------------------------------------- sources
def is_template_slot(summary):
    """A reserved placeholder block, not a booked client appt (e.g. 'LA: Template')."""
    return "template" in low(summary)


def tag_event(summary, description=""):
    # Title wins: a "… | Coaching" session whose description happens to teach the
    # listing presentation is coaching, not a listing appt. Scan the title first;
    # only fall back to the description when the title alone is inconclusive.
    for cat, needles in EVENT_TAGS:
        if any_hit(summary, needles):
            return cat
    if description:
        for cat, needles in EVENT_TAGS:
            if any_hit(description, needles):
                return cat
    return "other"


def process_calendar(raw, week_start, week_end):
    """Tag week-ahead events; flag dead weekday blocks."""
    events = []
    for e in as_list(raw, "events", "items"):
        summary = e.get("summary") or e.get("title") or "(no title)"
        start_raw = e.get("start") or (e.get("start", {}) if isinstance(e.get("start"), dict) else "")
        if isinstance(e.get("start"), dict):
            start_raw = e["start"].get("dateTime") or e["start"].get("date")
        end_raw = e.get("end")
        if isinstance(end_raw, dict):
            end_raw = end_raw.get("dateTime") or end_raw.get("date")
        sdt = parse_dt(start_raw)
        edt = parse_dt(end_raw)
        if sdt is None:
            continue
        # work in naive local wall-clock — day grouping + gap math only
        if sdt.tzinfo:
            sdt = sdt.replace(tzinfo=None)
        if edt and edt.tzinfo:
            edt = edt.replace(tzinfo=None)
        if not (week_start <= sdt.date() <= week_end):
            continue
        cat = tag_event(summary, e.get("description", ""))
        template = cat == "listing_appt" and is_template_slot(summary)
        events.append({
            "summary": summary,
            "category": cat,
            "category_label": CATEGORY_LABEL[cat] + (" (open slot)" if template else ""),
            "template_slot": template,
            "start": sdt.isoformat(),
            "end": edt.isoformat() if edt else None,
            "day": sdt.strftime("%a %b %d"),
            "time": sdt.strftime("%-I:%M %p") if (sdt.hour or sdt.minute) else "All day",
            "location": e.get("location", ""),
            "attendees": e.get("attendees", []),
        })
    events.sort(key=lambda x: x["start"])

    dead = find_dead_blocks(events, week_start, week_end)
    counts = {}
    for ev in events:
        counts[ev["category"]] = counts.get(ev["category"], 0) + 1
    booked_la = sum(1 for ev in events if ev["category"] == "listing_appt" and not ev["template_slot"])
    template_la = sum(1 for ev in events if ev.get("template_slot"))
    return {"events": events, "dead_blocks": dead, "counts": counts,
            "listing_appts_week": booked_la,        # booked (named) LAs only
            "template_slots_week": template_la}      # reserved-but-empty LA slots


def find_dead_blocks(events, week_start, week_end):
    """Weekday gaps >= DEAD_BLOCK_HOURS inside the workday with nothing booked."""
    by_day = {}
    for ev in events:
        sdt = parse_dt(ev["start"])
        edt = parse_dt(ev["end"]) or (sdt + timedelta(hours=1) if sdt else None)
        if sdt is None:
            continue
        by_day.setdefault(sdt.date(), []).append((sdt, edt))
    dead = []
    d = week_start
    while d <= week_end:
        if d.weekday() < 5:  # Mon-Fri only
            day_start = datetime(d.year, d.month, d.day, WORKDAY_START)
            day_end = datetime(d.year, d.month, d.day, WORKDAY_END)
            slots = sorted(by_day.get(d, []), key=lambda x: x[0])
            cursor = day_start
            for sdt, edt in slots:
                if sdt > cursor:
                    gap = (sdt - cursor).total_seconds() / 3600.0
                    if gap >= DEAD_BLOCK_HOURS:
                        dead.append({"day": d.strftime("%a %b %d"),
                                     "from": cursor.strftime("%-I:%M %p"),
                                     "to": sdt.strftime("%-I:%M %p"),
                                     "hours": round(gap, 1)})
                if edt and edt > cursor:
                    cursor = edt
            if day_end > cursor:
                gap = (day_end - cursor).total_seconds() / 3600.0
                if gap >= DEAD_BLOCK_HOURS:
                    dead.append({"day": d.strftime("%a %b %d"),
                                 "from": cursor.strftime("%-I:%M %p"),
                                 "to": day_end.strftime("%-I:%M %p"),
                                 "hours": round(gap, 1)})
        d += timedelta(days=1)
    return dead


def classify_email(subject, sender, snippet):
    """Return a bucket (money/client/recruiting) or None to drop."""
    blob = f"{subject} {snippet}"
    if any_hit(blob, MONEY_HINTS):
        return "money"
    if any_hit(blob, RECRUIT_HINTS):
        return "recruiting"
    if any_hit(blob, CLIENT_HINTS):
        return "client"
    # not obviously relevant -> drop unless it slips noise filters and looks personal
    return None


def is_noise(subject, sender):
    return any_hit(sender, NOISE_FROM) or any_hit(subject, NOISE_SUBJECT)


def process_gmail(raw):
    kept, dropped = [], 0
    seen = set()
    for m in as_list(raw, "threads", "messages", "results"):
        subject = m.get("subject") or m.get("title") or "(no subject)"
        sender = m.get("from") or m.get("sender") or ""
        snippet = m.get("snippet") or m.get("preview") or ""
        tid = m.get("threadId") or m.get("id") or f"{subject}|{sender}"
        if tid in seen:
            continue
        seen.add(tid)
        bucket = classify_email(subject, sender, snippet)
        if bucket is None or (is_noise(subject, sender) and bucket != "money"):
            dropped += 1
            continue
        kept.append({
            "subject": subject, "from": sender, "snippet": snippet[:240],
            "bucket": bucket, "threadId": m.get("threadId") or m.get("id"),
            "date": m.get("date") or m.get("internalDate") or "",
            "unread": bool(m.get("unread", m.get("isUnread", False))),
        })
    buckets = {}
    for k in kept:
        buckets[k["bucket"]] = buckets.get(k["bucket"], 0) + 1
    return {"threads": kept, "dropped": dropped, "buckets": buckets}


def process_drive(raw, cutoff):
    out = []
    for f in as_list(raw, "files", "items"):
        name = f.get("name") or f.get("title") or "(untitled)"
        mt = parse_dt(f.get("modifiedTime") or f.get("modified") or f.get("recencyTime"))
        if mt and mt.date() < cutoff:
            continue
        folder = f.get("folder") or f.get("parentFolder") or ""
        if not folder:
            parents = f.get("parents")
            if isinstance(parents, list) and parents:
                folder = parents[0].get("name", "") if isinstance(parents[0], dict) else str(parents[0])
        out.append({
            "name": name, "folder": folder,
            "modified": mt.strftime("%a %b %d") if mt else "",
            "modified_iso": mt.isoformat() if mt else "",
            "link": f.get("webViewLink") or f.get("link") or "",
        })
    out.sort(key=lambda x: x["modified_iso"], reverse=True)
    return {"files": out}


def process_granola(raw):
    meetings = []
    for mtg in as_list(raw, "meetings", "items", "notes"):
        title = mtg.get("title") or mtg.get("name") or "(untitled meeting)"
        when = mtg.get("date") or mtg.get("created_at") or mtg.get("start") or ""
        body = mtg.get("notes") or mtg.get("summary") or mtg.get("transcript") or ""
        explicit = mtg.get("actionItems") or mtg.get("action_items") or []
        actions, issues = list(explicit), []
        # mine the body for action items / client-issue lines the source didn't tag
        for line in re.split(r"[\n\r]+", body):
            ls = line.strip(" -*•\t")
            if not ls or len(ls) < 6:
                continue
            if any_hit(ls, ISSUE_HINTS):
                issues.append(ls[:240])
            elif ls not in actions and any_hit(ls, ACTION_HINTS):
                actions.append(ls[:240])
        meetings.append({
            "title": title,
            "date": (parse_dt(when).strftime("%a %b %d") if parse_dt(when) else str(when)[:10]),
            "action_items": actions[:12], "issues": issues[:8],
        })
    return {"meetings": meetings}


def process_fub(raw):
    """Pass-through of the existing fub_lead_attention_pull output. We do NOT
    re-score. Keep only Hot/Watch leads that are regressing or stalling."""
    leads = []
    for ld in as_list(raw, "leads", "people", "results"):
        seg = low(ld.get("segment") or ld.get("tier") or ld.get("stage") or "")
        status = low(ld.get("status") or ld.get("trend") or ld.get("flag") or "")
        is_hot_watch = ("hot" in seg) or ("watch" in seg)
        is_regress = any(w in status for w in ("regress", "stall", "stalling", "cooling",
                                               "slipping", "overdue", "no contact", "at risk"))
        # also honor an explicit boolean the pull may already set
        if ld.get("regressing") or ld.get("stalling"):
            is_regress = True
        if is_hot_watch and is_regress:
            leads.append({
                "name": ld.get("name") or ld.get("fullName") or "(unknown)",
                "segment": ld.get("segment") or ld.get("tier") or ld.get("stage") or "",
                "status": ld.get("status") or ld.get("trend") or ld.get("flag") or "",
                "last_contact": ld.get("lastContact") or ld.get("last_contact") or "",
                "next_action": ld.get("nextAction") or ld.get("next_action") or "",
            })
    return {"leads": leads}


# ----------------------------------------------------------------- KPI
def kpi_block(cal, campaign_start, today, appts_to_date=None):
    """Pace toward 40 listing appts in 100 days. appts_to_date comes from FUB/manual
    when available; otherwise we report the week-ahead booked count and the required
    pace so Claude can fill the actual."""
    info = {
        "target_appts": KPI_TARGET_APPTS,
        "window_days": KPI_WINDOW_DAYS,
        "listing_appts_week_ahead": cal.get("listing_appts_week", 0),
        "appts_to_date": appts_to_date,
    }
    if campaign_start:
        cs = parse_dt(campaign_start)
        if cs:
            elapsed = max(0, (today - cs.date()).days)
            elapsed = min(elapsed, KPI_WINDOW_DAYS)
            required = round(KPI_TARGET_APPTS * (elapsed / KPI_WINDOW_DAYS), 1)
            info.update({
                "campaign_start": campaign_start,
                "days_elapsed": elapsed,
                "days_remaining": KPI_WINDOW_DAYS - elapsed,
                "required_pace_to_date": required,
            })
            if appts_to_date is not None:
                info["gap_vs_pace"] = round(appts_to_date - required, 1)
                remaining = KPI_WINDOW_DAYS - elapsed
                need = max(0, KPI_TARGET_APPTS - appts_to_date)
                info["appts_needed_per_week_remaining"] = (
                    round(need / (remaining / 7.0), 1) if remaining > 0 else need)
    return info


# ----------------------------------------------------------------- assemble
def build(args, today):
    week_start, week_end = week_ahead_bounds(today)
    cutoff = today - timedelta(days=args.lookback)

    sources = {}
    missing = []

    cal_raw = load(args.calendar)
    if cal_raw is None and args.calendar:
        missing.append("Google Calendar")
    cal = process_calendar(cal_raw, week_start, week_end)

    gm_raw = load(args.gmail)
    if gm_raw is None and args.gmail:
        missing.append("Gmail")
    gmail = process_gmail(gm_raw)

    dr_raw = load(args.drive)
    if dr_raw is None and args.drive:
        missing.append("Google Drive")
    drive = process_drive(dr_raw, cutoff)

    gr_raw = load(args.granola)
    if gr_raw is None and args.granola:
        missing.append("Granola")
    granola = process_granola(gr_raw)

    fub_raw = load(args.fub)
    if fub_raw is None and args.fub:
        missing.append("FUB (fub_lead_attention_pull)")
    fub = process_fub(fub_raw)

    appts_to_date = args.appts_to_date
    kpi = kpi_block(cal, args.campaign_start, today, appts_to_date)

    briefing = {
        "generated": today.isoformat(),
        "week_of": week_start.strftime("%b %d"),
        "week_start": week_start.isoformat(),
        "week_end": week_end.isoformat(),
        "lookback_days": args.lookback,
        "missing_sources": missing,
        "calendar": cal,
        "gmail": gmail,
        "drive": drive,
        "granola": granola,
        "fub": fub,
        "kpi": kpi,
    }
    return briefing


# ----------------------------------------------------------------- skeleton md
def skeleton_md(b):
    L = []
    L.append(f"# 🗓 Monday Briefing — Week of {b['week_of']}")
    L.append(f"*Generated {b['generated']} · deterministic skeleton — Claude does the judgment pass on top.*\n")
    if b["missing_sources"]:
        L.append("> ⚠️ **Sources unavailable this run:** " + ", ".join(b["missing_sources"]) +
                 ". Briefing built from what was reachable.\n")

    L.append("## Key Opportunities")
    L.append("_Claude ranks these. Raw signal below._")
    for f in b["fub"]["leads"]:
        L.append(f"- **{f['name']}** ({f['segment']}) — {f['status']}. "
                 f"Last contact {f['last_contact'] or 'n/a'}. {f['next_action']}".rstrip())
    for f in b["drive"]["files"][:8]:
        L.append(f"- 📄 Movement: *{f['name']}* ({f['folder'] or 'Drive'}, {f['modified']})")
    L.append("")

    L.append("## Recruiting Updates")
    rec = [t for t in b["gmail"]["threads"] if t["bucket"] == "recruiting"]
    for t in rec:
        L.append(f"- ✉️ {t['subject']} — {t['from']}")
    if not rec:
        L.append("- _No recruiting email signal in window._")
    L.append("")

    L.append("## Client Issues")
    any_issue = False
    for m in b["granola"]["meetings"]:
        for iss in m["issues"]:
            L.append(f"- ⚠️ [{m['title']}, {m['date']}] {iss}")
            any_issue = True
    for t in b["gmail"]["threads"]:
        if t["bucket"] == "client":
            L.append(f"- ✉️ {t['subject']} — {t['from']}")
            any_issue = True
    if not any_issue:
        L.append("- _No flagged client friction in window._")
    L.append("")

    L.append("## Upcoming Appointments")
    for e in b["calendar"]["events"]:
        L.append(f"- {e['day']} {e['time']} — **{e['category_label']}**: {e['summary']}"
                 + (f" @ {e['location']}" if e['location'] else ""))
    if not b["calendar"]["events"]:
        L.append("- _No events in the week ahead._")
    if b["calendar"]["dead_blocks"]:
        L.append("\n**Dead / unblocked weekday time:**")
        for d in b["calendar"]["dead_blocks"]:
            L.append(f"- {d['day']}: {d['from']}–{d['to']} ({d['hours']}h open)")
    L.append("")

    L.append("## KPI Risks")
    k = b["kpi"]
    L.append(f"- Target: **{k['target_appts']} listing appts / {k['window_days']} days**.")
    if "days_elapsed" in k:
        L.append(f"- Day {k['days_elapsed']} of {k['window_days']} "
                 f"({k['days_remaining']} left). Required pace to date: **{k['required_pace_to_date']}** appts.")
    if k.get("appts_to_date") is not None:
        L.append(f"- Booked to date: **{k['appts_to_date']}** "
                 f"(gap vs pace: {k.get('gap_vs_pace')}). "
                 f"Need ~{k.get('appts_needed_per_week_remaining')}/wk to hit target.")
    else:
        L.append("- ⚠️ Appts-to-date not supplied (FUB pull) — fill the actual to compute the gap.")
    L.append(f"- **Booked** listing appts on the calendar this coming week: **{k['listing_appts_week_ahead']}**.")
    tpl = b["calendar"].get("template_slots_week", 0)
    if tpl:
        L.append(f"- ⚠️ Plus **{tpl}** reserved `LA:` template slots with no client booked — *fill these.*")
    L.append("")

    L.append("## Top 3 Priorities for the Week")
    L.append("1. _Claude's call._\n2. _Claude's call._\n3. _Claude's call._")
    return "\n".join(L) + "\n"


# ----------------------------------------------------------------- housekeeping
def prune(data_dir, today, retain=RETAIN_DAYS):
    removed = []
    if not data_dir or not os.path.isdir(data_dir):
        return removed
    horizon = today - timedelta(days=retain)
    for path in glob.glob(os.path.join(data_dir, "pull-*.json")):
        m = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(path))
        if not m:
            continue
        try:
            fdate = datetime.strptime(m.group(1), "%Y-%m-%d").date()
        except ValueError:
            continue
        if fdate < horizon:
            try:
                os.remove(path)
                removed.append(os.path.basename(path))
            except OSError:
                pass
    return removed


# ----------------------------------------------------------------- selftest
def selftest():
    here = os.path.dirname(os.path.abspath(__file__))
    sample = os.path.join(here, "..", "sample")
    args = argparse.Namespace(
        calendar=os.path.join(sample, "pull-calendar.json"),
        gmail=os.path.join(sample, "pull-gmail.json"),
        drive=os.path.join(sample, "pull-drive.json"),
        granola=os.path.join(sample, "pull-granola.json"),
        fub=os.path.join(sample, "pull-fub.json"),
        lookback=LOOKBACK_DAYS, campaign_start="2026-05-20", appts_to_date=11,
    )
    today = date(2026, 6, 24)
    b = build(args, today)
    md = skeleton_md(b)
    assert b["calendar"]["events"], "expected week-ahead events"
    assert any(e["category"] == "listing_appt" for e in b["calendar"]["events"]), "tagging failed"
    assert b["calendar"]["template_slots_week"] == 1, "template slot not detected"
    assert b["calendar"]["listing_appts_week"] == 1, "booked LA count should exclude template slot"
    # title must win: a coaching session that only mentions listings in its description stays coaching
    coach = [e for e in b["calendar"]["events"] if "Sample 1-1" in e["summary"]][0]
    assert coach["category"] == "coaching", "title should win over description"
    assert b["fub"]["leads"], "expected stalling FUB leads to pass through"
    assert all(t["bucket"] in ("money", "client", "recruiting") for t in b["gmail"]["threads"]), "gmail filter leak"
    assert any(m["issues"] for m in b["granola"]["meetings"]), "expected a granola issue"
    assert b["kpi"]["gap_vs_pace"] is not None, "kpi gap not computed"
    assert "Top 3 Priorities" in md
    print("selftest OK")
    print(f"  week of {b['week_of']} · {len(b['calendar']['events'])} events · "
          f"{len(b['gmail']['threads'])} emails kept ({b['gmail']['dropped']} dropped) · "
          f"{len(b['fub']['leads'])} FUB leads · {len(b['drive']['files'])} drive files")
    print(f"  KPI: day {b['kpi'].get('days_elapsed')}, required {b['kpi'].get('required_pace_to_date')}, "
          f"booked {b['kpi'].get('appts_to_date')}, gap {b['kpi'].get('gap_vs_pace')}")
    return 0


# ----------------------------------------------------------------- cli
def main():
    p = argparse.ArgumentParser(description="VNRE Monday briefing engine")
    p.add_argument("--calendar"); p.add_argument("--gmail"); p.add_argument("--drive")
    p.add_argument("--granola"); p.add_argument("--fub")
    p.add_argument("--out-json"); p.add_argument("--out-md")
    p.add_argument("--data-dir", help="folder of pull-*.json for housekeeping prune")
    p.add_argument("--campaign-start", help="YYYY-MM-DD start of the 100-day window")
    p.add_argument("--appts-to-date", type=int, default=None,
                   help="listing appts booked so far (from FUB) for the KPI gap")
    p.add_argument("--lookback", type=int, default=LOOKBACK_DAYS)
    p.add_argument("--retain-days", type=int, default=RETAIN_DAYS)
    p.add_argument("--today", help="override today (YYYY-MM-DD)")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        raise SystemExit(selftest())

    today = parse_dt(args.today).date() if args.today else date.today()
    b = build(args, today)

    if args.data_dir:
        b["pruned"] = prune(args.data_dir, today, args.retain_days)

    if args.out_json:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_json)), exist_ok=True)
        with open(args.out_json, "w", encoding="utf-8") as fh:
            json.dump(b, fh, indent=2)
    md = skeleton_md(b)
    if args.out_md:
        os.makedirs(os.path.dirname(os.path.abspath(args.out_md)), exist_ok=True)
        with open(args.out_md, "w", encoding="utf-8") as fh:
            fh.write(md)
    if not args.out_json and not args.out_md:
        print(md)
    else:
        print(f"briefing: week of {b['week_of']} · {len(b['calendar']['events'])} events · "
              f"{len(b['gmail']['threads'])} emails · {len(b['fub']['leads'])} FUB leads · "
              f"{len(b['drive']['files'])} files"
              + (f" · pruned {len(b.get('pruned', []))}" if args.data_dir else "")
              + (f" · MISSING: {', '.join(b['missing_sources'])}" if b["missing_sources"] else ""))


if __name__ == "__main__":
    main()
