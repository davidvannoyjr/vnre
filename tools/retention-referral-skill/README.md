# vnre-retention-referral — Stage 08 (Retention & Referral)

Turns the idle VNRE database (3,000+ COI) and sold history (1,450+ closings) into a steady
stream of repeat-and-referral touches — the **50% repeat/referral business** the VNRE plan
names as a key thrust, and the cheapest GCI in the business.

It's the first aiDrVN **Stage 08** module: prove it inside VNRE, then it becomes a sellable
piece of the productized offering.

## What it does

Each run scans past clients + sphere and flags **eight** "moments," each with a drafted
message in DVN's voice (approval-gated — nothing sends automatically):

| Moment | Trigger | Data source |
|---|---|---|
| 🔥 Active Move | property-view / website activity ≤ 45 days | FUB events |
| 💰 Equity Update | est. value gain ≥ $50k since purchase | deal price + appreciation |
| 🏡 Home Anniversary | within 14 days of a closing anniversary (milestone-weighted) | deal close date |
| 📦 Move-Window | owned 7–11 years | deal close date |
| 💵 Refi Touch | mortgage rate ≥ market + 0.75% (lender MSA) | custom field |
| 🎂 Birthday | birthday within 10 days | custom field |
| 🔁 Referral Ask | past client, no contact in 180+ days | comms |
| 👋 Re-engage Sphere | COI cold 365+ days | comms |

Score = moment weight × tier (past client > COI) × **CLV boost**. Anyone contacted in the
last 30 days is suppressed so you never over-touch.

## Files

```
retention-referral-skill/
├── SKILL.md                       # installable skill (frontmatter + full logic)
├── README.md                      # this file
├── PULL_SPEC.md                   # FUB field contract + what to confirm
├── ENRICHMENTS.md                 # workflow audit, data to add, connector map
├── config.example.json            # copy -> config.json (gitignored)
├── scripts/
│   ├── fub_pull.py                # self-contained FUB REST pull (people+deals+comms+events)
│   └── build_retention_brief.py   # deterministic scoring engine
└── sample/                        # runnable demo inputs
    ├── sample_pull.json
    └── sample_sold.json
```

## Try it (no FUB needed)

```bash
python3 scripts/fub_pull.py --selftest          # verify pull/join logic offline
python3 scripts/build_retention_brief.py \
  --pull sample/sample_pull.json --sold sample/sample_sold.json \
  --state /tmp/state.json --out-md /tmp/brief.md --today 2026-06-13
cat /tmp/brief.md
```

## Live setup (per device)

1. Install the skill: open `SKILL.md` (zipped as `vnre-retention-referral.skill`) in Claude
   desktop → **Save skill**.
2. Copy `config.example.json` → `config.json`, set your segment labels + key path/headers.
3. Pull: `FUB_API_KEY=… python3 scripts/fub_pull.py --config config.json --out
   _data/retention-pull-$(date +%F).json` (runs anywhere with network + key — no MCP helper
   required). In-session, the `fub_*` MCP tools can assemble the same JSON.
4. Point `--sold` at `04 Tools/plp-presentation-builder/vnre_sold_history.json`.
5. Schedule a Cowork task `retention-referral` weekly (Mon AM), or say "run the retention brief".

## Tuning

All constants are at the top of `build_retention_brief.py` (appreciation, equity threshold,
move-window band, property-view/refi/referral windows, suppression, CLV boost, cap). Edit there.
See **ENRICHMENTS.md** for the higher-accuracy upgrades (per-ZIP appreciation, real AVM,
QuickBooks→FUB lifetime value, loop-closure write-back).

> Appreciation defaults to 5%/yr as a conservative KC-metro placeholder — set it to your own
> number, or wire in per-ZIP / AVM data (ENRICHMENTS §4) for defensible equity figures.
