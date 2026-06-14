-- DVN Life Design — warehouse schema (Postgres / Supabase)
-- Phase 1. Everything every source writes lands here; the dashboard + Life Brief read from here.
-- Two walled-off finance domains (biz vs personal) per DVN's decision — no combined net-worth roll-up.

create schema if not exists life;

-- ── ingestion audit ────────────────────────────────────────────────
create table if not exists life.source_runs (
  id           bigserial primary key,
  source       text not null,                 -- 'quickbooks','google_calendar','function_health',...
  started_at   timestamptz not null default now(),
  finished_at  timestamptz,
  status       text not null default 'running',-- running|ok|error
  rows_written int default 0,
  note         text
);

-- ── business finance (QuickBooks) ──────────────────────────────────
create table if not exists life.finance_biz_snapshot (
  as_of            date primary key,
  revenue_ytd      numeric,
  gross_profit_ytd numeric,
  opex_ytd         numeric,
  net_income_ytd   numeric,
  margin           numeric,                    -- net_income / revenue
  cash             numeric,
  accounts_receivable numeric,
  ar_over_30       numeric,
  equity           numeric,
  liabilities      numeric,
  current_ratio    numeric,
  flags            jsonb default '[]'
);
create table if not exists life.finance_biz_monthly (
  month       date,                            -- first of month
  revenue     numeric,
  net_income  numeric,
  expenses    numeric,
  primary key (month)
);

-- ── personal finance (Monarch — deferred) + credit (Credit Karma) ──
create table if not exists life.credit_factors (
  as_of    date,
  band     text,                               -- bands only; Credit Karma does not expose the number
  model    text,
  factor   text,
  impact   text,                               -- HIGH|MEDIUM|LOW
  standing text,                               -- EXCELLENT|GOOD|FAIR|NEEDS_WORK
  primary key (as_of, factor)
);
create table if not exists life.finance_personal_snapshot (  -- pending Monarch/Plaid
  as_of      date primary key,
  net_worth  numeric,
  cash       numeric,
  investments numeric,
  debt       numeric,
  spend_mtd  numeric,
  budget_mtd numeric
);

-- ── body / labs (Whoop, Withings, Function Health) ─────────────────
create table if not exists life.body_daily (              -- Whoop (pending device)
  day          date primary key,
  recovery     int,
  hrv          numeric,
  resting_hr   numeric,
  strain       numeric,
  sleep_hours  numeric,
  sleep_perf   int,
  sleep_consistency int
);
create table if not exists life.body_measurements (      -- Withings (pending device)
  day        date primary key,
  weight_lb  numeric,
  body_fat   numeric,
  bp_sys     int,
  bp_dia     int
);
create table if not exists life.labs_summary (           -- Function Health (LIVE)
  as_of        date primary key,
  total        int,
  in_range     int,
  out_of_range int,
  provider     text default 'Function Health'
);
create table if not exists life.labs_biomarkers (
  as_of    date,
  name     text,
  value    numeric,
  unit     text,
  in_range boolean,
  category text,
  primary key (as_of, name)
);

-- ── diet (macro-log skill — conversational) ────────────────────────
create table if not exists life.diet_entries (
  id        bigserial primary key,
  ts        timestamptz not null default now(),
  item      text,
  calories  numeric,
  protein_g numeric,
  carbs_g   numeric,
  fat_g     numeric,
  source    text default 'macro-log'           -- claude estimate vs confirmed
);

-- ── work: prospecting + production + calendar (FUB, Mojo, Calendar) ─
create table if not exists life.prospecting_daily (
  day         date primary key,
  calls       int default 0,
  contacts    int default 0,
  hours       numeric default 0,
  appts_set   int default 0,
  appts_kept  int default 0,
  source      text default 'manual'            -- manual | fub | blended
);
create table if not exists life.production_snapshot (
  as_of           date primary key,
  listings_active int,
  listings_pending int,
  closed_ytd      int,
  listings_taken_ytd int,
  gci_ytd         numeric,
  pipeline        numeric
);
create table if not exists life.calendar_events (
  id          text primary key,
  starts_at   timestamptz,
  ends_at     timestamptz,
  summary     text,
  event_type  text,
  category    text                              -- prospecting|appointment|admin|workout|personal
);

-- ── coaching ───────────────────────────────────────────────────────
create table if not exists life.coaching_snapshot (
  as_of   date primary key,
  active  int,
  mrr     numeric,
  churn   int,
  lowest_pillar text
);

-- ── generic daily rollup — powers the trend + forecast views ───────
-- one row per (day, domain, metric); the dashboard charts read straight off this.
create table if not exists life.metrics_daily (
  day     date,
  domain  text,                                 -- biz|today|body|money
  metric  text,
  value   numeric,
  target  numeric,
  primary key (day, domain, metric)
);
create index if not exists metrics_daily_lookup on life.metrics_daily (domain, metric, day);
