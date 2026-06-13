# vnre-ceo-dashboard — Stage 07 (Finance)

A one-screen weekly CEO view: QuickBooks actuals vs the 2026 plan, the **50%-margin guard**,
revenue pace, and an A/R collections flag — each with a 🟢/🟡/🔴 status and an action.

Read-only. QuickBooks MCP is already connected, so there's nothing to wire — it just reads.

## What it shows

- **Scorecard** — Revenue, Operating Expenses, Net Profit, Net Margin: YTD actual, annualized
  pace, 2026 plan, % to plan, RAG flag.
- **Margin guard** — net margin vs the 50% target, with the **dollar profit gap** at current revenue.
- **A/R & collections** — receivables, overdue %, and the 91+ day bucket called out by customer.
- **This week's actions** — the 2–3 things to act on.

## Files
```
ceo-dashboard-skill/
├── SKILL.md, README.md, plan.example.json
├── scripts/build_dashboard.py
└── sample/  (sample_pl.json, sample_ar.json — synthetic)
```

## Try it (no network)
```bash
python3 scripts/build_dashboard.py --selftest
python3 scripts/build_dashboard.py --pl sample/sample_pl.json --ar sample/sample_ar.json \
  --plan plan.example.json --out /tmp/dash.md && cat /tmp/dash.md
```

## Live
1. Copy `plan.example.json` → `plan.json` (already holds your 2026 targets; refresh yearly).
2. Pull P&L (`profit_loss_quickbooks_account`, periodStart = Jan 1) and A/R aging from the
   QuickBooks MCP; save each report's JSON to `_data/`.
3. Run `build_dashboard.py` → drop the markdown in your `Follow Up Boss Pipeline` / finance folder.
4. Schedule a Cowork task `ceo-dashboard` weekly (Mon AM), or say "run my numbers".

> Real financials never need to enter git — `_data/` is gitignored; only synthetic samples
> are committed. The renderer reads top-level P&L keys + the A/R summary, so a large raw QBO
> report can be passed straight through by file path.
