#!/usr/bin/env python3
"""
coach_call.py — VNRE Stage 09 AI call-coach (self mode).

Scores one prospecting/listing call transcript (from Granola) against the script rubric
for that call type: did each phase happen (opener → discovery → value → close), which
objections came up and were they handled, plus talk-ratio and questions-asked metrics.
Output is a private self-coaching report — what landed, what to fix, and 2 drills.

Deterministic rubric scoring; the skill layers qualitative judgment on top. The report
`mode` (self | client | agent) only changes framing — the engine is the same. No network.
"""
import argparse
import json
import re
from datetime import date

AGENT_LABELS = {"me", "agent", "dvn", "david", "david van noy", "van noy"}


def norm(s):
    return (s or "").strip().lower()


def parse_transcript(raw, agent_name):
    """Accept JSON [{speaker,text}] or plain text 'Speaker: line'. Return turns + agent flag."""
    turns = []
    if isinstance(raw, list):
        turns = [{"speaker": t.get("speaker", ""), "text": t.get("text", "")} for t in raw]
    else:
        for line in str(raw).splitlines():
            m = re.match(r"\s*([^:]{1,40}?):\s*(.*)", line)
            if m:
                turns.append({"speaker": m.group(1), "text": m.group(2)})
            elif turns:
                turns[-1]["text"] += " " + line.strip()
    labels = AGENT_LABELS | ({norm(agent_name)} if agent_name else set())
    for t in turns:
        sp = norm(t["speaker"])
        t["agent"] = any(lbl in sp or sp in lbl for lbl in labels if lbl)
    return turns


def hit(patterns, text):
    return any(re.search(p, text, re.I) for p in patterns)


def score(rubric, ctype, turns):
    spec = rubric["types"][ctype]
    agent_text = " ".join(t["text"] for t in turns if t["agent"])
    all_words = sum(len(t["text"].split()) for t in turns) or 1
    agent_words = sum(len(t["text"].split()) for t in turns if t["agent"])

    hits, misses, phases = [], [], {}
    total_w = done_w = 0
    for cp in spec["checkpoints"]:
        w = cp.get("weight", 1)
        total_w += w
        ph = phases.setdefault(cp["phase"], [0, 0])
        ph[1] += 1
        if hit(cp["patterns"], agent_text):
            hits.append(cp["name"]); done_w += w; ph[0] += 1
        else:
            misses.append({"name": cp["name"], "coach": cp.get("coach", ""), "phase": cp["phase"], "w": w})

    # objections: raised by prospect, handled if any agent turn follows it
    objections = []
    for i, t in enumerate(turns):
        if t["agent"]:
            continue
        for ob in spec.get("objections", []):
            if hit(ob["patterns"], t["text"]):
                handled = any(tt["agent"] for tt in turns[i + 1:i + 3])
                objections.append({"name": ob["name"], "handled": handled})

    questions = sum(1 for t in turns if t["agent"] for s in re.split(r"[.!?]", t["text"]) if s.strip().endswith("")
                    and "?" in t["text"]) or sum(t["text"].count("?") for t in turns if t["agent"])
    return {
        "type": ctype, "label": spec.get("label", ctype),
        "score": round(done_w / total_w * 100),
        "phases": phases, "hits": hits,
        "misses": sorted(misses, key=lambda m: -m["w"]),
        "objections": objections,
        "questions": questions,
        "talkRatio": round(agent_words / all_words, 2),
    }


