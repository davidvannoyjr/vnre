# vnre-active-hunter — Stage 01 daily prospecting targeting

Ranks today's outbound targets across **FSBO, Expired, Aged Lead, Geo-farm, COI, Past Client**,
attaches the right DVN-voice script, and filters **DNC/opt-out** up front. Connect → book via
`vnre-book-appointment`; no-answer → nurture sequence. Aimed at the plan's 120 listing appointments.

## Files
```
active-hunter-skill/
├── SKILL.md, README.md
├── scripts/build_call_list.py        # ranking + DNC/recency/attempt suppression
├── call-scripts/                     # FSBO, Expired, Aged-Lead, Circle-COI, Past-Client, _nurture-sequences
└── sample/sample_pull.json
```

## Try it (no network)
```bash
python3 scripts/build_call_list.py --selftest
python3 scripts/build_call_list.py --pull sample/sample_pull.json --out /tmp/calls.md --today 2026-06-13
cat /tmp/calls.md
```

## Ranking
`score = segment weight + signal boost + recency boost`. Segment weights: FSBO/Expired 5,
Past Client 4, COI/Aged 3, Geo-farm 2. Suppressed: DNC/opt-out, dialed < 2 days ago, attempts ≥ 8.
Tune at the top of `build_call_list.py`.

## Compliance
DNC/opt-out filtered automatically; you still own TCPA consent, KS/MO calling hours, and recording
consent (KS one-party / MO all-party). This is human-dial targeting — the voice overlay is gated on
the compliance checklist in `../stage01-prospecting/SCOPE.md`.

> The scripts double as your `02 Reference/Scripts/` library; keep both in sync.
