---
name: monday-briefing
description: Build DVN's Monday-morning executive briefing — a chief-of-staff pass across Calendar, Gmail, Drive, Granola, and FUB that lands as a phone-readable Gmail DRAFT (never a send) by 5 AM Central. Six sections: Key Opportunities, Recruiting Updates, Client Issues, Upcoming Appointments, KPI Risks, and the Top 3 Priorities forcing-function call. Use whenever DVN says "run the Monday briefing", "Monday brief", "week-ahead brief", "what's my week look like", "build my exec briefing", or when the monday-briefing scheduled task fires. Re-run / tune anytime.
---

# VNRE Monday Executive Briefing

Every Monday at 5:00 AM Central, before the day starts: pull from the connected systems, run a
chief-of-staff analysis pass, and leave a finished briefing as a **Gmail draft** DVN reads on his
phone. The deterministic script does the filtering and assembly; **Claude does the judgment** —
ranking opportunities, calling friction, and writing the Top 3 in DVN's voice. **Output is always a
draft. It never sends.**

Same architecture as `daily-lead-attention`: **MCP pull → deterministic Python → Claude judgment → deliver.**

## Architecture (why it works this way)

The Cowork/Claude sandbox cannot reach external APIs directly. All live data comes through **MCP
servers running on DVN's Mac** (`fub_*`, Gmail, Google Calendar, Google Drive, Granola — load via
ToolSearch if deferred). Flow:

1. **Pull** — MCP tools dump raw data to JSON in `_data/` (one `pull-<source>-<date>.json` per source).
2. **Build** — `scripts/build_briefing.py` tags, filters, dedups, runs the KPI math, prunes old
   pulls, and emits `briefing.json` (structured) + a markdown skeleton. No network, pure stdlib.
3. **Judge** — Claude reads `briefing.json`, ranks the opportunities, separates real friction from
   noise, makes the Top-3 call, and writes every section in DVN's voice.
4. **Deliver** — Gmail `create_draft` to david@vannoyre.com + save the `.md` to the project folder.

If an MCP source is missing at run time: **fail loudly** — note which source was unavailable in the
draft and build the briefing from everything reachable. Never silently skip a source.

## Paths (production — OUTSIDE any Drive-synced folder)

- **Project home (deliverables + state):** `/Users/davidvannoy/Claude/Projects/Monday Briefing/`
  (resolve the bash session mount prefix at runtime — same convention as the lead brief).
- Briefing: `<home>/YYYY-MM-DD Monday Briefing.md`
- Working data: `<home>/_data/` → `pull-calendar-<date>.json`, `pull-gmail-<date>.json`,
  `pull-drive-<date>.json`, `pull-granola-<date>.json`, `pull-fub-<date>.json`, `briefing.json`
- This skill's script: `<skill>/scripts/build_briefing.py`
- Config: `<skill>/config.json` (copy from `config.example.json`; holds the 100-day campaign start).

## Pull layer (last 7 days unless noted)

Load any deferred MCP tool via ToolSearch first. Dump each raw result to `_data/pull-<source>-<today>.json`.

1. **Google Calendar — the WEEK AHEAD (Mon–Sun).** `list_events` from this coming Monday through
   Sunday. The script tags each event: listing appt / coaching / closing-transaction / prospecting
   block / other, and flags dead (unblocked) weekday time.
2. **Gmail — unread + awaiting-my-reply, last 7 days.** `search_threads` (e.g.
   `is:unread newer_than:7d` and `to:me -from:me newer_than:7d`). The script keeps client /
   recruiting / money (invoices, commissions, disputes) and drops newsletters + automated noise.
3. **Google Drive — docs modified in last 7 days** = movement signal. `list_recent_files`
   (`orderBy: lastModified`). Title + folder + date.
4. **Granola — meeting notes, last 7 days.** `list_meetings` / `query_granola_meetings`. The script
   extracts action items and anything flagged as a client issue or commitment.
