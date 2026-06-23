# Project — Board of Advisors

**Purpose (DVN personal / strategic):** Clone the expertise of the people DVN
already learns from into a queryable panel. Bring a real decision, get each
advisor's read in their own lens, get the synthesis, decide faster and better.

**Status:** Framework built 2026-06-23. Skill scaffolded, registry seeded with
slots, interview + ingestion specs written. Goes live once the advisor registry is
filled and a first decision is run through it.

---

## Why this, why now
DVN makes high-stakes calls weekly — pricing strategy, hiring, capital, where to
point the brokerage. He already absorbs a handful of operators through podcasts,
books, and YouTube. The board makes that absorption *on-demand and structured*
instead of remembered-when-convenient. It is the first **Skill** of the new OS and
the template every later advisor-style skill copies.

## How it works (the five steps from the source)
1. **Interview** — Claude interviews DVN to pin the goals and the kinds of
   decisions the board exists to serve. Guide: `tools/shared/board-of-advisors-skill/interview-guide.md`.
2. **Identify** — pick 3–7 experts with *accessible, real* material (books,
   long-form talks, written frameworks). No one whose thinking can't be sourced.
3. **Ingest** — pull their content into a structured profile per advisor: their
   decision lens, heuristics, signature moves, what they'd flag. Spec:
   `tools/shared/board-of-advisors-skill/ingestion-spec.md`.
4. **Skill** — `consult_board.py` turns a decision + the registry into a
   structured multi-advisor consultation prompt, then a synthesis.
5. **Ask** — bring a real decision, get per-advisor guidance + the synthesis +
   one recommended call.

## Inputs
- `advisors.json` (from `advisors.example.json`) — the filled registry.
- The decision: one paragraph of context + the specific question + constraints.

## Outputs
- `YYYY-MM <Decision> - Board Consultation.md` — per-advisor reads, points of
  agreement/conflict, synthesis, one recommended action, and the open question to
  resolve next.

## Process
1. `python3 scripts/consult_board.py --advisors advisors.json --decision decision.md --out "<home>/<today> <Decision> - Board Consultation.md"`
2. Review each advisor's read for "does this actually sound like them." Tune the
   profile in `advisors.json` where it doesn't.
3. Decide. Log the call and the outcome back via `/improve-system` so the board's
   track record is visible over time.

## Decisions (do not relitigate)
- **Real sources only.** Every advisor profile cites the material it's built from.
  No invented positions, no "channeling" someone with no accessible thinking.
- **Advisor, not oracle.** The board informs DVN's decision; it never makes it.
- **Synthesis is required.** A pile of opinions is not the deliverable — the
  conflict map + one recommended call is.
- **Track record on.** Outcomes feed back so a loud advisor who's wrong loses
  weight.

## Connects to
- **`/improve-system`** — decisions and outcomes captured here refine future
  consultations.
- **DVN Coaching** — the same engine, re-pointed at a coaching client's own
  admired operators, is a sellable aiDrVN module later.
