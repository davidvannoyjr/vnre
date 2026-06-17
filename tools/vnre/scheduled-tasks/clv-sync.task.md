# Scheduled Task — clv-sync

- **Name:** `clv-sync`
- **Schedule:** Monthly — **first Monday 5:45 AM** (ahead of the Database & COI brief so scoring is current)
- **Skill:** `vnre-clv-sync`
- **Output:** `Follow Up Boss Pipeline/_data/clv-plan.json` + a dry-run summary in chat; optional partner brief
- **Prereqs:** `followupboss` MCP connected; `vnre_sold_history.json` present; `04 Tools/clv-sync-skill/config.json` set; FUB `Lifetime Value` custom field exists.

## Trigger prompt (paste verbatim)

```
Refresh client Lifetime Value (dry-run — do not write to FUB unless I say so).

1. Run build_clv.py --sold vnre_sold_history.json --people <latest COI pull
   or a fub_search_people dump> --config config.json --out _data/clv-plan.json.
   This sums each past client's commission across all their closings (repeat
   clients rank highest) and matches them to FUB people.
2. Run fub_push.py --plan _data/clv-plan.json (DRY-RUN — writes nothing). Show me
   the top 20 planned Lifetime Value updates and the count of unmatched past
   clients (candidates to add to FUB).
3. Wait for my go-ahead. Only when I approve, re-run fub_push.py with --config and
   --commit to write the Lifetime Value field.
4. Also generate the QuickBooks Partner Value brief: pull sales_by_customer_summary,
   run partner_value.py, and flag concentration + any MSA gaps.
```

## Notes
- Quarterly is enough if monthly feels heavy — the data moves slowly. Keep it ahead of the first Database & COI run of the period either way.
- Once you've validated a few dry-runs, you can let it auto-commit by adding `--commit` to step 2 and dropping the approval gate.

## On failure
- No `Lifetime Value` custom field in FUB → create it (Admin → Custom Fields), set the exact name in `config.json`, retry.
- Many unmatched clients → likely a name/address format mismatch; review `unmatchedClients` and the match confidence before committing.

## Governance (agent-ops — see [GOVERNANCE.md](GOVERNANCE.md))
- **Trigger:** cron — monthly, first Monday 5:45 AM (ahead of database-coi). Manual: "sync CLV".
- **STATE:** `<home>/_state/clv-sync.STATE.md`. Read first (last sync date, prior
  unmatched list, autonomy); write last (writeback count, unmatched count, tokens, cost).
- **Writer ≠ checker — hard gate: `Dry-Run/Commit Gate`.** `fub_push.py` is dry-run by
  default and **writes nothing without `--commit`.** Commit only on DVN approval (L2) — or,
  at L3, only when match-confidence ≥ threshold and 0 over-threshold unmatched.
- **Stop condition (machine-checkable):** `clv-plan.json` written **AND `writeback ≥ 1`**.
- **Iteration ceiling:** 1 pass/fire · retry ≤3 · 20 tool-calls hard cap.
- **Autonomy: L2 (Stage) → L3-eligible** for the Lifetime-Value writeback after a few clean
  dry-runs (idempotent, single reversible number field). Write the level in STATE; raise only on sign-off.
- **Found-something → inbox** (top-20 planned updates + unmatched count). **Found-nothing →
  silent archive** (no plan, no commit).
- **Shell allowlist:** `python3 scripts/build_clv.py …`, `fub_push.py …`,
  `partner_value.py …`, `fub_field_setup.py …` (+ `--selftest`). `--commit` is the one gated
  write; no network from sandbox.
- **Parallel:** N/A — sequential, ahead of database-coi by design.
- **Open box:** log tokens/iteration for 3–5 dry-runs into STATE.
