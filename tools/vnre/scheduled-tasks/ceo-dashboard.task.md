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
