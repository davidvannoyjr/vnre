---
name: vnre-ceo-dashboard
description: Build DVN's CEO P&L dashboard — QuickBooks actuals vs the 2026 plan, annualized pace, the 50%-margin guard, and an A/R collections flag, each with a red/amber/green status and a recommended action. Use whenever DVN says "CEO dashboard", "run my numbers", "where am I vs plan", "P&L snapshot", "how's my margin", "what's overdue", or when the weekly dashboard task fires.
---

# VNRE CEO Dashboard (aiDrVN Stage 07)

One screen, every Monday: are we on track to the 2026 plan, is the 50% margin holding, and
what needs attention this week. Read-only — pulls from QuickBooks, decides nothing for you.

## Architecture

QuickBooks data comes through the **QuickBooks MCP tools** (already connected — no extra
setup). The renderer is offline and deterministic.

1. Pull from QBO MCP: `profit_loss_quickbooks_account` (YTD), `qbo_accounting_get_ar_aging_summary`,
   optionally `sales_by_customer_summary` (partner mix — see the clv-sync skill).
2. Save each report's JSON to `_data/` (the P&L is large — write it to a file, don't inline it).
3. `scripts/build_dashboard.py --pl … --ar … --plan plan.json --out "<home>/YYYY-MM-DD CEO Dashboard.md"`.
4. Present the dashboard; act on the flags.

## Steps
```bash
# 1. P&L year-to-date  (MCP: profit_loss_quickbooks_account periodStart=YYYY-01-01)
#    A/R aging          (MCP: qbo_accounting_get_ar_aging_summary)
#    -> save each to _data/pl.json and _data/ar.json
python3 scripts/build_dashboard.py \
  --pl _data/pl.json --ar _data/ar.json --plan plan.json \
  --out "<home>/$(date +%F) CEO Dashboard.md"
```

The renderer reads only top-level P&L keys (`totalIncome`, `totalExpenses`, `grossProfit`,
`netIncome`, `periodStart/End`) and the A/R `summary` block, so the large raw report is fine
to pass by path. It computes: annualized pace vs plan, net margin vs the 50% target (with the
dollar gap), and A/R risk (91+ day bucket → named collections action).

## Plan targets
`plan.json` holds the 2026 numbers (revenue $1.25M, opex $537.5k, net $625k, margin 50% — from
the Strategic Business Plan). Copy `plan.example.json` → `plan.json`; refresh each January.

## Cadence & safety
- **Weekly** (Mon AM) via a Cowork task `ceo-dashboard`, or "run my numbers". Monthly close is
  the one that matters most.
- Read-only: it never writes to QuickBooks. Keep the pulled `_data/*.json` out of git
  (`_data/` is gitignored) — real financials stay local.

## Verify offline
`python3 scripts/build_dashboard.py --selftest` (renders from fixtures, no network).

## Roadmap
- Add a **GCI / transactions** row once unit counts are wired (FUB closed deals or the sold log)
  — pace toward 75 listings / 50 buyers, not just dollars.
- Trend the monthly `monthlyBreakdown` for a sparkline of margin over the year.
- Cash position from the balance sheet (`qbo_accounting_get_balance_sheet`) → runway line.
