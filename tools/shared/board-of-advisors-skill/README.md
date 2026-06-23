# board-of-advisors-skill

Cloned counsel on demand. Bring a real decision; get each advisor's read in their
own lens, the agreement/conflict map, a synthesis, and one recommended call.

```
board-of-advisors-skill/
├── SKILL.md              # the skill (trigger + architecture + rules)
├── README.md             # this file
├── advisors.example.json # registry template — copy to advisors.json and fill
├── interview-guide.md    # stand up the board; decision template
├── ingestion-spec.md     # turn real material into a sourced profile
└── scripts/
    └── consult_board.py  # deterministic assembler (--selftest)
```

## Quickstart
1. Run the interview (`interview-guide.md`) and pick 3–7 advisors with accessible
   material.
2. `cp advisors.example.json advisors.json` and fill each profile from real
   sources (`ingestion-spec.md`).
3. Write the decision into `decision.md` (template in `interview-guide.md`).
4. `python3 scripts/consult_board.py --advisors advisors.json --decision decision.md --out "<home>/<today> <Decision> - Board Consultation.md"`
5. Review, decide, capture the call via `/improve-system`.

## Verify
`python3 scripts/consult_board.py --selftest`

## Design rules (suite-wide)
Deterministic Python, offline `--selftest`, tunable constants at the top of the
script, approval-gated (writes a file, sends nothing). Real sources only — the
assembler drops any profile that still has `<placeholder>` fields or no sources.

## Drive home
`04 Tools/board-of-advisors-skill/` (flat, like the rest). Package as
`board-of-advisors.skill` for the desktop app. A private/client `advisors.json`
stays out of git — keep it as `*.local.json` or under `_data/`.
