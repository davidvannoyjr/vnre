---
name: vnre-clv-sync
description: Compute each VNRE past client's Lifetime Value from the closing history (Deal Sheets / sold history + FUB won deals), write it back to the Follow Up Boss "Lifetime Value" custom field, and produce a QuickBooks partner-value brief. Use whenever DVN says "sync CLV", "update lifetime value", "client lifetime value", "partner value", "which partners drive my MSA income", or before a retention run that should be profit-weighted.
---

# VNRE CLV Sync + Partner Value

Two outputs, both about putting money behind your attention:

1. **Client Lifetime Value → FUB.** Sum each past client's commission across every closing and
   write it to their FUB `Lifetime Value` custom field. The retention engine then CLV-weights
   its scoring, so your most profitable relationships rise to the top of every brief — directly
   serving the 50% margin target.
2. **Partner Value brief (QuickBooks).** Your QBO "customers" are B2B partners (lenders, title,
   insurance, co-op brokers), not consumer clients — this ranks them, flags concentration, and
   proposes MSA actions for the plan's $25k Vendor MSA line.

## Why CLV comes from closings, not QuickBooks

QBO sales-by-customer is **partner/referral income**, not per-client commission (verified:
the customers are All Western Mortgage, Bison State Bank, etc.). So client CLV is built from
the authoritative closing record — `vnre_sold_history.json` (Deal Sheets, 1,450+ closings,
2009–2026) plus FUB won deals — matched to FUB people and summed. Repeat clients rank highest.

## Files
```
clv-sync-skill/
├── SKILL.md, README.md, config.example.json
├── scripts/
│   ├── build_clv.py       # closings -> per-client Lifetime Value writeback plan
│   ├── fub_push.py        # write Lifetime Value to FUB (DRY-RUN by default; --commit to apply)
│   └── partner_value.py   # QBO sales-by-customer -> partner-nurture brief
└── sample/                # runnable demo (synthetic data)
```

## Steps

### Step 0. One-time — set up the FUB field (do this first)
There's no `Lifetime Value` field in FUB yet, so set it up before any sync:
```bash
python3 scripts/fub_field_setup.py --config config.json            # check what exists
python3 scripts/fub_field_setup.py --config config.json --create   # create the missing fields
```
It creates/verifies `Lifetime Value` (number) plus the other fields the suite uses
(`Mortgage Rate`, `Preferred Channel`, `Opt-Out`), and reports each field's API key
(e.g. `customLifetimeValue`). If your FUB plan only allows custom fields via the admin UI,
it prints the exact click-path instead. Set `config.json → customFieldName = "Lifetime Value"`.

### A. Client CLV
1. **Source the closings.** Use `vnre_sold_history.json` as `--sold`. If it lacks commission,
   the engine derives it: explicit `commission`/`gci` → else `price × rate` → else avg GCI by
   side ($12k listing / $5.5k buyer, from the 2026 plan). Tune in `config.json`.
2. **Source the people.** Use the `fub_pull.py` output (or a `fub_search_people` dump) as
   `--people` — these are the writeback targets.
3. **Build the plan:**
   ```bash
   python3 scripts/build_clv.py --sold vnre_sold_history.json \
     --people retention-pull-YYYY-MM-DD.json --config config.json --out clv-plan.json
   ```
   Review `clv-plan.json`: `writeback` (matched), `unmatchedClients` (past clients not in FUB —
   candidates to add). Spot-check the top names and match confidence.
4. **Dry-run the writeback (writes nothing):**
   ```bash
   python3 scripts/fub_push.py --plan clv-plan.json
   ```
5. **Commit when it looks right:**
   ```bash
   python3 scripts/fub_push.py --plan clv-plan.json --config config.json --commit
   ```
   Touches only the `Lifetime Value` field; never overwrites anything else.

### B. Partner value
```bash
# save the QBO sales-by-customer MCP report to qbo.json, then:
python3 scripts/partner_value.py --qbo qbo.json --out "YYYY Partner Value Brief.md"
```
(Or just ask Claude — the QuickBooks MCP `sales_by_customer_summary` tool is connected.)

## Safety & cadence
- `fub_push.py` is **dry-run by default**; nothing is written without `--commit`.
- The `Lifetime Value` custom field must exist in FUB (Admin → Custom Fields). Confirm its
  exact name and set it in `config.json → customFieldName`.
- Run **quarterly**, and always **before a retention run** so scoring is current. Re-running is
  idempotent (it overwrites the same field with the latest sum).

## Verify offline
`python3 scripts/build_clv.py --selftest` and `python3 scripts/fub_push.py --selftest`.
