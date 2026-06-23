#!/usr/bin/env python3
"""Board of Advisors — deterministic consultation assembler.

Takes a filled advisor registry + a decision file and assembles the structured
consultation: a per-advisor section (each in that advisor's lens), the
agreement/conflict matrix, and the synthesis scaffold ending in one recommended
call. Deterministic and offline — no network in the assembly layer. The model
fills each advisor's read using only that advisor's sourced profile.

Usage:
  python3 consult_board.py --advisors advisors.json --decision decision.md \
      --out "<home>/<today> <Decision> - Board Consultation.md"
  python3 consult_board.py --selftest

Design rules (suite-wide): deterministic, offline --selftest, tunable constants
at the top, approval-gated (writes a file, sends nothing).
"""

import argparse
import json
import sys
from datetime import date

# ---- Tunable constants -----------------------------------------------------
MIN_ADVISORS = 1            # selftest floor; live board should be 3-7
MAX_ADVISORS = 7            # synthesis turns to mush past this
DEFAULT_WEIGHT = 1.0
REQUIRED_FIELDS = ["name", "decision_lens", "sources"]  # a profile is invalid without these
# ---------------------------------------------------------------------------


def load_advisors(path):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    advisors = data.get("advisors", [])
    return data, advisors


def validate(advisors):
    """Return (clean, warnings). Drops profiles missing required/real sources."""
    clean, warnings = [], []
    if len(advisors) > MAX_ADVISORS:
        warnings.append(
            f"{len(advisors)} advisors — over the cap of {MAX_ADVISORS}; synthesis quality drops."
        )
    for a in advisors:
        name = a.get("name", "<unnamed>")
        missing = [f for f in REQUIRED_FIELDS if not a.get(f)]
        if missing:
            warnings.append(f"Dropped '{name}': missing {', '.join(missing)}.")
            continue
        sources = a.get("sources") or []
        if any(str(s).strip().startswith("<") for s in sources) or any(
            str(v).strip().startswith("<") for v in [a.get("decision_lens", "")]
        ):
            warnings.append(f"Dropped '{name}': profile still has unfilled <placeholder> fields.")
            continue
        clean.append(a)
    return clean, warnings


def read_decision(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read().strip()


def advisor_section(a):
    lens = a.get("decision_lens", "")
    heur = a.get("heuristics", []) or []
    flags = a.get("will_flag", []) or []
    moves = a.get("signature_moves", []) or []
    voice = a.get("voice", "")
    src = a.get("sources", []) or []
    lines = [f"### {a['name']} — {a.get('domain', '')}".rstrip(" —")]
    if voice:
        lines.append(f"*Voice: {voice}*")
    lines.append("")
    lines.append(f"**Lens:** {lens}")
    if heur:
        lines.append("**Reads it through:** " + "; ".join(heur))
    if moves:
        lines.append("**Would likely:** " + "; ".join(moves))
    if flags:
        lines.append("**Flags:** " + "; ".join(flags))
    lines.append("")
    lines.append("**Their read on this decision:**")
    lines.append("> _Fill in this advisor's actual take, written in their voice and"
                 " grounded only in their sourced thinking. If it doesn't sound like"
                 " them, the profile is thin — fix the registry, not this line._")
    if src:
        lines.append("")
        lines.append("_Built from: " + "; ".join(str(s) for s in src) + "._")
    return "\n".join(lines)


def build_report(meta, advisors, decision_text, today):
    board = meta.get("board_name", "Board of Advisors")
    out = []
    out.append(f"# {board} — Consultation ({today})")
    out.append("")
    out.append("## The decision")
    out.append(decision_text if decision_text else "_(no decision file provided)_")
    out.append("")
    out.append(f"## The panel ({len(advisors)})")
    out.append(", ".join(a["name"] for a in advisors))
    out.append("")
    out.append("## Each advisor's read")
    out.append("")
    for a in advisors:
        out.append(advisor_section(a))
        out.append("")
    out.append("## Where they agree / conflict")
    out.append("| Point | Who agrees | Who pushes back |")
    out.append("|---|---|---|")
    out.append("| _key point 1_ | | |")
    out.append("| _key point 2_ | | |")
    out.append("")
    out.append("## Synthesis")
    out.append("- **Strongest signal across the board:** ")
    out.append("- **The real tension:** ")
    out.append("- **What this means for DVN specifically:** ")
    out.append("")
    out.append("## Recommended call")
    out.append("> One action. The board informed it; DVN owns it.")
    out.append("")
    out.append("## Open question to resolve next")
    out.append("> ")
    out.append("")
    out.append("---")
    out.append("_Log the decision and (later) the outcome via `/improve-system` so "
               "the board builds a track record._")
    return "\n".join(out)


def run(args):
    meta, advisors = load_advisors(args.advisors)
    clean, warnings = validate(advisors)
    for w in warnings:
        print(f"[warn] {w}", file=sys.stderr)
    if len(clean) < MIN_ADVISORS:
        print("[error] No valid advisor profiles. Fill advisors.json from real sources first.",
              file=sys.stderr)
        return 1
    decision_text = read_decision(args.decision) if args.decision else ""
    today = args.today or date.today().isoformat()
    report = build_report(meta, clean, decision_text, today)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(report + "\n")
        print(f"Wrote consultation for {len(clean)} advisor(s) -> {args.out}")
    else:
        print(report)
    return 0


def selftest():
    sample = {
        "board_name": "Test Board",
        "advisors": [
            {
                "name": "A. Operator",
                "domain": "Sales systems",
                "decision_lens": "Does this add a listing in 90 days?",
                "heuristics": ["Simple beats clever", "Volume fixes most things"],
                "signature_moves": ["Double the prospecting before adding spend"],
                "will_flag": ["Vanity metrics"],
                "voice": "blunt, numbers-first",
                "sources": ["Book: The System (accessible)"],
            },
            {
                "name": "B. Builder",
                "domain": "Capital",
                "decision_lens": "What's the downside if this is wrong?",
                "heuristics": ["Protect the base first"],
                "signature_moves": ["Stage the bet"],
                "will_flag": ["Over-leverage"],
                "voice": "measured",
                "sources": ["Talk: Capital Discipline (accessible)"],
            },
            {  # invalid — should be dropped
                "name": "C. Placeholder",
                "decision_lens": "<...>",
                "sources": ["<...>"],
            },
        ],
    }
    clean, warnings = validate(sample["advisors"])
    assert len(clean) == 2, f"expected 2 valid advisors, got {len(clean)}"
    assert any("Placeholder" in w for w in warnings), "placeholder advisor not dropped"
    report = build_report(sample, clean, "# Decision: test\nShould we?", "2026-06-23")
    for needle in ["## Each advisor's read", "A. Operator", "B. Builder",
                   "Where they agree", "## Recommended call", "Built from:"]:
        assert needle in report, f"missing section: {needle}"
    assert "C. Placeholder" not in report, "invalid advisor leaked into report"
    print("selftest passed: validation drops bad profiles, report assembles all sections.")
    return 0


def main():
    p = argparse.ArgumentParser(description="Board of Advisors consultation assembler")
    p.add_argument("--advisors", help="path to advisors.json")
    p.add_argument("--decision", help="path to decision.md")
    p.add_argument("--out", help="output path for the consultation .md")
    p.add_argument("--mode", choices=["self", "client"], default="self")
    p.add_argument("--today", help="override date (YYYY-MM-DD), for reproducible output")
    p.add_argument("--selftest", action="store_true", help="run offline self-test")
    args = p.parse_args()
    if args.selftest:
        return selftest()
    if not args.advisors:
        p.error("--advisors is required (or use --selftest)")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
