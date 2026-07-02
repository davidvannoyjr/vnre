# Scheduled Task — monday-briefing

- **Name:** `monday-briefing`
- **Schedule:** Weekly — **Monday 5:00 AM America/Chicago**
- **Skill:** `monday-briefing`
- **Output:** `Monday Briefing/YYYY-MM-DD Monday Briefing.md` + a Gmail **draft** to david@vannoyre.com
- **Prereqs:** Gmail, Google Calendar, Google Drive, Granola, and `fub_*` MCP servers connected on the Mac; `Monday Briefing/monday-briefing-skill/config.json` set (campaign start + targets).

## Trigger prompt (paste verbatim)

```
Run my Monday executive briefing.

1. Pull to Monday Briefing/_data/ (one pull-<source>-<today>.json each):
   - Google Calendar: list_events for the WEEK AHEAD (this coming Mon 00:00
     through Sun 23:59).
   - Gmail: search_threads for "is:unread newer_than:7d" and
     "to:me -from:me newer_than:7d".
   - Google Drive: list_recent_files, orderBy lastModified (last 7 days).
   - Granola: list_meetings / query_granola_meetings, last 7 days.
   - FUB: call the existing fub_lead_attention_pull and dump its output. Do not
     rebuild lead scoring.
   If any MCP source is unavailable, note WHICH one and keep going — fail loudly
   in the draft, do not skip silently.
2. Run build_briefing.py with those pulls, --campaign-start + --appts-to-date
   from config / the FUB pull, --data-dir Monday Briefing/_data --retain-days 14,
   today = <today>. It writes briefing.json + a skeleton.
3. Chief-of-staff pass on briefing.json: rank Key Opportunities with a specific
   next action each; pull Recruiting Updates; flag Client Issues (name + fix);
   mark each Upcoming Appointment prepped/needs-prep (cross-check Drive for a
   built PLP); state KPI Risks vs the 40-appt/100-day target using the script's
   pace + gap; write the Top 3 Priorities as a forcing-function call. dvn-voice
   throughout — direct, no hedging.
4. Save the briefing .md to the Monday Briefing folder, then create a Gmail
   DRAFT to david@vannoyre.com — subject "🗓 Monday Briefing — <Mon DD>",
   clean phone-readable htmlBody, the six sections. NEVER send. Draft only.
5. Chat summary: section counts, anything overruled, any source that was down.
```

## On failure
- A source MCP missing → name it at the top of the draft and build from the rest. Do not abort the whole run for one missing source.
- `fub_*` missing → KPI appts-to-date is unknown; omit `--appts-to-date` so the KPI section says so. Restart Claude; if still missing run `followupboss-mcp/fix-claude-config.sh` (Claude quit). Never curl FUB from the sandbox.
- Empty week-ahead calendar → still build; the brief should say the week is wide open and push prospecting into the dead time.
- This task NEVER sends mail. If you ever find yourself about to call a send tool, stop — the deliverable is a draft.