def render(r, ctx, rubric, today, mode):
    who = {"self": "Self-coaching", "client": f"Coaching review — {ctx.get('contact','client')}",
           "agent": f"Agent ramp — {ctx.get('contact','agent')}"}.get(mode, "Self-coaching")
    flags = rubric.get("metrics", {})
    L = [f"# Call Coach ({who}) — {r['label']}  ·  {today.isoformat()}",
         f"Outcome: **{ctx.get('outcome','—')}**" + (f" · {ctx.get('contact')}" if ctx.get("contact") else ""), "",
         f"## Adherence: {r['score']}%", "",
         "| Phase | Hit |", "|---|---|"]
    for ph in ("opener", "discovery", "value", "objection", "close"):
        if ph in r["phases"]:
            L.append(f"| {ph} | {r['phases'][ph][0]}/{r['phases'][ph][1]} |")
    L.append("")
    if r["hits"]:
        L += ["## ✅ What landed", ""] + [f"- {h}" for h in r["hits"]] + [""]
    if r["misses"]:
        L += ["## 🎯 Fix next time", ""] + [f"- **{m['name']}** ({m['phase']}) — {m['coach']}" for m in r["misses"]] + [""]
    if r["objections"]:
        L += ["## Objections", ""]
        for o in r["objections"]:
            L.append(f"- {o['name']}: raised · {'✅ handled' if o['handled'] else '⚠️ not addressed'}")
        L.append("")
    L += ["## Metrics", ""]
    q_flag = " 🟡 ask more" if r["questions"] < flags.get("minQuestions", 4) else ""
    t_flag = " 🟡 talk less, listen more" if r["talkRatio"] > flags.get("talkRatioFlag", 0.6) else ""
    L += [f"- Questions you asked: **{r['questions']}**{q_flag}",
          f"- Your talk ratio: **{int(r['talkRatio']*100)}%**{t_flag}", ""]
    # drills: top miss + the weakest metric
    drills = []
    if r["misses"]:
        top = r["misses"][0]
        drills.append(f"Rehearse the {top['phase']}: {top['coach']}")
    if r["talkRatio"] > flags.get("talkRatioFlag", 0.6):
        drills.append("Run the next call asking 2 questions before making any pitch.")
    elif r["questions"] < flags.get("minQuestions", 4):
        drills.append("Add discovery questions: why, where, and by when — before value.")
    L += ["## Drills (next call)", ""] + [f"{i+1}. {d}" for i, d in enumerate(drills[:2])]
    return "\n".join(L).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--transcript")
    ap.add_argument("--rubric")
    ap.add_argument("--type", help="fsbo | expired | aged_lead | listing_appt")
    ap.add_argument("--context")
    ap.add_argument("--mode", default="self", choices=["self", "client", "agent"])
    ap.add_argument("--out")
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (args.transcript and args.rubric and args.type):
        ap.error("--transcript, --rubric and --type required (or --selftest)")
    try:
        raw = json.load(open(args.transcript))
    except (ValueError, json.JSONDecodeError):
        raw = open(args.transcript).read()
    rubric = json.load(open(args.rubric))
    ctx = json.load(open(args.context)) if args.context else {}
    turns = parse_transcript(raw, ctx.get("agent", "David"))
    r = score(rubric, args.type, turns)
    md = render(r, ctx, rubric, date.fromisoformat(args.today), args.mode)
    (open(args.out, "w").write(md) if args.out else print(md))
    print(f"coached {args.type}: adherence {r['score']}%, talk {int(r['talkRatio']*100)}%, "
          f"{len(r['misses'])} to fix -> {args.out or 'stdout'}")


def selftest():
    rubric = {"types": {"fsbo": {"label": "FSBO", "checkpoints": [
        {"phase": "opener", "name": "Name + brokerage", "patterns": ["van noy", "david"], "weight": 1, "coach": "Open with name + VNRE."},
        {"phase": "discovery", "name": "Reason + timeline", "patterns": ["why.*sell", "timeline", "how soon"], "weight": 1, "coach": "Ask why + when."},
        {"phase": "value", "name": "Net / USP", "patterns": ["net", "commission", "2%", "guarantee"], "weight": 2, "coach": "Show net + a USP."},
        {"phase": "close", "name": "Asked for appointment", "patterns": ["20 min", "appointment", "tuesday", "what.*works"], "weight": 2, "coach": "Ask for a 20-min appt with a day/time."}],
        "objections": [{"name": "Commission", "patterns": ["pay.*commission", "not paying"]}]}},
        "metrics": {"talkRatioFlag": 0.6, "minQuestions": 3}}
    transcript = [
        {"speaker": "David", "text": "Hi, this is David Van Noy with Van Noy Real Estate. Why are you selling, and what's your timeline?"},
        {"speaker": "Seller", "text": "Moving for work. But I don't want to pay commission."},
        {"speaker": "David", "text": "Fair. Let me show you net-to-net — FSBO vs listed, and we have a 2% option."},
        {"speaker": "Seller", "text": "Maybe. Send me some info."},
        {"speaker": "David", "text": "Will do."},
    ]
    turns = parse_transcript(transcript, "David")
    r = score(rubric, "fsbo", turns)
    assert "Name + brokerage" in r["hits"] and "Net / USP" in r["hits"]
    assert any(m["name"] == "Asked for appointment" for m in r["misses"])   # never asked → close missed
    assert r["objections"] and r["objections"][0]["name"] == "Commission" and r["objections"][0]["handled"]
    # opener+discovery(1)+value(2)=4 of 6 weighted -> 67%
    assert r["score"] == 67, r["score"]
    out = render(r, {"outcome": "callback"}, rubric, date(2026, 6, 13), "self")
    assert "Fix next time" in out and "Asked for appointment" in out and "Drills" in out
    print("selftest OK — phase scoring, missed close, objection-handled detection, drills all correct")


if __name__ == "__main__":
    main()
