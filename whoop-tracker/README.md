# WHOOP Superuser Tracker → Spreadsheet Dashboard

A production-grade personal biometric pipeline. It pulls from the official
WHOOP API (OAuth 2.0), normalizes the data into SQLite, and writes a
self-contained, dashboard-grade `whoop_dashboard.xlsx` you open daily. Every
analytical number in the workbook is a **live Excel formula**, so the workbook
recalculates when the raw tabs are refreshed.

> **API version note.** The original spec referenced WHOOP **v1**. WHOOP fully
> deprecated v1 (Oct 2025); **v2** is the only live version, so this project
> targets v2. The practical differences: sleep/workout ids are now **UUID
> strings** (cycle ids stay integers), score fields are nested under a `score`
> object with a `score_state`, and pagination returns `next_token`. These are
> reflected in `config.py` and `src/store.py`.

---

## Quick start

```bash
cd whoop-tracker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # then fill in the four values (see below)

python -m src.cli auth                      # one-time OAuth, stores encrypted tokens
python -m src.cli backfill --since 2023-01-01   # full history (omit --since for all)
python -m src.cli all                       # daily command: sync + build
open whoop_dashboard.xlsx                   # macOS; use start/xdg-open elsewhere
```

A convenience wrapper is optional — everything is `python -m src.cli <cmd>`.

### `.env` values

| Variable | Meaning |
| --- | --- |
| `WHOOP_CLIENT_ID` | OAuth client id from your WHOOP developer app |
| `WHOOP_CLIENT_SECRET` | OAuth client secret (also used to verify webhook signatures) |
| `WHOOP_REDIRECT_URI` | Must match a redirect URI on the app; default `http://localhost:8080/callback` |
| `WHOOP_TOKEN_KEY` | Passphrase that derives the Fernet key encrypting your token file |

Create an app at <https://developer.whoop.com/> and request these scopes:
`read:profile read:body_measurement read:cycles read:recovery read:sleep
read:workout offline`. The `offline` scope is required to receive a refresh
token (otherwise you must re-auth whenever the access token expires).

---

## Commands

| Command | What it does |
| --- | --- |
| `whoop auth` | Runs the OAuth Authorization Code flow; stores encrypted tokens. |
| `whoop backfill --since YYYY-MM-DD` | Full historical pull (default: account start). |
| `whoop sync` | Incremental delta pull using the per-resource watermark. |
| `whoop build` | Regenerates `whoop_dashboard.xlsx` from the DB. |
| `whoop all` | `sync` then `build` — the daily command. |
| `whoop webhook` | Runs the push receiver (see *Webhooks* below). |

Add `--quiet` to log only to `data/whoop.log`. Ingestion is **idempotent**
(upsert on the WHOOP record id), so re-running never duplicates rows.

---

## The cycle → calendar-day rule

WHOOP's core unit is the **physiological cycle**, which is *not* a calendar
day. This pipeline assigns each cycle to the calendar day of the **local date
of its `start`** (`cycle.start` shifted by `cycle.timezone_offset`). Recovery,
sleep and cycle are joined on the WHOOP **id linkage**
(`recovery.cycle_id → cycle.id`, `recovery.sleep_id → sleep.id`), never on date
proximity. Workouts are attached to the local date of their own start. The rule
is restated on the workbook's **Config** tab.

---

## The workbook

Opens on a **Dashboard** cockpit tab; the rest are the working tabs.

- **Dashboard** — KPI band (Recovery, HRV, RHR, Day Strain, Hours Slept, Sleep
  Performance) with traffic-light fills driven by the Config thresholds, each
  with its 30-day baseline and z-score; 30-day native sparklines; a "Flags
  today" area (|z| ≥ 1.5); and a "What's driving recovery" top-5 correlation
  table. Everything is a formula referencing the data tabs.
- **Daily** — the joined one-row-per-day analytical workhorse (newest on top),
  with conditional colour scales. This is the source the analytics tabs read.
- **Recovery / Sleep / Strain_Workouts** — resource detail with typed columns
  and derived hours/calories/°F as formulas.
- **Rolling** — 7d/30d means & SDs, calibrating-excluded baselines, and
  z-scores per metric (all formulas referencing Daily).
- **Correlations** — Pearson `=CORREL()` of prior-day drivers vs next-morning
  recovery & HRV (with `n`), plus a strain-quartile → next-day-recovery table.
- **Interventions** — your editable n-of-1 experiment log (mirrors
  `data/interventions.csv`) with a category dropdown. Each distinct `item`
  becomes a 0/1 daily flag and a correlation predictor.
- **Config** — thresholds (blue = inputs you can retune), the cycle-day rule,
  units, and refresh instructions.
- **Raw_\*** — hidden audit tabs holding the raw API JSON.

The build sets `fullCalcOnLoad`, runs a LibreOffice headless **recalc** pass to
populate cached values, then **scans every cell for error strings and fails the
build if any are found**. All divisions/lookups are `IFERROR`-guarded, so the
workbook opens with zero `#REF!/#DIV0!/#VALUE!/#N/A/#NAME?` errors.