5. **FUB — reuse the existing `fub_lead_attention_pull`.** Do **not** rebuild lead scoring. Call the
   existing tool, dump its output, and the script surfaces only Hot/Watch leads regressing or
   stalling. If `fub_*` is unavailable: note it in the draft and continue (the appt count for KPI is
   then unknown — say so).

## Build

```bash
python3 "<skill>/scripts/build_briefing.py" \
  --calendar "<home>/_data/pull-calendar-<today>.json" \
  --gmail    "<home>/_data/pull-gmail-<today>.json" \
  --drive    "<home>/_data/pull-drive-<today>.json" \
  --granola  "<home>/_data/pull-granola-<today>.json" \
  --fub      "<home>/_data/pull-fub-<today>.json" \
  --campaign-start <YYYY-MM-DD> --appts-to-date <N from FUB, omit if unknown> \
  --data-dir "<home>/_data" --retain-days 14 \
  --out-json "<home>/_data/briefing.json" \
  --out-md   "<home>/_data/skeleton.md" \
  --today <today>
```
(Translate paths to the bash mount prefix.) The script owns: event tagging + dead-time detection,
the Gmail noise/keep filter, Drive movement list, Granola action-item + issue extraction, the FUB
Hot/Watch regressing filter, the KPI pace math (40 appts / 100 days → required pace + gap), and the
14-day prune of `pull-*.json`. Pass `--appts-to-date` only when FUB gives a real booked count;
otherwise the KPI section flags it as unknown. Tuning constants are at the top of the script.

## Analysis layer — the chief-of-staff pass (Claude, not the script)

Read `briefing.json` and produce six sections. This is where judgment earns its keep:

- **Key Opportunities** — *ranked*. Lead with the FUB stalling Hot/Watch leads and the strongest
  Drive/email movement. Each gets the specific next action, not a restatement of the signal.
- **Recruiting Updates** — coaching-pipeline movement + any agent conversations (recruiting emails,
  the recruiting-pipeline doc, coaching 1:1 commitments from Granola).
- **Client Issues** — anything in email or notes flagged as friction or risk. Name the client, the
  issue, and what closes it.
- **Upcoming Appointments** — the week's appts with prep status (prepped / needs prep). Cross-check
  Drive: a listing appt with a built PLP = prepped; one without = needs prep.
- **KPI Risks** — appointment count vs the 100-day target (**40 appointments**), listing-pipeline
  gaps, anything trending the wrong way. Use the script's pace + gap numbers; state the gap plainly.
- **Top 3 Priorities for the Week** — the forcing-function call. DVN's voice, no hedging. These are
  the three things that, done, make the week. Rank ruthlessly.

Apply the **`dvn-voice`** skill to all prose: direct, clear, efficient, solutions only, no preamble.
Write as DVN, not about him. Banned: "I hope this finds you well," "just checking in," any softener.

## Deliver

1. **Save the `.md`:** write the finished briefing to `<home>/YYYY-MM-DD Monday Briefing.md`.
2. **Gmail draft (never send):** `create_draft` to `david@vannoyre.com`.
   - Subject: `🗓 Monday Briefing — {Mon DD}`
   - Body: clean **`htmlBody`** — phone-readable, the six sections as `<h2>`/`<ul>`, scannable at
     5am. Keep it tight; this is read on a phone before coffee. Lead any unavailable-source warning
     at the very top so DVN knows what's missing.
3. **Confirm** in chat: "Draft saved — not sent," with the section counts and anything overruled.
   Nothing auto-sends. Ever.

## Housekeeping
The build step prunes `_data/pull-*.json` older than 14 days (`--data-dir` + `--retain-days 14`).

## Cadence
Monday 5:00 AM **America/Chicago** via the `monday-briefing` scheduled task
(`tools/vnre/scheduled-tasks/monday-briefing.task.md`). Manual trigger: "run the Monday briefing."

## Verify offline
`python3 scripts/build_briefing.py --selftest` — renders from `sample/` fixtures, no network.
