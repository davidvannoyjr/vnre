---
name: board-of-advisors
description: Run DVN's Board of Advisors — bring a real decision and get each cloned advisor's read in their own decision lens, a map of where they agree and conflict, a synthesis, and one recommended call. Use when DVN says "ask the board", "what would the board do", "run this past my advisors", "board consultation on {decision}", or wants structured outside counsel before a high-stakes call. Built from real, sourced material per advisor — never invented positions.
---

# Board of Advisors — cloned counsel on demand

Turns the people DVN already learns from into a queryable panel. Bring a decision,
get each advisor's read through *their* lens, the agreement/conflict map, the
synthesis, and one recommended action. The board informs the call; DVN makes it.

## Architecture
Same shape as the rest of the suite: structured registry → deterministic
assembly → review → decide → capture.

1. **Registry** — `advisors.json` (from `advisors.example.json`) holds 3–7
   advisors, each with a sourced profile: decision lens, heuristics, signature
   moves, what they flag, and the material the profile is built from.
2. **Decision** — a short file: context paragraph + the specific question +
   constraints. Template at the top of `interview-guide.md`.
3. **Consult** —
   `python3 scripts/consult_board.py --advisors advisors.json --decision decision.md --out "<home>/<today> <Decision> - Board Consultation.md"`.
   Deterministic: it assembles the per-advisor consultation structure, the
   conflict matrix, and the synthesis scaffold. No network in the assembly layer.
4. **Work it** — read each advisor's section, pressure-test "does this sound like
   them," tune the profile where it doesn't, decide.
5. **Capture** — log the decision and (later) the outcome via `/improve-system`
   so each advisor builds a track record and a wrong-but-loud voice loses weight.

## Building the registry (the four source steps)
1. **Interview** DVN — goals + the decisions the board serves. See
   `interview-guide.md`.
2. **Identify** 3–7 experts with *accessible* thinking (books, long-form talks,
   written frameworks). No un-sourceable picks.
3. **Ingest** each into a profile. Spec + JSON shape: `ingestion-spec.md`.
4. **Query** with `consult_board.py`.

## Rules (non-negotiable)
- **Real sources only.** Every profile lists its `sources`. No invented positions.
- **Advisor, not oracle.** Output ends in a recommendation to DVN, never a
  decision made for him.
- **Synthesis required.** The conflict map + one recommended call is the
  deliverable — not a pile of opinions.
- **Voice fidelity.** An advisor's section must read like that person; if it
  doesn't, the profile is wrong — fix the registry, not the output.

## Modes
- `--mode self` (default) — DVN's own board.
- `--mode client` — re-point at a coaching client's admired operators (DVN
  Coaching / aiDrVN product). Same engine, client registry.

## Cadence
On demand, before any high-stakes call. Lives in `tools/shared/` because the same
engine serves VNRE decisions and the coaching product.

## Verify offline
`python3 scripts/consult_board.py --selftest`