### Interventions / experiment engine

`data/interventions.csv` is seeded with a header and example rows on first run:

```
date, category, item, dose, notes
```

Categories: `supplement, nutrition, training, sleep_protocol, substance,
environment`. Edit it, re-run `whoop build`, and each item's effect on
next-morning recovery and HRV shows up on the Correlations tab.

---

## Quota, rate limits & efficiency

WHOOP enforces app-wide limits of **100 requests/minute** and **10,000/day**.
The client is built to stay well under them:

- **Proactive pacing** — `src/ratelimit.py` keeps sliding-window counters for
  both windows (paced to 90% of the ceiling) and blocks before a breach.
- **Header-aware** — every response's `X-RateLimit-Remaining` / `-Reset`
  headers feed back into the limiter.
- **Backoff with jitter** — 429/5xx honor `Retry-After`, otherwise exponential
  backoff with full jitter to avoid thundering-herd retries.
- **Cheap I/O** — pagination at `limit=25`, incremental watermarks (only fetch
  deltas after the first backfill), idempotent upserts as the cache, and token
  refresh only when the access token is actually near expiry.

### Prefer webhooks over polling

Register a webhook in your WHOOP app and run the receiver:

```bash
python -m src.cli webhook --port 8099   # put HTTPS (proxy/tunnel) in front
```

It verifies the `X-WHOOP-Signature` HMAC, then fetches **only the one updated
record** and upserts it — far cheaper than polling. Rebuild the workbook on a
light cadence (or after a batch of events).

### Adaptive polling (if you can't use webhooks)

Recovery posts once per night, so poll it **once each morning** ~1h after your
typical wake. Strain accrues during the day; poll it at most every **30–60
min** while you're awake, and not at all overnight. The watermark + upsert make
any cadence safe.

### SaaS scaling note

The limiter and webhook verify/dispatch functions are framework-agnostic and
single-process today. For multi-tenant scale, swap the in-memory deques for a
shared per-app Redis token bucket and move the verify/dispatch into your async
framework — the call sites don't change.

---

## Scheduling (run `whoop all` every morning)

Run ~1 hour after your typical wake so the prior night's recovery has posted.

**cron** (Linux), 7:30am daily:

```cron
30 7 * * * cd /path/to/whoop-tracker && /path/to/whoop-tracker/.venv/bin/python -m src.cli all --quiet >> data/cron.log 2>&1
```

**macOS launchd** — `~/Library/LaunchAgents/com.user.whoop.plist`, then
`launchctl load ~/Library/LaunchAgents/com.user.whoop.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.user.whoop</string>
  <key>ProgramArguments</key>
  <array>
    <string>/path/to/whoop-tracker/.venv/bin/python</string>
    <string>-m</string><string>src.cli</string><string>all</string><string>--quiet</string>
  </array>
  <key>WorkingDirectory</key><string>/path/to/whoop-tracker</string>
  <key>StartCalendarInterval</key>
  <dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>30</integer></dict>
  <key>StandardErrorPath</key><string>/path/to/whoop-tracker/data/launchd.log</string>
  <key>StandardOutPath</key><string>/path/to/whoop-tracker/data/launchd.log</string>
</dict>
</plist>
```

**Windows Task Scheduler**:

```powershell
schtasks /Create /SC DAILY /ST 07:30 /TN "WHOOP Daily" ^
  /TR "cmd /c cd /d C:\path\to\whoop-tracker && .venv\Scripts\python -m src.cli all --quiet"
```

---

## Tests

```bash
python -m pytest -q
```

Covers cycle→day mapping across a timezone boundary, sleep-debt floor, unit
conversions, calibrating-day exclusion, z-score & correlation math (including
the `n<5` guard), the rate limiter, webhook signature/dispatch, and a full
workbook build that asserts **zero error strings** and numeric Dashboard KPIs.

---

## Troubleshooting

- **`WHOOP_TOKEN_KEY is not set`** — fill it in `.env`; it encrypts your tokens.
- **`Could not decrypt token file`** — `WHOOP_TOKEN_KEY` changed; delete
  `data/whoop_tokens.enc` and re-run `whoop auth`.
- **OAuth callback times out** — `WHOOP_REDIRECT_URI` must exactly match the app
  setting, and the local port must be free.
- **KPIs show formulas, not numbers, in a non-Excel viewer** — the workbook
  carries `fullCalcOnLoad`; Excel and current LibreOffice recalc on open. The
  build also attempts a headless LibreOffice recalc to pre-cache values; if your
  LibreOffice can't convert (some headless installs can't), values still appear
  the moment you open the file. The error-scan still guarantees no error cells.
- **No data in the workbook** — run `whoop backfill` first, then `whoop all`.

## Security

- Tokens are encrypted at rest with a Fernet key derived (PBKDF2) from
  `WHOOP_TOKEN_KEY`. Tokens and the client secret are never logged or printed.
- `.env`, `data/`, `*.xlsx` and token files are gitignored. Nothing secret is
  committed.
