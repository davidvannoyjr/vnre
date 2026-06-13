#!/usr/bin/env python3
"""
build_coi_brief.py — VNRE Stage 08 (Database & COI Management + Customer Care) engine.

Deterministic scoring layer for the `vnre-database-coi` skill. Consumes the
JSON produced by fub_pull.py (Follow Up Boss past clients + sphere, joined with
deals, communications, and property-view events), merges with the VNRE sold-history
JSON, detects outreach "moments," scores + dedupes against a state file, and writes
a markdown brief with drafted outreach in DVN's voice for approval.

Built for Van Noy Real Estate. No network, pure stdlib. All tuning at the top.

Moments detected
  🔥 active-move   property-view / website activity inside the window  (hottest)
  💰 equity        est. value gain since purchase >= threshold
  🏡 anniversary   within N days of a closing anniversary
  📦 move-window   owned inside the typical-move tenure band
  💵 refi          mortgage rate sits above market (lender-MSA + value touch)
  🎂 birthday      birthday inside the window
  🔁 referral      past client, no contact in N days
  👋 reengage      sphere contact gone cold

Score = moment weight  ×  tier weight (past client > coi)  ×  CLV boost.
"""
import argparse
import json
import re
from datetime import date, datetime

# ----------------------------------------------------------------- TUNING
APPRECIATION_RATE = 0.05          # KC-metro est. annual appreciation (set to your number)
EQUITY_GAIN_THRESHOLD = 50_000    # flag Equity Update when est. value gain >= this
EQUITY_REFRESH_DAYS = 365         # don't repeat an equity touch inside this window
ANNIVERSARY_WINDOW_DAYS = 14      # +/- days around a closing anniversary
MILESTONE_YEARS = {1, 3, 5, 7, 10, 15, 20}
MOVE_WINDOW_YEARS = (7, 11)       # tenure band where move-likelihood rises
PROPERTY_VIEW_DAYS = 45           # FUB property-view this recent = active move signal
REFI_MARKET_RATE = 6.5            # current 30-yr market rate (update periodically)
REFI_DELTA = 0.75                 # flag refi when their rate >= market + this
BIRTHDAY_WINDOW_DAYS = 10
REFERRAL_DUE_DAYS = 180           # past client, no contact this long -> referral ask
REENGAGE_COI_DAYS = 365           # sphere gone cold this long -> re-engage
SUPPRESS_CONTACT_DAYS = 30        # never surface anyone contacted within this window
CLV_BOOST_DIVISOR = 50_000        # lifetimeValue / this, capped, added to score multiplier
CLV_BOOST_CAP = 2.0
CAP = 50

TIER_WEIGHT = {"past_client": 3, "coi": 2, "other": 1}
MOMENT_WEIGHT = {
    "active_move": 7, "equity": 5, "anniversary": 4, "move_window": 4,
    "refi": 3, "birthday": 3, "referral": 3, "reengage": 2,
}
LANES = [
    ("🤝 Customer Care", [
        ("anniversary", "🏡 Home Anniversaries"),
        ("birthday", "🎂 Birthdays"),
    ]),
    ("📇 Opportunity & Database Management", [
        ("active_move", "🔥 Active Move Signals"),
        ("equity", "💰 Equity Updates"),
        ("move_window", "📦 Move-Window Check-ins"),
        ("refi", "💵 Rate / Refi Touches"),
        ("referral", "🔁 Referral Asks"),
        ("reengage", "👋 Re-engage Cold Contacts"),
    ]),
]

# ----------------------------------------------------------------- helpers
def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def parse_date(s):
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s[:10] if fmt.startswith("%Y-%m-%d") and "T" not in fmt else s, fmt).date()
        except ValueError:
            continue
    m = re.search(r"(20\d\d)", s)            # bare-year fallback (sold list)
    return date(int(m.group(1)), 6, 30) if m else None

def parse_md(s):
    """Birthday as full date or MM/DD or MM-DD -> (month, day)."""
    if not s:
        return None
    d = parse_date(s)
    if d:
        return (d.month, d.day)
    m = re.match(r"\s*(\d{1,2})[/-](\d{1,2})\s*$", str(s))
    return (int(m.group(1)), int(m.group(2))) if m else None

def days_between(a, b):
    return (a - b).days if a and b else None

def tier_of(contact):
    blob = " ".join([contact.get("stage", "")] + contact.get("tags", [])).lower()
    if any(k in blob for k in ("past client", "pastclient", "closed", "sold")):
        return "past_client"
    if any(k in blob for k in ("coi", "sphere", "center of influence")):
        return "coi"
    return "other"

