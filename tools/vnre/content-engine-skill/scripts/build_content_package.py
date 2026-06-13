#!/usr/bin/env python3
"""
build_content_package.py — VNRE Stage 02 (Attraction) content-chop engine.

One listing in → a full multichannel launch package out, in the exact structure of DVN's
hand-built social plans (building blocks → status-aware beat schedule → per-channel captions →
FUB email/SMS blast → graphics spec → approval gate). Generates the COPY + SCHEDULE + a JSON
plan; visuals are handed to the existing premarket-social vnre_social_graphic.py / Canva template.

Status-aware: coming_soon · active · price_improvement · just_sold · open_house.
Pure stdlib, no network. The skill polishes copy to DVN voice and routes scheduling.
"""
import argparse
import json
from datetime import date, datetime, timedelta

BASE_TAGS = ["#vannoyrealestate", "#kansascityrealestate", "#kcmo", "#kchomes"]

# status -> ordered beats. each: (key, label, banner, angle, hook_filter)
BEATS = {
    "coming_soon": [
        ("teaser", "Coming Soon", "COMING SOON", "anticipation", None),
        ("sneak", "Sneak Peek", "COMING SOON", "feature", "kitchen"),
        ("live_soon", "Live This Week", "COMING SOON", "countdown", None),
    ],
    "active": [
        ("just_listed", "Just Listed", "JUST LISTED", "overview", None),
        ("feature", "Spotlight: the home", "JUST LISTED", "feature", "kitchen"),
        ("value", "Spotlight: yard + value", "JUST LISTED", "value", "yard"),
        ("still", "Still Available", "STILL AVAILABLE", "scarcity", None),
        ("open_house", "Open House", "OPEN {DAY} {TIME}", "open_house", None),
    ],
    "price_improvement": [
        ("improved", "Improved Price", "NEW PRICE", "value", None),
        ("still", "Still the best value", "NEW PRICE", "scarcity", None),
    ],
    "just_sold": [
        ("sold", "Just Sold", "SOLD", "social_proof", None),
    ],
    "open_house": [
        ("oh_announce", "Open House", "OPEN {DAY} {TIME}", "open_house", None),
        ("oh_dayof", "Open House — Today", "OPEN TODAY", "open_house", None),
    ],
}
# which channels get a caption on each beat (beat index 0 = full launch)
LAUNCH_CHANNELS = ["ig_feed", "ig_story", "fb_page", "fb_group", "linkedin"]
FOLLOW_CHANNELS = ["ig_feed", "fb_page"]


def stat_line(l):
    bits = [f"{l.get('beds','?')} bd", f"{l.get('baths','?')} ba", f"{l.get('sqft','?')} sqft",
            l.get("neighborhood", ""), f"{l.get('city','')}, {l.get('state','')}"]
    return " · ".join(b for b in bits if b and "?" not in b or "bd" in b or "ba" in b or "sqft" in b)

def spec_block(l):
    parts = [f"{l.get('beds','?')} Bedrooms", f"{l.get('baths','?')} Bath",
             f"{l.get('sqft','?')} sqft"]
    if l.get("lot"):
        parts.append(f"{l['lot']} lot")
    parts.append(f"Price: {price(l)}")
    return " | ".join(parts)

def price(l):
    p = l.get("price")
    return f"${p:,}" if isinstance(p, (int, float)) else (p or "TBD")

def contact_lockup(l):
    a = l.get("agent", {})
    return " · ".join(x for x in [a.get("name", "David Van Noy"),
                      a.get("company", "Van Noy Real Estate"), a.get("phone", ""),
                      a.get("email", "")] if x)

def hashtags(l, extra=None):
    tags = list(BASE_TAGS)
    for k in ("neighborhood", "city"):
        v = l.get(k, "").replace(" ", "").replace(",", "")
        if v:
            tags.append("#" + v.lower())
    for e in (extra or []):
        tags.append("#" + e)
    seen, out = set(), []
    for t in tags:
        if t.lower() not in seen:
            seen.add(t.lower()); out.append(t)
    return " ".join(out)

