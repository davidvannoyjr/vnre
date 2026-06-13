# vnre-retention-referral — Stage 08 (Retention & Referral)

Turns the idle VNRE database (3,000+ COI) and sold history (1,450+ closings) into a steady
stream of repeat-and-referral touches — the **50% repeat/referral business** the VNRE plan
names as a key thrust, and the cheapest GCI in the business.

It's the first aiDrVN **Stage 08** module: prove it inside VNRE, then it becomes a sellable
piece of the productized offering.

## What it does

Each run scans past clients + sphere and flags five "moments," each with a drafted message
in DVN's voice (approval-gated — nothing sends automatically):

| Moment | Trigger |
|---|---|
| 💰 Equity Update | est. value gain ≥ $50k since purchase (price × appreciation^years) |
| 🏡 Home Anniversary | within 14 days of a closing anniversary (extra weight on 1/3/5/7/10/15/20-yr) |
| 📦 Move-Window | owned 7–11 years (typical move-likelihood band) |
| 🔁 Referral Ask | past client, no contact in 180+ days |
| 👋 Re-engage Sphere | COI contact cold 365+ days |

Anyone contacted in the last 30 days is suppressed so you never over-touch.

## Files

```
retention-referral-skill/
├── SKILL.md                       # installable skill (frontmatter + full logic)
├── README.md                      # this file
├── scripts/build_retention_brief.py
└── sample/                        # runnable demo inputs
    ├── sample_pull.json
    └── sample_sold.json
```

## Try it (no FUB needed)

```bash
python3 scripts/build_retention_brief.py \
  --pull sample/sample_pull.json --sold sample/sample_sold.json \
  --state /tmp/state.json --out-md /tmp/brief.md --today 2026-06-13
cat /tmp/brief.md
```

## Live setup (per device)

1. Install the skill: open `SKILL.md` (zipped as `vnre-retention-referral.skill`) in Claude
   desktop → **Save skill**.
2. Requires the `followupboss` MCP server connected (same setup as the lead brief:
   `npm install` in `04 Tools/followupboss-mcp`, quit Claude, run `fix-claude-config.sh`,
   reopen).
3. Point `--sold` at `04 Tools/plp-presentation-builder/vnre_sold_history.json`.
4. Schedule a Cowork task `retention-referral` weekly (Mon AM), or say "run the retention brief".

## Tuning

All constants are at the top of `build_retention_brief.py` (appreciation rate, equity
threshold, move-window band, referral/cold-sphere days, suppression window, cap). Edit there.

> Appreciation defaults to 5%/yr as a conservative KC-metro placeholder — set it to your
> own number, or wire in real per-ZIP appreciation later for sharper equity estimates.
