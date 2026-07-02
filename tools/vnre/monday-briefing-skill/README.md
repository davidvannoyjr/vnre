# monday-briefing

DVN's Monday-morning executive briefing. Scheduled for **Monday 5:00 AM America/Chicago**; lands as
a phone-readable **Gmail draft** (never a send) plus a saved `.md` in the project folder.

## What it is
A chief-of-staff pass across five connected systems, delivered before the week starts:

| Source | Window | Signal |
|---|---|---|
| Google Calendar | week ahead (Mon–Sun) | tagged appts + dead/unblocked time |
| Gmail | last 7 days | unread / awaiting-reply, filtered to client / recruiting / money |
| Google Drive | last 7 days | docs modified = movement |
| Granola | last 7 days | action items + flagged client issues |
| FUB | live | Hot/Watch leads regressing or stalling (via `fub_lead_attention_pull`) |

Six sections out: Key Opportunities · Recruiting Updates · Client Issues · Upcoming Appointments ·
KPI Risks (vs the 40-appt / 100-day target) · Top 3 Priorities.

## Architecture
`MCP pull → _data/*.json → build_briefing.py (filter/dedup/KPI) → Claude judgment pass → Gmail draft.`
The script is deterministic and offline; Claude does the ranking, friction calls, and Top-3 voice.
See [`SKILL.md`](SKILL.md) for the full contract.

## Files
- `SKILL.md` — the operating instructions Claude follows.
- `scripts/build_briefing.py` — deterministic engine (pure stdlib; `--selftest` runs on `sample/`).
- `config.example.json` — copy to `config.json`; holds the campaign start + targets.
- `sample/` — fixture pulls for the selftest.

## Run it
- **Scheduled:** `tools/vnre/scheduled-tasks/monday-briefing.task.md` (Mon 5:00 AM Central).
- **Manual:** "run the Monday briefing."
- **Offline check:** `python3 scripts/build_briefing.py --selftest`.

## Safety
Draft only — `create_draft`, never send. If an MCP source is down at run time, the briefing fails
loudly (notes the missing source at the top) and builds from what's reachable. Pulled `_data/*.json`
is gitignored and pruned after 14 days.