def hooks_text(l, angle):
    hooks = l.get("hooks", [])
    if angle == "feature":
        hooks = [h for h in hooks if any(k in h.lower() for k in ("kitchen", "hardwood", "renovat", "updat"))] or hooks
    if angle == "value":
        hooks = [h for h in hooks if any(k in h.lower() for k in ("yard", "lot", "fenced", "tax", "school", "access"))] or hooks
    return hooks[:4]


# ----------------------------------------------------------------- captions
def opener(beat_key, angle, l):
    nbhd = l.get("neighborhood") or l.get("city", "")
    return {
        "overview": f"Just Listed | {nbhd}",
        "feature": "The work is already done.",
        "value": f"Room to spread out, for {price(l)}.",
        "scarcity": f"Still available in {nbhd}.",
        "anticipation": f"Coming soon to {nbhd} — be the first in the door.",
        "countdown": "Going live this week.",
        "social_proof": f"Just sold in {nbhd}.",
        "open_house": f"Open House | {l.get('address','')}",
    }.get(angle, f"{nbhd}")

def caption(channel, beat, l):
    key, label, banner, angle, _ = beat
    addr = l.get("address", "")
    nbhd = l.get("neighborhood") or l.get("city", "")
    cta_phone = (l.get("agent", {}) or {}).get("phone", "")
    book = "Showings by appointment" if l.get("status") != "coming_soon" else "DM to get on the first-look list"
    hk = hooks_text(l, angle)
    if channel == "ig_feed":
        body = [opener(key, angle, l), "",
                ". ".join(hk) + ("." if hk else ""), "",
                spec_block(l), "",
                f"{addr}, {l.get('city','')}. {book} — DM or call {cta_phone}.", "",
                hashtags(l, ["justlisted"] if l.get("status") == "active" else None)]
        return "\n".join(x for x in body if x is not None)
    if channel == "ig_story":
        return "\n".join([banner_text(banner, l), f"{addr} · {l.get('city','')}",
                          f"{price(l)} · {l.get('beds','?')} bd {label.lower()}",
                          f"(sticker) {book}"])
    if channel == "fb_page":
        bullets = [f"• {price(l)}", f"• {l.get('beds','?')} bd / {l.get('baths','?')} ba · {l.get('sqft','?')} sqft"]
        bullets += [f"• {h}" for h in hk]
        return "\n".join([f"{label} | {addr} | {l.get('city','')}", "",
                          f"{opener(key, angle, l)}", ""] + bullets +
                         ["", f"Listed with {contact_lockup(l)}. {book} — call or text {cta_phone}.",
                          "", hashtags(l)])
    if channel == "fb_group":
        return (f"New on the market in {nbhd} — a {l.get('beds','?')}-bed at {price(l)}. "
                f"{(hk[0] if hk else '').rstrip('.')}{'.' if hk else ''} {book} — message me or call "
                f"{cta_phone}. — {(l.get('agent',{}) or {}).get('name','David')}, Van Noy Real Estate")
    if channel == "linkedin":
        return (f"New {l.get('city','Kansas City')} listing: {price(l)} in {nbhd}. "
                f"{(hk[0] if hk else '')} {l.get('beds','?')} bd · {l.get('baths','?')} ba · "
                f"{l.get('sqft','?')} sqft. Reach out if you or a client is watching this price point. "
                f"— {contact_lockup(l)}")
    return ""

def banner_text(banner, l):
    return banner.replace("{DAY}", l.get("openHouseDay", "{DAY}")).replace("{TIME}", l.get("openHouseTime", "{TIME}"))


