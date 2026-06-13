#!/usr/bin/env python3
"""
build_delivery.py — stage the retention brief into ready-to-send actions.

Turns the retention brief JSON (build_retention_brief.py --out-json) from a list of
touches into a DELIVERY PLAN the skill can execute against the connected MCPs:
  - Gmail draft (create_draft) per emailable contact, in DVN's voice
  - Canva one-pager spec for every Equity Update (generate-design)
  - a manual queue (text/call) for text-preferred or no-email contacts

Approval-gated by design: this only *plans*. The skill creates drafts/designs from
the plan; nothing sends automatically. Pure stdlib, no network.
"""
import argparse
import json
import html

SUBJECTS = {
    "active_move": "Saw you were looking — {city}",
    "equity": "Your home equity update — {address}",
    "anniversary": "{years_word} years in the {city} house",
    "move_window": "Quick question about {address}",
    "refi": "You may be overpaying on your rate",
    "birthday": "Happy birthday, {first}",
    "referral": "A quick favor, {first}",
    "reengage": "Been too long, {first}",
}


def subject_for(mtype, row, moment):
    first = (row.get("name") or "there").split()[0]
    years = "".join(ch for ch in moment.get("detail", "") if ch.isdigit())[:2] or "a few"
    return SUBJECTS.get(mtype, "A quick note, {first}").format(
        city=row.get("city") or "your area", address=row.get("address") or "your home",
        first=first, years_word=years)


def html_body(draft):
    return f"<p>{html.escape(draft).replace(chr(10), '<br>')}</p>"


def build(brief):
    rows = brief.get("surfaced", brief if isinstance(brief, list) else [])
    plan = {"gmailDrafts": [], "canvaOnePagers": [], "manualQueue": []}
    for r in rows:
        prim = r.get("primary")
        moment = next((m for m in r.get("moments", []) if m["type"] == prim), None)
        if not moment:
            continue
        draft, email = moment["draft"], r.get("email")
        channel = (r.get("channel") or "").lower()

        if prim == "equity":
            plan["canvaOnePagers"].append({
                "name": r["name"],
                "query": (f"One-page Home Equity Update for {r['name']}, {r.get('address','')} "
                          f"{r.get('city','')}. {moment['detail']}. Van Noy Real Estate branding, "
                          f"charcoal + red #C8102E accent, clean, client-facing. Headline 'Your Home "
                          f"Equity Update', the estimated value and gain as big stats, a soft "
                          f"'curious what it's worth today?' CTA."),
                "design_type": "flyer",
            })

        if email and channel != "text":
            plan["gmailDrafts"].append({
                "to": email, "name": r["name"],
                "subject": subject_for(prim, r, moment),
                "htmlBody": html_body(draft), "moment": prim,
            })
        else:
            plan["manualQueue"].append({
                "name": r["name"], "via": channel or ("text" if not email else "email"),
                "moment": prim, "message": draft,
            })
    return plan


def render_md(plan, today):
    L = [f"# Retention Delivery Plan — {today}", "",
         f"{len(plan['gmailDrafts'])} Gmail drafts · {len(plan['canvaOnePagers'])} Canva "
         f"equity one-pagers · {len(plan['manualQueue'])} manual (text/call).",
         "", "> The skill creates these against Gmail / Canva on approval. Nothing sends automatically.", ""]
    if plan["gmailDrafts"]:
        L += ["## 📧 Gmail drafts"]
        for d in plan["gmailDrafts"]:
            L.append(f"- **{d['name']}** ({d['moment']}) → {d['to']} · subj: _{d['subject']}_")
        L.append("")
    if plan["canvaOnePagers"]:
        L += ["## 🎨 Canva equity one-pagers"]
        for c in plan["canvaOnePagers"]:
            L.append(f"- **{c['name']}** — generate-design ({c['design_type']})")
        L.append("")
    if plan["manualQueue"]:
        L += ["## 📞 Manual (text / call — connector can't send)"]
        for m in plan["manualQueue"]:
            L.append(f"- **{m['name']}** via {m['via']} ({m['moment']}): {m['message']}")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp")
    ap.add_argument("--out-json")
    ap.add_argument("--out-md")
    ap.add_argument("--today", default="")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.inp:
        ap.error("--in required (or --selftest)")
    brief = json.load(open(args.inp))
    plan = build(brief)
    if args.out_json:
        json.dump(plan, open(args.out_json, "w"), indent=2)
    md = render_md(plan, args.today or brief.get("today", ""))
    (open(args.out_md, "w").write(md) if args.out_md else print(md))
    print(f"delivery plan: {len(plan['gmailDrafts'])} drafts, {len(plan['canvaOnePagers'])} "
          f"one-pagers, {len(plan['manualQueue'])} manual")


def selftest():
    brief = {"today": "2026-06-13", "surfaced": [
        {"name": "Andrew Edwards", "address": "16408 Riggs Rd", "city": "Stilwell",
         "email": "a@x.com", "channel": "text", "primary": "equity",
         "moments": [{"type": "equity", "detail": "est. gain $110,000",
                      "draft": "Andrew — homes like yours are up ~$110k. Want a value update? — DVN"}]},
        {"name": "Sarah Kim", "address": "123 Oak St", "city": "OP", "email": "s@x.com",
         "channel": "email", "primary": "referral",
         "moments": [{"type": "referral", "detail": "past client",
                      "draft": "Sarah — who's the next person making a move? — DVN"}]},
    ]}
    plan = build(brief)
    # equity → canva one-pager always; Andrew is text-preferred → manual, not gmail
    assert len(plan["canvaOnePagers"]) == 1 and plan["canvaOnePagers"][0]["name"] == "Andrew Edwards"
    assert any(m["name"] == "Andrew Edwards" for m in plan["manualQueue"])
    assert not any(d["name"] == "Andrew Edwards" for d in plan["gmailDrafts"])
    # Sarah emailable → gmail draft with a referral subject
    g = next(d for d in plan["gmailDrafts"] if d["name"] == "Sarah Kim")
    assert g["to"] == "s@x.com" and "favor" in g["subject"].lower()
    assert "&mdash" not in g["htmlBody"] and "<p>" in g["htmlBody"]
    print("selftest OK — equity→Canva, text-pref→manual, emailable→Gmail draft with subject")


if __name__ == "__main__":
    main()
