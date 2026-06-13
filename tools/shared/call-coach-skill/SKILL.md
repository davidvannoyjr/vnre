---
name: vnre-call-coach
description: Score one prospecting/listing call transcript (from Granola) against the script rubric — phase adherence (opener → discovery → value → close), objections raised vs handled, talk-ratio and questions-asked metrics — into a private self-coaching report with two drills. Use whenever DVN says "coach my call", "review this call", "how did that call go", "score my FSBO/expired call", or after a Granola-recorded prospecting call. aiDrVN Stage 09 (self mode; client/agent report modes available).
---

# VNRE Call Coach — Stage 09 (Scale), self mode

Turns a recorded call into a fast, honest self-review: did you run the play, did you handle the
objections, did you **ask for the appointment** — and the 2 things to drill next time. Lifts your
own conversion (the funnel multiplier) using calls you're already recording in Granola.

## Architecture
Granola transcript → deterministic rubric scoring → coaching report. Same shape as the rest.

1. **Get the transcript:** pull the call from the **Granola MCP** (`get_meeting_transcript` /
   `query_granola_meetings`). Save as JSON `[{speaker, text}]` or plain `Speaker: line` text.
2. **Context:** `{"agent": "David", "contact": "FSBO — 100 Main St", "outcome": "booked|callback|no"}`.
3. **Coach:** `python3 scripts/coach_call.py --transcript t.json --rubric rubric.json --type
   fsbo|expired|aged_lead|listing_appt --context ctx.json --out "<folder>/<date> Call Coach.md"`.
4. **Layer judgment.** The rubric scores the mechanics; you (Claude) add the qualitative read —
   rapport, where the energy shifted, the line that actually moved them — and confirm the drills.

## What it scores
- **Phase adherence** (weighted): opener → discovery → value → close, hit/total per phase.
- **Objections:** which came up and whether you addressed them (the rubric per call type).
- **Metrics:** questions you asked (flag if thin) and your **talk ratio** (flag if you dominated).
- **Drills:** the highest-weight miss + the weakest metric → two concrete reps for next call.

## Rubric
`rubric.json` (copy from `rubric.example.json`) defines the checkpoints + objection patterns per
call type, mirroring the active-hunter call scripts. Keep the rubric and the scripts in sync —
when you change a script, update its checkpoints.

## Report modes (one engine)
`--mode self` (default, private) · `--mode client` (DVN Coaching client review) · `--mode agent`
(new-agent ramp scorecard). Only the framing changes; you locked **self** for now. The other modes
are how this becomes a Tier-3 coaching product later — no rebuild needed.

## Cadence
After any meaningful prospecting call, or a weekly roll-up across the week's recorded calls to
spot a pattern (e.g., "closes missed on 3 of 5 FSBOs → drill the ask").

## Verify offline
`python3 scripts/coach_call.py --selftest`