def usd(n):
    return f"${n:,.0f}"

# ----------------------------------------------------------------- sold-list merge
def build_sold_index(sold):
    idx = {}
    for d in sold:
        name = d.get("family") or d.get("lastName") or d.get("name") or ""
        last = name.split()[-1] if name else d.get("lastName", "")
        idx[norm(last) + norm(d.get("address", ""))] = d
        idx.setdefault(norm(last), d)
    return idx

def merge_sold(contact, sold_index):
    if contact.get("closeDate") and contact.get("salePrice"):
        return contact
    hit = sold_index.get(norm(contact.get("lastName", "")) + norm(contact.get("address", ""))) \
        or sold_index.get(norm(contact.get("lastName", "")))
    if hit:
        contact.setdefault("address", hit.get("address"))
        contact.setdefault("city", hit.get("city"))
        if not contact.get("closeDate"):
            contact["closeDate"] = hit.get("closeDate") or str(hit.get("year", ""))
        if not contact.get("salePrice") and hit.get("salePrice"):
            contact["salePrice"] = hit.get("salePrice")
    return contact

# ----------------------------------------------------------------- moment detection
def detect(contact, today, state):
    out = []
    name = (contact.get("firstName") or contact.get("name") or "there").split()[0]
    addr = contact.get("address") or "your home"
    city = contact.get("city") or ""
    tier = tier_of(contact)
    close = parse_date(contact.get("closeDate"))
    last = parse_date(contact.get("lastContactDate"))
    last_days = days_between(today, last)
    price = contact.get("salePrice")
    cid = str(contact.get("id") or norm(contact.get("lastName", "")) + norm(addr))
    seen = state.get(cid, {})
    years = round((today - close).days / 365.25, 1) if close else None

    # 🔥 active move — property view / website activity
    pv = parse_date(contact.get("recentPropertyViewDate"))
    if pv and (days_between(today, pv) or 999) <= PROPERTY_VIEW_DAYS:
        d = days_between(today, pv)
        out.append(("active_move", MOMENT_WEIGHT["active_move"],
                    f"viewed listings {d}d ago" + (f" · owned ~{years}y" if years else ""),
                    f"{name} — noticed you've been browsing homes. Want a private, no-spam list that "
                    f"fits what you're after — and what {addr} would sell for right now? — DVN"))

    # 💰 equity
    if close and price and years and years >= 1:
        est = price * ((1 + APPRECIATION_RATE) ** years)
        gain = est - price
        le = parse_date(seen.get("equity"))
        fresh = (not le) or (days_between(today, le) or 999) >= EQUITY_REFRESH_DAYS
        if gain >= EQUITY_GAIN_THRESHOLD and fresh:
            out.append(("equity", MOMENT_WEIGHT["equity"] + min(gain / 50_000, 4),
                        f"owned ~{years}y · est. value {usd(est)} · est. gain {usd(gain)}",
                        f"{name} — homes like yours near {addr} are up roughly {usd(gain)} since you "
                        f"bought. Want a no-pressure value update? — DVN"))

    # 🏡 anniversary
    if close and years and years >= 1:
        anniv = close.replace(year=today.year)
        if abs((anniv - today).days) <= ANNIVERSARY_WINDOW_DAYS:
            yr = today.year - close.year
            out.append(("anniversary", MOMENT_WEIGHT["anniversary"] + (2 if yr in MILESTONE_YEARS else 0),
                        f"{yr}-year home anniversary ({close.isoformat()})",
                        f"{name} — {yr} years in the {city or addr} house this week. Hope it still feels "
                        f"like home. Anything changing for you in the next 12 months? — DVN"))

    # 📦 move-window
    if years and MOVE_WINDOW_YEARS[0] <= years <= MOVE_WINDOW_YEARS[1]:
        out.append(("move_window", MOMENT_WEIGHT["move_window"], f"owned ~{years}y — typical move window",
                    f"{name} — you're right in the window most folks start thinking about the next move. "
                    f"Want me to run what {addr} would sell for today? — DVN"))

    # 💵 refi (their rate above market -> lender MSA + value touch)
    rate = contact.get("mortgageRate")
    if isinstance(rate, (int, float)) and rate >= REFI_MARKET_RATE + REFI_DELTA:
        out.append(("refi", MOMENT_WEIGHT["refi"], f"locked at {rate}% vs ~{REFI_MARKET_RATE}% market",
                    f"{name} — you're at {rate}%. Rates have come off that; my lender partner can run a "
                    f"refi number — could be real monthly savings. Want the intro? — DVN"))

    # 🎂 birthday
    bd = parse_md(contact.get("birthday"))
    if bd:
        try:
            this_year = date(today.year, bd[0], bd[1])
            if abs((this_year - today).days) <= BIRTHDAY_WINDOW_DAYS:
                out.append(("birthday", MOMENT_WEIGHT["birthday"], "birthday this week",
                            f"{name} — happy birthday. No pitch — just glad to know you. — DVN"))
        except ValueError:
            pass

    # 🔁 referral
    if tier == "past_client" and (last_days is None or last_days >= REFERRAL_DUE_DAYS):
        ld = "no contact on file" if last_days is None else f"last contact {last_days}d ago"
        out.append(("referral", MOMENT_WEIGHT["referral"], f"past client · {ld}",
                    f"{name} — quick one: who's the next person you know making a move? I'll take the same "
                    f"care of them I took of you. — DVN"))

    # 👋 re-engage sphere
    if tier == "coi" and last_days is not None and last_days >= REENGAGE_COI_DAYS:
        out.append(("reengage", MOMENT_WEIGHT["reengage"], f"sphere · cold {last_days}d",
                    f"{name} — been too long. No agenda, just checking in. What's new with you? — DVN"))

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
    try:
        state = json.load(open(args.state)) if args.state else {}
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
        clv = c.get("lifetimeValue") or 0
        clv_mult = 1 + min(clv / CLV_BOOST_DIVISOR, CLV_BOOST_CAP)
        rows.append({
            "id": cid,
            "name": (c.get("firstName", "") + " " + c.get("lastName", "")).strip() or c.get("name", "?"),
            "address": c.get("address", ""), "city": c.get("city", ""),
            "email": c.get("email", ""), "channel": c.get("preferredChannel", ""), "clv": clv, "tier": tier,
            "primary": top[0], "score": round(top[1] * TIER_WEIGHT.get(tier, 1) * clv_mult, 1),
            "moments": [{"type": m[0], "detail": m[2], "draft": m[3]} for m in moments],
        })

    rows.sort(key=lambda r: r["score"], reverse=True)
    capped, tail = rows[:args.cap], max(0, len(rows) - args.cap)

    lines = [f"# VNRE Database & COI Brief — Care & Opportunity — {today.isoformat()}", "",
             f"Surfaced **{len(capped)}** contacts" + (f" (+{tail} in tail)" if tail else "") +
             f" · suppressed {suppressed} (contacted < {SUPPRESS_CONTACT_DAYS}d).",
             f"_Appreciation {int(APPRECIATION_RATE*100)}%/yr · equity ≥ {usd(EQUITY_GAIN_THRESHOLD)} · "
             f"move {MOVE_WINDOW_YEARS[0]}–{MOVE_WINDOW_YEARS[1]}y · property-view {PROPERTY_VIEW_DAYS}d · "
             f"refi ≥ {REFI_MARKET_RATE + REFI_DELTA}% · referral {REFERRAL_DUE_DAYS}d._", "",
             "> **Customer Care** = relationship touches, no ask. **Opportunity & Database "
             "Management** = surfaced opportunities + hygiene. Drafts are in DVN voice; nothing "
             "goes out automatically.", ""]
    for lane, sections in LANES:
        if not any(any(mm["type"] == k for r in capped for mm in r["moments"]) for k, _ in sections):
            continue
        lines.append(f"## {lane}")
        for key, title in sections:
            bucket = [r for r in capped if any(m["type"] == key for m in r["moments"])]
            if not bucket:
                continue
            lines.append(f"### {title} ({len(bucket)})")
            for r in bucket:
                m = next(mm for mm in r["moments"] if mm["type"] == key)
                where = (r["address"] + (", " + r["city"] if r["city"] else "")) or "—"
                extra = []
                if r["channel"]:
                    extra.append(f"prefers {r['channel']}")
                if r["clv"]:
                    extra.append(f"CLV {usd(r['clv'])}")
                tag = (" · " + " · ".join(extra)) if extra else ""
                lines += [f"- **{r['name']}** — {where} · {m['detail']}{tag}", f"  > {m['draft']}"]
            lines.append("")
    open(args.out_md, "w").write("\n".join(lines).rstrip() + "\n")

    if args.out_json:
        json.dump({"today": today.isoformat(), "surfaced": capped, "tail": tail,
                   "suppressed": suppressed}, open(args.out_json, "w"), indent=2)
    print(f"surfaced {len(capped)} (+{tail} tail), suppressed {suppressed} -> {args.out_md}")


if __name__ == "__main__":
    main()
