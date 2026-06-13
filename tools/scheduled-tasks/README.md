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
| 5:00 AM | daily | `daily-lead-attention` (lead brief) | existing |
| 5:15 AM | daily | **`active-hunter`** (call list) | new → [active-hunter.task.md](active-hunter.task.md) |
| 5:45 AM | 1st Mon/month | **`clv-sync`** (refresh Lifetime Value) | new → [clv-sync.task.md](clv-sync.task.md) |
| 6:00 AM | Mon | **`retention-referral`** (retention brief) | new → [retention-referral.task.md](retention-referral.task.md) |
| 6:30 AM | Mon | **`ceo-dashboard`** (run my numbers) | new → [ceo-dashboard.task.md](ceo-dashboard.task.md) |
| 7:00 AM | daily | `plp-folder-build` (PLP prep) | existing |
| 8:48 AM | daily | Team huddle | existing |

Order matters on the **first Monday of the month**: `clv-sync` (5:45) refreshes Lifetime
Value *before* `retention-referral` (6:00) so retention scoring is profit-weighted. Other
Mondays, retention uses the last CLV sync.

## Shared prerequisites (one-time, per device)
- `followupboss` MCP server connected (lead brief / retention / clv-sync).
- QuickBooks MCP connected (ceo-dashboard / clv-sync partner view).
- Skills saved in Claude desktop; each tool's `config.json` filled from its `config.example.json`.

## Safety posture
- **retention-referral, ceo-dashboard:** read-only outputs (briefs + drafts). Nothing sends
  or writes automatically.
- **clv-sync:** scheduled run produces the plan + **dry-run** only. It does **not** auto-write
  to FUB. Flip to auto-commit (add `--commit`) yourself once you've validated a few runs.
