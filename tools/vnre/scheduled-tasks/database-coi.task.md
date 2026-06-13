# Scheduled Task — database-coi

- **Name:** `database-coi`
- **Schedule:** Weekly — **Monday 6:00 AM**
- **Skill:** `vnre-database-coi`
- **Output:** `Follow Up Boss Pipeline/YYYY-MM-DD Database & COI Brief.md` + Gmail drafts
- **Prereqs:** `followupboss` MCP connected; `04 Tools/plp-presentation-builder/vnre_sold_history.json` present; `04 Tools/database-coi-skill/config.json` set.

## Trigger prompt (paste verbatim)

```
Run the weekly Database & COI brief.

1. Pull Past Client + Sphere/COI contacts from Follow Up Boss using fub_pull.py
   (or the fub_* tools): id, name, address/city, tags, stage, close date + sale
   price from the most recent won deal, last-contact date, recent property-view
   events, and the mortgage-rate / birthday / preferred-channel / lifetime-value
   custom fields. Save to Follow Up Boss Pipeline/_data/coi-pull-<today>.json.
2. Run build_coi_brief.py with that pull, --sold vnre_sold_history.json, and
   the coi-state.json, today = <today>. Output the brief to the Follow Up
   Boss Pipeline folder.
3. Review the drafts: kill any equity claim you can't defend, personalize the top
   few from prior conversation notes, keep DVN's voice. Respect the 30-day
   suppression.
4. For the touches that look ready, create Gmail DRAFTS (do not send). For each
   Equity Update, also generate a branded Canva "Your Home Equity Update" one-pager.
5. Post a short chat summary: counts by moment, anything overruled, anyone
   high-value held back. Nothing sends automatically.
```

## On failure
- `fub_*` tools missing → restart Claude; if still missing run `followupboss-mcp/fix-claude-config.sh` (Claude quit). Do not curl FUB from the sandbox.
- Empty pull → report it and stop; do not write an empty brief over the prior one.