# ----------------------------------------------------------------- fub blast
def fub_email(l):
    a = l.get("agent", {})
    return {
        "subject": f"Just listed in {l.get('city','Kansas City')} — {l.get('beds','?')} bd, {price(l)}",
        "body": (f"{{First name}} —\n\nWe just brought {l.get('address','')} to market in "
                 f"{l.get('neighborhood') or l.get('city','')}, and I wanted you — and anyone you "
                 f"know watching this price range — to see it first.\n\n{spec_block(l)}. "
                 f"{(l.get('hooks',['']) or [''])[0]}\n\nIf you, a friend, or a client want a look, "
                 f"reply or text me.\n\n{a.get('name','David Van Noy')}\n"
                 f"{a.get('company','Van Noy Real Estate')} · {a.get('phone','')}"),
    }

def fub_sms(l):
    return (f"Hi {{First name}} — just listed in {l.get('city','KC')}: {l.get('beds','?')} bd, "
            f"{l.get('sqft','?')} sqft, {price(l)}. {(l.get('hooks',['']) or [''])[0][:60]}. "
            f"Want a look or know someone who does? Text me back. — David, VNRE")


# ----------------------------------------------------------------- schedule
def schedule(l, beats):
    launch = datetime.strptime((l.get("launchDate") or date.today().isoformat())[:10], "%Y-%m-%d").date()
    offsets = [0, 4, 7, 11, 18]
    rows = []
    for i, beat in enumerate(beats):
        d = launch + timedelta(days=offsets[min(i, len(offsets) - 1)])
        chans = LAUNCH_CHANNELS if i == 0 else FOLLOW_CHANNELS
        for j, ch in enumerate(chans):
            rows.append({"beat": beat[1], "channel": ch, "date": d.isoformat(),
                         "time_ct": ["6:30 PM", "6:35 PM", "6:45 PM", "11:30 AM", "8:00 AM"][j % 5]})
    return rows


def build(l):
    status = l.get("status", "active")
    beats = BEATS.get(status, BEATS["active"])
    pkg = {
        "listing": {"address": l.get("address"), "status": status, "price": price(l)},
        "buildingBlocks": {"statLine": stat_line(l), "specBlock": spec_block(l),
                           "contactLockup": contact_lockup(l), "hooks": l.get("hooks", [])},
        "schedule": schedule(l, beats),
        "captions": {}, "fub": {"email": fub_email(l), "sms": fub_sms(l)},
        "graphics": {
            "bannerAnatomy": "Full-bleed hero photo, VNRE logo on white chip top-center, soft "
                             "bottom gradient scrim, all-caps wide-tracked status banner bottom-left "
                             "with a single VNRE-red #C8102E hairline accent.",
            "identityLine": f"{l.get('address','').upper()} | {l.get('city','').upper()}, "
                            f"{l.get('state','')} | {price(l)}",
            "statLine": spec_block(l).replace(" | Price: " + price(l), "").upper(),
            "exports": ["1080x1080", "1080x1350", "1080x1920"],
            "tool": "premarket-social-automation/vnre_social_graphic.py (or Canva 'Coming Soon/Just Listed' template)",
        },
        "needsDvn": [
            "Approve the schedule + captions (the one approval gate).",
            "Confirm photo selection (hero + gallery order).",
            "Confirm the Canva brand template / let the graphic generator autofill the banner.",
            "Confirm the FUB smart list for the blast (saved template vs Gmail draft).",
        ] + (["Set the open-house day/time once the home is showable."] if status in ("active", "open_house") else []),
    }
    for i, beat in enumerate(beats):
        chans = LAUNCH_CHANNELS if i == 0 else FOLLOW_CHANNELS
        pkg["captions"][beat[1]] = {ch: caption(ch, beat, l) for ch in chans}
    return pkg


