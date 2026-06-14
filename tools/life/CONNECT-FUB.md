# Connect Follow Up Boss (Phase 1.5)

FUB is the prospecting spine — calls, contacts, appts set/kept. It is **not connected in the
Claude web session**, so this is the one source you wire by hand. Adapter is built and tested
in shape (`ingest/sources/follow_up_boss.py`); it just needs the key.

## Option A — direct API (fastest, recommended for the pipeline)
1. Get the API key: FUB → **Admin → API** → copy the key. (Already on file in Drive:
   `fub-api-key.local.md` — never commit it.)
2. Drop it in `config.json` → `sources.follow_up_boss.api_key`, set `"enabled": true`.
3. Smoke-test a single day without touching the warehouse:
   ```
   FUB_API_KEY=xxxxx python ingest/sources/follow_up_boss.py --date 2026-06-14
   ```
   Expect: `{ "life.prospecting_daily": [{ calls, contacts, appts_set, appts_kept, source:"fub" }] }`
4. Tune the counting rules if your FUB outcomes differ from the defaults
   (`CONNECTED_OUTCOMES`, `KEPT_OUTCOMES` at the top of the adapter).
5. Schedule in n8n hourly during business hours (see README cadence).

## Option B — reuse the existing followupboss-mcp
You already run a custom `followupboss-mcp` (per `claude/CLAUDE.md`) for the VNRE skills.
Point n8n / the runner at the same key; the adapter logic is identical.

## What lights up when connected
- Daily tab → **Prospecting** card flips its source pill from `Manual · FUB pending` to
  `Manual + FUB` and the calls/contacts/appts numbers fill automatically.
- Summary row → **Calls** and **Kept** tiles update from FUB instead of the manual log.
- The manual Daily Log stays as the override/fallback for anything FUB didn't capture
  (e.g. dials made on a personal line).

## Counting assumptions (auditable — change in the adapter)
| Metric | Rule |
|---|---|
| calls | every logged call created that day |
| contacts | calls with outcome in `{Interested, Not Interested, Connected, Talked, Appointment Set}` |
| appts_set | appointments **created** that day |
| appts_kept | appointments **starting** that day with outcome in `{Met, Completed, Showed}` |
