# Board of Advisors — Ingestion Spec

How to turn an advisor's real material into a registry profile. The goal is
**fidelity from sources**, not impersonation from memory. If a field can't be
backed by the material, leave it empty rather than invent it.

## What counts as a source
Accessible, attributable material:
- Books / published frameworks.
- Long-form talks, interviews, YouTube (transcript-able).
- Written posts, newsletters, courses the advisor authored.

Not a source: a general reputation, a single quote out of context, or "everyone
knows they think X."

## Process per advisor
1. **Collect** 2–5 substantial pieces of their material.
2. **Extract** the recurring structure:
   - The **first question** they ask of any decision → `decision_lens`.
   - Their **rules of thumb**, in their phrasing → `heuristics`.
   - Their **default plays** → `signature_moves`.
   - The **risk they reliably catch** → `will_flag`.
   - **How they talk** (cadence, bluntness, jargon) → `voice`.
3. **Cite** every piece you drew from → `sources`. This is what keeps the board
   honest and what lets DVN check a read against the real person.
4. **Weight** — default `1.0`. Raise/lower as track record accrues (a loud advisor
   who's been wrong gets dialed down via `/improve-system`).

## Quality bar
- A profile passes when a section generated from it reads like the real person to
  DVN. If it doesn't, the extraction is thin — go back to the material.
- No two advisors should collapse into the same voice. If they do, the board isn't
  diverse enough to be useful.

## Refresh
Re-ingest when an advisor publishes something that materially shifts their thinking,
or when a consultation exposes a gap. Note the refresh date in the profile's
`sources`.

## Privacy / git
The example registry is safe to commit. A real `advisors.json` that references
private notes or a client's board should stay out of git — `config.json` and
`_data/` are already gitignored; keep private registries there or name them
`*.local.json`.
