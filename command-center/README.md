# VNRE Operations Command Center

One screen that runs the whole brokerage: the financials, the listing funnel, the
pipeline, the database, the EOS scorecard, and every system — wired to live data,
not a mockup. Open `index.html` and you see Van Noy Real Estate's actual numbers.

> **Ship-to-team:** `index.html` is fully self-contained. Email it, drop it in
> Drive, or host it — it works by double-click, offline, on any browser. No login,
> no server, no install. The latest data snapshot is embedded inside the file.

---

## What it shows (7 tabs)

| Tab | Runs on | Highlights |
|---|---|---|
| **Pulse** | everything | Income & profit vs the 2026 plan, listing-appt pace, A/R at risk, 10-yr target, auto-generated alerts |
| **Money** | QuickBooks (live) | P&L Jan 1→today, income mix, top expenses, A/R aging + collections, balance sheet |
| **Listings** | Listing Appts tracker | Appts set/held/taken funnel, monthly trend vs goal, lead-source mix, conversion math |
| **Pipeline** | Commercial Pipeline tracker | Active commercial deals + residential listing status |
| **Database** | Follow Up Boss | 3,000+ COI, A/B/C tier cadence, the #1 growth lever |
| **Team & EOS** | EOS System | Weekly scorecard measurables + goals, accountability chart, open seats |
| **Systems** | — | Tech stack health + the aiDrVN 9-stage automation suite + standing schedules |

The top **alert strip** is generated automatically from the data: 91+ day A/R,
margin gap, prospecting pace, and open seats all surface themselves.

---

## How it's built (the "Coefficient layer")

```
 LIVE SOURCES                    CONNECTOR (build.py)            DELIVERABLE
 ───────────                     ────────────────────           ───────────
 QuickBooks  (P&L, A/R, BS) ───▶ transform_pl / _ar / _balance ─┐
 Listing Appts tracker      ───▶ (edited in snapshot.json)      ├─▶ data/snapshot.json ─▶ index.html
 Pipeline / EOS / FUB       ───▶ (edited in snapshot.json)      ┘    (validate)         (inject between markers)
```

- **`data/snapshot.json`** — the single source of truth for what the dashboard shows.
  Raw facts + targets; all formatting, pace, and red/amber/green logic happen in the
  browser at render time.
- **`index.html`** — the dashboard. The snapshot is embedded between
  `/*VNRE_SNAPSHOT_START*/` and `/*VNRE_SNAPSHOT_END*/` so the file is portable.
- **`build.py`** — validates the snapshot and injects it; also transforms the raw
  QuickBooks MCP JSON into the `finance` block. Pure stdlib, deterministic,
  `--selftest` runs offline.

---

## Refreshing the data

### Weekly — financials (from the QuickBooks MCP, 2 minutes)
Pull the three reports and save them to `_data/` (gitignored — real financials never
hit the repo):

| Save to | MCP tool |
|---|---|
| `_data/pl.json` | `profit_loss_quickbooks_account(periodStart="2026-01-01")` |
| `_data/ar.json` | `qbo_accounting_get_ar_aging_summary()` |
| `_data/bs.json` | `qbo_accounting_get_balance_sheet(start_date=end_date=today)` |

Then:
```bash
python3 build.py --refresh-financials --pl _data/pl.json --ar _data/ar.json --balance _data/bs.json --asof 2026-06-22
```
This rewrites the `finance` block of `snapshot.json` and re-embeds it in `index.html`.

### Weekly — operations (the trackers)
The Google Drive trackers are the source of truth for the non-financial blocks. Update
the matching fields in `data/snapshot.json`, then run:
```bash
python3 build.py        # validate + inject
```

### Connector map — which field comes from where

| snapshot block | Source | Refresh |
|---|---|---|
| `finance.pl / incomeMix / expenseTop` | QuickBooks P&L | `--refresh-financials --pl` |
| `finance.ar` | QuickBooks A/R aging | `--refresh-financials --ar` |
| `finance.balance` | QuickBooks Balance Sheet | `--refresh-financials --balance` |
| `funnel.*` | `2026 Listing Appointments Tracking.xlsx` | edit snapshot.json |
| `pipeline.deals` | `Pipeline_Tracker.xlsx` (commercial) | edit snapshot.json |
| `pipeline.residentialListingStatus` | Listing Appts tracker | edit snapshot.json |
| `database.*` | Follow Up Boss | edit snapshot.json |
| `eos.*` | `VNRE_EOS_System.xlsx` | edit snapshot.json |
| `systems.*` | this manual | edit snapshot.json |

> **Roadmap (full auto-refresh):** the `funnel`, `pipeline`, and `eos` blocks can be
> parsed straight from CSV exports of the trackers, and the database block from a
> Follow Up Boss MCP pull — both drop into `build.py` next to the QuickBooks
> transforms. Today those blocks are updated in `snapshot.json` directly; the
> financial pull is already fully automated.

---

## Snapshot at build time (2026-06-15)

Real figures embedded in this build, straight from the live systems:

- **Income YTD** $446,501 · **Net** $82,463 · **Margin** 18.5% (vs 50% plan target)
- **Cash** $25,888 · **Working capital** $18,957 · **Current ratio** 1.81
- **A/R** $16,050 — **$11,500 is 91+ days** (All Western Mortgage — collect now)
- **Listing appts** 41 set / 26 held / 9 taken YTD (goal 25/mo)
- **Open seats** Marketing Manager, Buyer Agent

---

## Files

```
command-center/
├── index.html          # the dashboard — ship this file
├── data/snapshot.json  # source of truth for the dashboard
├── build.py            # validate / inject / refresh-from-QuickBooks  (python3 build.py --selftest)
├── _data/              # raw QuickBooks pulls — gitignored, never committed
└── README.md
```

Verify the build any time: `python3 build.py --selftest`.
