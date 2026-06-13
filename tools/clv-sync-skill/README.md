# vnre-clv-sync — Client Lifetime Value + Partner Value

Makes every Database & COI and CEO decision **profit-weighted**.

- **Client CLV → FUB:** sums each past client's commission across all closings and writes it
  to their FUB `Lifetime Value` field. The Database & COI engine CLV-weights its scoring, so the
  most profitable relationships surface first. Serves the **50% margin** target.
- **Partner Value brief:** turns QuickBooks sales-by-customer (your lenders/title/insurance/
  co-op partners) into a ranked nurture brief with concentration risk + MSA actions. Serves
  the **$25k Vendor MSA** line.

## The key finding

QuickBooks "customers" at VNRE are **B2B partners, not home clients** (All Western Mortgage,
Bison State Bank, …). So client CLV is built from the **closing record**
(`vnre_sold_history.json` + FUB won deals), not QBO. QBO is repurposed for partner value.

## Files
```
clv-sync-skill/
├── SKILL.md, README.md, config.example.json
├── scripts/build_clv.py       # closings -> per-client Lifetime Value plan
├── scripts/fub_push.py        # write to FUB (DRY-RUN default; --commit to apply)
├── scripts/partner_value.py   # QBO -> partner-nurture brief
└── sample/                    # synthetic demo data
```

## Try it (no network)
```bash
python3 scripts/build_clv.py --selftest
python3 scripts/fub_push.py  --selftest
python3 scripts/build_clv.py --sold sample/sample_sold.json --people sample/sample_people.json --out /tmp/clv.json
python3 scripts/fub_push.py  --plan /tmp/clv.json          # dry-run, writes nothing
python3 scripts/partner_value.py --qbo sample/sample_qbo.json --out /tmp/partners.md
```

## Live
1. Copy `config.example.json` → `config.json`; set key path, X-System, and the exact FUB
   custom-field name.
2. `build_clv.py` with your real `vnre_sold_history.json` + a `fub_pull.py` people dump.
3. `fub_push.py --plan … ` (dry-run) → review → add `--commit` to write.
4. Run **quarterly** and **before each Database & COI run**. Idempotent.

> Commission defaults (2.5% / $12k listing / $5.5k buyer) come from the 2026 plan — set your
> real numbers in `config.json`. If `vnre_sold_history.json` carries actual commission per
> closing, that's used directly and the rates are ignored.
