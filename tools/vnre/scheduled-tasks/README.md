# VNRE Standing Scheduled Tasks

The cadence that makes the brain run itself. Each task here is a **Cowork scheduled task** —
a saved trigger prompt + a schedule. Claude runs the prompt; the skill does the work. These
are paste-ready definitions; create each one in your scheduled-tasks UI with the time shown.

## How to create one
In Claude desktop / Cowork → Scheduled Tasks → New:
1. **Schedule:** the day/time from the task file.
2. **Prompt:** paste the **Trigger prompt** block verbatim.
3. **Workspace:** connect the `_Claude md` Drive folder (so the skill + paths resolve).
4. Save. The task fires on schedule and lands its output in the folder noted.

## Master cadence (collision-checked)

| Time | Day | Task | Status |
|---|---|---|---|
| 4:55 AM | daily | **`morning-pull`** (shared FUB pull) | new → [morning-pull.task.md](morning-pull.task.md) |
| 5:00 AM | daily | `daily-lead-attention` (lead brief) | existing — consumes morning-pull |
| 5:15 AM | daily | **`active-hunter`** (call list) | new → [active-hunter.task.md](active-hunter.task.md) — consumes morning-pull |
| 5:45 AM | 1st Mon/month | **`clv-sync`** (refresh Lifetime Value) | new → [clv-sync.task.md](clv-sync.task.md) |
| 6:00 AM | Mon | **`database-coi`** (Database & COI brief) | new → [database-coi.task.md](database-coi.task.md) |
| 6:30 AM | Mon | **`ceo-dashboard`** (run my numbers) | new → [ceo-dashboard.task.md](ceo-dashboard.task.md) |
| 7:00 AM | daily | `plp-folder-build` (PLP prep) | existing |
| 8:48 AM | daily | Team huddle | existing |
| 6:00 PM | Sun | **`meta-review`** (weekly ops + cost rollup) | new → [meta-review.task.md](meta-review.task.md) |
| 5:00 PM | 1st Sun/month | **`drive-hygiene`** (duplicate / conflict / drift scan) | new → [drive-hygiene.task.md](drive-hygiene.task.md) |

**`morning-pull` (4:55)** pulls the union of pipeline + prospecting segments once; the 5:00
lead brief and 5:15 hunter list **read it and filter** instead of each hitting FUB — one pull
per morning instead of two, one consistent suppression snapshot. Both consumers fall back to
self-pull if the shared file is missing/stale, so it's non-breaking.

**`meta-review` (Sun 6 PM)** reads every `_state/*.STATE.md` ledger and reports fired-vs-missed,
cost vs the worst-case ceiling, autonomy/promotion candidates, and anomalies — the self-monitor
that closes the tokens/cost boxes with real numbers.

Order matters on the **first Monday of the month**: `clv-sync` (5:45) refreshes Lifetime
Value *before* `database-coi` (6:00) so Database & COI scoring is profit-weighted. Other
Mondays, the brief uses the last CLV sync.

## Shared prerequisites (one-time, per device)
- `followupboss` MCP server connected (lead brief / database & COI / clv-sync).
- QuickBooks MCP connected (ceo-dashboard / clv-sync partner view).
- Skills saved in Claude desktop; each tool's `config.json` filled from its `config.example.json`.

## Safety posture
- **database-coi, ceo-dashboard:** read-only outputs (briefs + drafts). Nothing sends
  or writes automatically.
- **clv-sync:** scheduled run produces the plan + **dry-run** only. It does **not** auto-write
  to FUB. Flip to auto-commit (add `--commit`) yourself once you've validated a few runs.

## Governance (agent-ops standard)
Every task here is governed by **[GOVERNANCE.md](GOVERNANCE.md)** — the agent-ops hygiene
standard (trigger, STATE read-first/write-last, writer≠checker with a named hard gate,
machine-checkable stop condition, iteration ceiling, autonomy level, found→inbox/none→silent,
shell allowlist, cost model). Each `*.task.md` carries a filled-in `## Governance` block;
the run ledger scaffold is **[STATE.template.md](STATE.template.md)**.

- **Autonomy today:** `morning-pull`, `meta-review`, `drive-hygiene`, `ceo-dashboard` L1 (read-only) ·
  `active-hunter`, `database-coi`, `clv-sync` L2 (stage drafts/dry-runs, nothing sends) ·
  `clv-sync` writeback L3-eligible.
- **Worst-case day** (first Monday, all six fire): ≈ 365k input / 66k output tokens —
  low single-digit dollars at the ballpark Opus rate. Math + levers in GOVERNANCE §9.
- **The one open box** across all tasks: run each 3–5× and record tokens/iteration in its
  STATE ledger to replace the estimates. Everything else is satisfied by the suite design.
- `daily-lead-attention` + `plp-folder-build` (defined in Drive) inherit this standard —
  add the same block when you next edit them.
