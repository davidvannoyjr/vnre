# Scheduled Task — active-hunter

- **Name:** `active-hunter`
- **Schedule:** Daily — **5:15 AM** (ready before the 7:30 AM prospecting block; pairs with the 5:00 lead brief)
- **Skill:** `vnre-active-hunter`
- **Output:** `Follow Up Boss Pipeline/YYYY-MM-DD Call List.md`
- **Prereqs:** `followupboss` MCP connected; `04 Tools/active-hunter-skill/` installed.

## Trigger prompt (paste verbatim)

```
Build today's Active-Hunter call list.

1. Pull FUB prospecting contacts — FSBO, Expired, Aged Lead, Geo-farm, COI, Past
   Client — with id, name, phone, address/city, tags/stage, lastAttemptDate,
   attempts, and any signal. Include the DNC/Opt-Out tag so it can be filtered.
   Save to _data/hunter-pull-<today>.json.
2. Run build_call_list.py --pull that file --out "Follow Up Boss Pipeline/<today>
   Call List.md" --today <today>.
3. Present the list grouped by segment with the script reference per group. Note the
   suppressed counts (DNC/opt-out, dialed <2d, maxed).
4. As I work it: connect -> run vnre-book-appointment; no-answer -> log the attempt
   and draft the next nurture touch (Gmail/text draft, approval-gated). Nothing sends
   automatically. Respect KS/MO calling hours and any opt-out.
```

## On failure
- `fub_*` tools missing → restart Claude / run fix-claude-config.sh (Claude quit).
- Empty pull → report and stop; don't overwrite the prior list with an empty one.
