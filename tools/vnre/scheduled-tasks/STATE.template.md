# STATE — `<task-name>`

> Run ledger. The agent **reads this first** (last run, suppression window, carried
> items, autonomy) and **writes it last** (this run's result). Lives at
> `<home>/_state/<task>.STATE.md`, beside the deliverables. Gitignored — never commit
> real CRM/financial data. Pairs with `<task>.state.json` for machine dedupe.

## Header (rarely changes)
- **Task:** `<task-name>`
- **Autonomy level:** `L_` (see GOVERNANCE §1 — raise only on DVN sign-off)
- **Checker gate:** `<named gate>` (GOVERNANCE §3)
- **Stop condition:** `<machine-checkable assertion>` (GOVERNANCE §4)
- **Suppression window:** `<e.g. 30 days>` · **Attempt cap:** `<n>`

## Carry-forward (read before the pull)
- **Unmatched / deferred items:** `<none | list>`
- **Held-back high-value:** `<none | list>`
- **Open anomaly from last run:** `<none | note>`

## Run log (newest first — append each fire)

| Run # | Date/time | Trigger | Output | Surfaced | Suppressed | Carried | Tokens in/out | Est. cost | Anomalies |
|---|---|---|---|---|---|---|---|---|---|
| 3 | YYYY-MM-DD HH:MM | cron | `…/<file>.md` | 12 | 5 | 0 | 64k / 11k | $_ | — |
| 2 | … | cron | … | 0 | — | — | … | $_ | silent archive (empty pull) |
| 1 | … | manual | … | 9 | 4 | 1 | … | $_ | — |

## Tokens/iteration (fill from 3–5 real runs — closes the last checklist box)
- Run 1: `___k in / ___k out`
- Run 2: `___k in / ___k out`
- Run 3: `___k in / ___k out`
- **Median:** `___k in / ___k out` → replaces the GOVERNANCE §9 estimate for this task.
