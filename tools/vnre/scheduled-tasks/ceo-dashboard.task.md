# Scheduled Task — ceo-dashboard

- **Name:** `ceo-dashboard`
- **Schedule:** Weekly — **Monday 6:30 AM** (the month-end-close run is the one to read closely)
- **Skill:** `vnre-ceo-dashboard`
- **Output:** `Follow Up Boss Pipeline/YYYY-MM-DD CEO Dashboard.md` (or your finance folder)
- **Prereqs:** QuickBooks MCP connected; `04 Tools/ceo-dashboard-skill/plan.json` set (2026 targets).

## Trigger prompt (paste verbatim)

```
Run my weekly CEO dashboard.

1. From the QuickBooks MCP, pull profit_loss_quickbooks_account for periodStart =
   <this year>-01-01 through today, and qbo_accounting_get_ar_aging_summary. Save
   each report's JSON to _data/pl.json and _data/ar.json (the P&L is large — write
   it to a file, don't inline it).
2. Run build_dashboard.py --pl _data/pl.json --ar _data/ar.json --plan plan.json
   --out "<finance folder>/<today> CEO Dashboard.md" --today <today>.
3. Present the dashboard. Lead the chat summary with anything RED: margin vs the
   50% target (and the dollar gap), revenue pace vs plan, and any A/R 91+ days.
4. Read-only — never write to QuickBooks. Keep _data/*.json local (gitignored).
```

## On failure
- QuickBooks auth lapsed → say so and prompt DVN to re-authorize the QBO connector; do not fabricate numbers.
- Report saved-to-file too large to inline → pass it to build_dashboard.py by path (it only reads top-level keys).

## Governance (agent-ops — see [GOVERNANCE.md](GOVERNANCE.md))
- **Trigger:** cron — weekly Monday 6:30 AM (documented above). Manual: "run my numbers".
- **STATE:** `<home>/_state/ceo-dashboard.STATE.md`. Read first (last margin/pace,
  open A/R flags); write last (margin, pace, A/R 91+, tokens, cost).
- **Writer ≠ checker — hard gate: `No-Fabrication Gate`.** Every number traces to a QBO MCP
  report saved in `_data/` (`pl.json`, `ar.json`). Missing or auth-lapsed pull → **stop,
  never infer a number.**
- **Stop condition (machine-checkable):** dashboard `.md` written **AND both `pl.json` +
  `ar.json` parsed** (top-level keys present).
- **Iteration ceiling:** 1 pass/fire · retry ≤3 · 20 tool-calls hard cap.
- **Autonomy: L1 (Propose).** Read-only — **never writes to QuickBooks.** `_data/*.json`
  stays local + gitignored.
- **Found-something → inbox** (lead the summary with anything RED). **Found-nothing →
  silent archive** (rare here; keep prior dashboard on a failed pull).
- **Shell allowlist:** `python3 scripts/build_dashboard.py …` (+ `--selftest`); no network.
- **Parallel:** N/A — sequential.
- **Open box:** log tokens/iteration for 3–5 runs into STATE.