# ----------------------------------------------------------------- render
def render_md(pkg, l):
    bb = pkg["buildingBlocks"]
    L = [f"# Active-Listing Social Plan — {l.get('address','')}",
         f"**Status:** {pkg['listing']['status']} · {pkg['listing']['price']}",
         f"**Property:** {l.get('address','')}, {l.get('city','')} {l.get('state','')} · "
         f"{l.get('neighborhood','')}", "",
         "## Reusable building blocks", "",
         f"**Stat line**\n`{bb['statLine']}`", "",
         f"**Spec block**\n`{bb['specBlock']}`", "",
         f"**Contact lockup**\n`{bb['contactLockup']}`", "",
         "**Hooks**\n" + "\n".join(f"- {h}" for h in bb["hooks"]), "",
         "## The schedule (staggered ~10–15 min, all times Central)", "",
         "| Beat | Channel | Date | Time (CT) |", "|---|---|---|---|"]
    for r in pkg["schedule"]:
        L.append(f"| {r['beat']} | {r['channel']} | {r['date']} | {r['time_ct']} |")
    L += ["", "## Captions", ""]
    for beat, chans in pkg["captions"].items():
        L.append(f"### {beat}")
        for ch, text in chans.items():
            L += [f"**{ch}**", "", "> " + text.replace("\n", "\n> "), ""]
    L += ["## Follow Up Boss blast", "", f"**Email — Subject:** {pkg['fub']['email']['subject']}", "",
          "> " + pkg["fub"]["email"]["body"].replace("\n", "\n> "), "",
          "**SMS**", "", "> " + pkg["fub"]["sms"], "",
          "## Graphics spec", "", pkg["graphics"]["bannerAnatomy"],
          f"- Identity line: `{pkg['graphics']['identityLine']}`",
          f"- Stat line: `{pkg['graphics']['statLine']}`",
          f"- Exports: {', '.join(pkg['graphics']['exports'])}",
          f"- Tool: {pkg['graphics']['tool']}", "",
          "## Needs DVN before scheduling", ""]
    L += [f"{i+1}. {x}" for i, x in enumerate(pkg["needsDvn"])]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--listing")
    ap.add_argument("--out-md")
    ap.add_argument("--out-json")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.listing:
        ap.error("--listing required (or --selftest)")
    l = json.load(open(args.listing))
    pkg = build(l)
    if args.out_json:
        json.dump(pkg, open(args.out_json, "w"), indent=2)
    md = render_md(pkg, l)
    (open(args.out_md, "w").write(md) if args.out_md else print(md))
    print(f"content package: {len(pkg['captions'])} beats, {len(pkg['schedule'])} scheduled posts "
          f"-> {args.out_md or 'stdout'}")


def selftest():
    l = {"address": "5908 E 101st St", "city": "Kansas City", "state": "MO",
         "neighborhood": "Skyline Heights", "status": "active", "price": 165000,
         "beds": 3, "baths": 1, "sqft": 912, "lot": "0.20-acre", "launchDate": "2026-06-12",
         "hooks": ["Fully renovated, move-in ready", "Granite + stainless kitchen",
                   "Refinished hardwoods throughout", "Newer roof, HVAC & water heater",
                   "Level fully fenced backyard + shed"],
         "agent": {"name": "David Van Noy", "company": "Van Noy Real Estate",
                   "phone": "913-361-6030", "email": "info@vannoyre.com"}}
    pkg = build(l)
    assert pkg["buildingBlocks"]["specBlock"] == "3 Bedrooms | 1 Bath | 912 sqft | 0.20-acre lot | Price: $165,000"
    assert "Just Listed" in pkg["captions"]
    assert "#skylineheights" in pkg["captions"]["Just Listed"]["ig_feed"].lower()
    assert pkg["captions"]["Just Listed"]["fb_page"].startswith("Just Listed | 5908 E 101st St")
    assert "$165,000" in pkg["fub"]["sms"] and "VNRE" in pkg["fub"]["sms"]
    assert any(r["channel"] == "linkedin" for r in pkg["schedule"])      # launch beat = all channels
    # coming_soon flips the CTA to interest-capture
    cs = build({**l, "status": "coming_soon"})
    assert "first-look" in cs["captions"]["Coming Soon"]["ig_feed"]
    md = render_md(pkg, l)
    assert "## The schedule" in md and "Needs DVN" in md
    print("selftest OK — building blocks, status-aware beats/captions, FUB blast, schedule, render all correct")


if __name__ == "__main__":
    main()
