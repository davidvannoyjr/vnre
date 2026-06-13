#!/usr/bin/env python3
"""
build_call_list.py — VNRE Stage 01 "Active Hunter" daily targeting.

Ranks today's outbound prospecting targets across segments (FSBO, Expired, Aged Lead,
Geo-farm, COI, Past Client), attaches the right script per segment, and — critically —
filters out DNC / opt-out contacts before they ever surface. Output is a prioritized
call list; connect → hand to vnre-book-appointment, no-connect → the nurture sequence.

Pure stdlib, no network. Same scoring spirit as daily-lead-attention, tuned for hunting.
"""
import argparse
import json
import re
from datetime import date, datetime

# ----------------------------------------------------------------- TUNING
SEGMENT_WEIGHT = {                 # listing-intent segments rank highest
    "fsbo": 5, "expired": 5, "past_client": 4, "coi": 3, "aged_lead": 3, "geo_farm": 2,
}
SEGMENT_SCRIPT = {
    "fsbo": "call-scripts/FSBO.md", "expired": "call-scripts/Expired.md",
    "aged_lead": "call-scripts/Aged-Lead.md", "coi": "call-scripts/Circle-COI.md",
    "past_client": "call-scripts/Past-Client.md", "geo_farm": "call-scripts/Circle-COI.md",
}
SUPPRESS_ATTEMPT_DAYS = 2          # don't re-dial within this window
MAX_ATTEMPTS = 8                   # stop hammering a non-responder; route to nurture
CAP = 60                           # a workable daily block
DNC_TAGS = ("dnc", "do not call", "do-not-call", "opt-out", "optout", "do not contact")


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def parse_date(s):
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None

def is_dnc(c):
    blob = " ".join([c.get("stage", "")] + c.get("tags", [])).lower()
    return bool(c.get("dnc")) or any(t in blob for t in DNC_TAGS)

def segment_of(c):
    if c.get("segment"):
        return c["segment"].lower().replace(" ", "_")
    blob = " ".join([c.get("stage", "")] + c.get("tags", [])).lower()
    if "fsbo" in blob or "for sale by owner" in blob:
        return "fsbo"
    if "expired" in blob:
        return "expired"
    if "past client" in blob or "closed" in blob:
        return "past_client"
    if "coi" in blob or "sphere" in blob:
        return "coi"
    if "farm" in blob or "geo" in blob:
        return "geo_farm"
    return "aged_lead"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pull")
    ap.add_argument("--out")
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--cap", type=int, default=CAP)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (args.pull and args.out):
        ap.error("--pull and --out required (or --selftest)")

    today = parse_date(args.today)
    data = json.load(open(args.pull))
    contacts = data.get("contacts", data) if isinstance(data, dict) else data

    rows, dnc_n, recent_n, maxed_n = [], 0, 0, 0
    for c in contacts:
        if is_dnc(c):
            dnc_n += 1
            continue
        last_attempt = parse_date(c.get("lastAttemptDate"))
        days = (today - last_attempt).days if last_attempt else None
        if days is not None and days < SUPPRESS_ATTEMPT_DAYS:
            recent_n += 1
            continue
        if (c.get("attempts") or 0) >= MAX_ATTEMPTS:
            maxed_n += 1
            continue
        seg = segment_of(c)
        signal_boost = 2 if c.get("signal") else 0
        recency_boost = 2 if days is None else (1 if days >= 14 else 0)
        score = SEGMENT_WEIGHT.get(seg, 1) + signal_boost + recency_boost
        rows.append({
            "name": (c.get("firstName", "") + " " + c.get("lastName", "")).strip() or c.get("name", "?"),
            "phone": c.get("phone", ""), "address": c.get("address", ""), "city": c.get("city", ""),
            "segment": seg, "script": SEGMENT_SCRIPT.get(seg, ""), "score": score,
            "signal": c.get("signal", ""),
            "lastAttempt": f"{days}d ago" if days is not None else "never",
            "attempts": c.get("attempts") or 0,
        })

    rows.sort(key=lambda r: r["score"], reverse=True)
    capped, tail = rows[:args.cap], max(0, len(rows) - args.cap)

    SEG_TITLE = {"fsbo": "FSBO", "expired": "Expired", "past_client": "Past Client",
                 "coi": "Circle / COI", "aged_lead": "Aged Lead", "geo_farm": "Geo-farm"}
    L = [f"# VNRE Active-Hunter Call List — {today.isoformat()}", "",
         f"**{len(capped)}** to work" + (f" (+{tail} tail)" if tail else "") +
         f" · suppressed: {dnc_n} DNC/opt-out, {recent_n} dialed <{SUPPRESS_ATTEMPT_DAYS}d, {maxed_n} maxed.",
         "", "> Connect → run `vnre-book-appointment`. No-connect → log the attempt; the nurture "
         "sequence drafts the follow-up. Compliance: DNC/opt-out filtered; mind KS/MO calling hours.", ""]
    for seg in sorted(SEG_TITLE, key=lambda s: -SEGMENT_WEIGHT.get(s, 0)):
        bucket = [r for r in capped if r["segment"] == seg]
        if not bucket:
            continue
        L.append(f"## {SEG_TITLE[seg]} ({len(bucket)}) — script: `{SEGMENT_SCRIPT.get(seg, '')}`")
        for r in bucket:
            where = (r["address"] + (", " + r["city"] if r["city"] else "")) or "—"
            sig = f" · 🔔 {r['signal']}" if r["signal"] else ""
            L.append(f"- **{r['name']}** · {r['phone'] or 'no phone'} · {where} · "
                     f"last attempt {r['lastAttempt']} ({r['attempts']} tries){sig}")
        L.append("")
    open(args.out, "w").write("\n".join(L).rstrip() + "\n")
    print(f"call list: {len(capped)} to work (+{tail} tail); suppressed {dnc_n} DNC / {recent_n} recent / {maxed_n} maxed -> {args.out}")


def selftest():
    today = date(2026, 6, 13)
    contacts = [
        {"firstName": "Joe", "lastName": "FSBO", "tags": ["FSBO"], "phone": "913-555-1", "signal": "new this week"},
        {"firstName": "Ed", "lastName": "Expired", "tags": ["Expired"], "lastAttemptDate": "2026-05-01"},
        {"firstName": "No", "lastName": "Call", "tags": ["FSBO", "DNC"], "phone": "x"},        # filtered
        {"firstName": "Too", "lastName": "Soon", "tags": ["Expired"], "lastAttemptDate": "2026-06-12"},  # <2d
        {"firstName": "Pat", "lastName": "Client", "stage": "Past Client", "attempts": 1},
    ]
    import io, json as _j, tempfile, os
    pf = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False); _j.dump(contacts, pf); pf.close()
    of = tempfile.mktemp(suffix=".md")
    import sys
    sys.argv = ["x", "--pull", pf.name, "--out", of, "--today", "2026-06-13"]
    main()
    out = open(of).read()
    assert "Joe FSBO" in out and "Ed Expired" in out and "Pat Client" in out
    assert "No Call" not in out                    # DNC filtered
    assert "Too Soon" not in out                   # dialed <2d filtered
    assert "1 DNC/opt-out" in out and "1 dialed" in out
    assert out.index("FSBO (") < out.index("Past Client (")   # FSBO outranks past client
    os.unlink(pf.name); os.unlink(of)
    print("selftest OK — DNC/recent/maxed suppression, segment scoring, and ordering all correct")


if __name__ == "__main__":
    main()
