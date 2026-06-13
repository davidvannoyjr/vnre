# vnre-call-coach — Stage 09 (Scale), self mode

Scores one prospecting/listing call transcript (Granola) against the script rubric → a private
self-coaching report: phase adherence, objections raised/handled, talk-ratio + questions metrics,
and two drills. Built to lift your own conversion using calls you already record.

## Files
```
call-coach-skill/
├── SKILL.md, README.md
├── rubric.example.json        # checkpoints + objections per call type (fsbo/expired/aged_lead/listing_appt)
├── scripts/coach_call.py
└── sample/  (sample_transcript.json, sample_context.json)
```

## Try it (no network)
```bash
python3 scripts/coach_call.py --selftest
python3 scripts/coach_call.py --transcript sample/sample_transcript.json \
  --rubric rubric.example.json --type fsbo --context sample/sample_context.json \
  --out /tmp/coach.md --today 2026-06-13
cat /tmp/coach.md
```

## Input
- **Transcript:** JSON `[{speaker, text}]` or plain text `Speaker: line` (from the Granola MCP).
  Your turns are detected by the `agent` name in context (or labels like "Me"/"David"/"DVN").
- **Rubric:** per-call-type checkpoints (regex patterns over your lines) + objection patterns.
- **Context:** `agent`, `contact`, `outcome`.

## Modes
`--mode self` (default) · `client` · `agent` — same engine, different framing. Self is locked for
now; the others turn this into a DVN Coaching / new-agent product with no rebuild.

> The rubric scores mechanics deterministically; the skill adds the qualitative read on top. Keep
> `rubric.json` checkpoints in sync with the active-hunter call scripts.
