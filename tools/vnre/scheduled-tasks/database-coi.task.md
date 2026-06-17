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

## Governance (agent-ops — see [GOVERNANCE.md](GOVERNANCE.md))
- **Trigger:** cron — weekly Monday 6:00 AM (documented above). Manual: "run the Database & COI brief".
- **STATE:** `<home>/_state/database-coi.STATE.md`, wrapping the existing
  `_data/coi-state.json` dedupe memory. Read first (30-day suppression, held-back
  high-value, carried items); write last (counts by moment, tokens, cost).
- **Writer ≠ checker — hard gate: `Defensible-Claim Gate`.** `build_coi_brief.py` owns
  30-day suppression + scoring; **no draft leaves staging with an equity number DVN can't
  defend or a suppressed contact.** Review step (SKILL §3) is the human half of the gate.
- **Stop condition (machine-checkable):** brief `.md` written **AND `surfacedCount > 0`**,
  state dedupe applied.
- **Iteration ceiling:** 1 pass/fire · retry ≤3 · 20 tool-calls hard cap.
- **Autonomy: L2 (Stage).** Gmail **drafts** + Canva one-pagers only — **nothing sends**.
- **Found-something → inbox** (brief + staged drafts + summary). **Found-nothing → silent
  archive** (STATE line only; keep the prior brief).
- **Shell allowlist:** `python3 scripts/build_coi_brief.py …` (verify offline against
  `sample/`), `build_delivery.py …` (+ `--selftest`); no network from sandbox.
- **Parallel:** N/A — sequential. Worktree-isolate any future multi-segment backfill.
- **Open box:** log tokens/iteration for 3–5 runs into STATE.
