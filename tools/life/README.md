# tools/life — DVN Life Design pipeline

Phase 1 of the Life Tracking System. Pulls every connected source into one warehouse
(`life.*` schema in Supabase/Postgres); the mobile dashboard and the 5 AM Life Brief read
from the warehouse. Mirrors the `tools/vnre/` skill pattern.

Full architecture: [`../../claude/01-projects/Life Tracking System/Life Tracking System Design.md`](../../claude/01-projects/Life%20Tracking%20System/Life%20Tracking%20System%20Design.md)

## Layout
```
tools/life/
  schema.sql                 warehouse DDL (run once in Supabase)
  config.example.json        per-source auth + endpoints (copy → config.json, never commit)
  warehouse-snapshot.json    first REAL snapshot, captured 2026-06-14 (the proof)
  ingest/
    runner.py                orchestrates all source adapters, writes to the warehouse
    sources/
      quickbooks.py          LIVE — P&L, balance sheet, A/R aging  → finance_biz_*
      function_health.py     LIVE — biomarker in/out-of-range       → labs_*
      google_calendar.py     LIVE — events → time categories        → calendar_events
      credit_karma.py        LIVE — bands + factor standings         → credit_factors
      granola.py             LIVE — call/meeting counts + scores     → (call quality)
      follow_up_boss.py      PENDING — calls/contacts/appts          → prospecting_daily
      whoop.py               PENDING — recovery/sleep/strain         → body_daily
      withings.py            PENDING — weight/BF/BP                   → body_measurements
      macro_log.py           PENDING — macros (Claude skill writes)  → diet_entries
```

## Status (2026-06-14 live check)
| Source | State | Lands in |
|---|---|---|
| QuickBooks | 🟢 live | `finance_biz_snapshot`, `finance_biz_monthly` |
| Function Health | 🟢 live | `labs_summary` |
| Credit Karma | 🟢 live (bands only) | `credit_factors` |
| Google Calendar | 🟢 live | `calendar_events` |
| Granola | 🟢 live | call-quality metrics |
| **Follow Up Boss** | 🔴 **pending** — not connected in web session | `prospecting_daily` |
| Whoop / Withings / macro-log / Monarch | ⚪ pending device / build / decision | body, diet, personal $ |

> **#1 Phase-1.5 task:** connect Follow Up Boss so calls / contacts / appts set+kept stop
> being manual-only. Until then the dashboard's Daily Log feeds `prospecting_daily` by hand.

## Runbook
1. `supabase` project → run `schema.sql`.
2. `cp config.example.json config.json` and fill auth (QBO OAuth, Google service acct, Whoop/Withings/Function tokens).
3. `python ingest/runner.py --once` to backfill, or schedule via n8n (cadence below).
4. Dashboard points at the Supabase REST endpoint; until deployed it reads `warehouse-snapshot.json`.

## Cadence (n8n)
- Hourly (business hrs): Follow Up Boss, calendar
- Morning 5:00: Whoop (overnight), QuickBooks, Function Health, → Life Brief
- Weekly Mon: Credit Karma, Monarch, coaching scorecards

## Data-quality flags captured this run
- Balance-sheet Net Income ($285,929) ≠ P&L Net Income ($82,463). Reconcile basis before trusting a headline net.
- Monthly P&L "expenses" include COGS/commission payouts; YTD headline opex excludes them.
