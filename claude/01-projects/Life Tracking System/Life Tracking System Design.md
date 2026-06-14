# Life Tracking System — Full Architecture & Build Plan

> One system that keeps a single, always-current picture of DVN's body, sleep, diet,
> work, calls/appointments, business, and money — fed automatically from the apps he
> already runs plus a short list of additions. Mobile-first. Owned data. Premium-but-justified.
>
> **Decisions locked (2026-06-14):** Whoop = primary body spine · dashboard = mobile-first
> PWA · finances = personal + business tracked **separately** (no net-worth roll-up) ·
> spend posture = premium but justified.

---

## 1. The model in one picture

Four layers. Data flows up; the dashboard and the morning brief read down.

```
   ┌─────────────────────────────────────────────────────────────┐
4  │  SURFACE        Mobile-first PWA dashboard  +  5 AM Life Brief │
   │                 Snapshot · 30/90/180-day trends · 6-mo forecast│
   │                 (glance on phone · home-screen install)        │
   ├─────────────────────────────────────────────────────────────┤
3  │  WAREHOUSE      One datastore (Supabase / Postgres)            │
   │                 every metric, timestamped, queryable, owned    │
   ├─────────────────────────────────────────────────────────────┤
2  │  ORCHESTRATION  Scheduled pulls per source (n8n)               │
   │                 normalize → write to warehouse → fire alerts   │
   ├─────────────────────────────────────────────────────────────┤
1  │  SOURCES        Whoop · Withings · MacroFactor · Google Cal/   │
   │                 Gmail/Drive · FUB · Mojo · Upfirst · QBO ·      │
   │                 Monarch · Credit Karma · Granola · Audible      │
   └─────────────────────────────────────────────────────────────┘
```

**Principle:** the dashboard never talks to a source directly. Everything lands in the
warehouse first. That's what makes it always-current, survivable when one app changes its
API, and fast on a phone.

---

## 2. Stack decisions (the spine)

| Layer | Pick | Why this one |
|---|---|---|
| **Warehouse** | **Supabase** (hosted Postgres) | REST + realtime + auth out of the box, scales from free → $25/mo, you own the SQL. The PWA reads it directly. |
| **Orchestration** | **n8n** (self-hosted on a $6/mo VPS) | 400+ connectors, owns your data, one flat cost, visual flows Claude can edit. *No-ops alternative: Make.com if you never want to touch a server.* |
| **Dashboard** | **Next.js PWA on Vercel** | Installs to your home screen like an app, mobile-first responsive, reuses the look you already started in `vannoy_dashboard.html`. Free hobby tier covers it. |
| **Brain / brief** | **Claude (this repo's skill pattern)** | A `life-brief` skill joins the existing 5 AM cadence — reads the warehouse, writes the morning roll-up. Same pattern as `daily-lead-attention`. |

Body spine: **Whoop 5.0** (official API). Secondary: Apple Watch.

---

## 3. Source map — every life domain to a feed

Legend: 🟢 already connected in your Claude environment · 🟡 you own it, needs a bridge · 🔵 add it

### Body & recovery
| Metric | Source | Status |
|---|---|---|
| Recovery %, HRV, resting HR, respiratory rate, skin temp | **Whoop API** | 🔵 add device |
| Day strain, workouts (type, duration, HR zones), steps, active energy | Whoop + Apple Watch | 🔵 / 🟡 |
| Weight, body-fat %, lean mass | **Withings Body smart scale** (API) | 🔵 add (~$100 once) |
| Blood pressure | **Withings BPM Connect** (API) | 🔵 add (~$100 once) — age-appropriate, fully automated |
| Bloodwork / biomarkers (in-range vs out-of-range, trends) | **Function Health** (MCP — confirmed live) | 🟢 already connected |
| *(optional)* glucose / metabolic | Stelo or Lingo CGM | 🔵 optional, 14-day sensors |

### Sleep
| Metric | Source | Status |
|---|---|---|
| Hours, sleep performance %, need vs got, debt, consistency, stages, disturbances | **Whoop API** | 🔵 |

### Diet & macros — conversational logging (no app)
| Metric | Source | Status |
|---|---|---|
| Calories vs target, protein/carb/fat, fiber, water, alcohol, adherence days | **`macro-log` skill** — text or photo a meal to Claude → it estimates macros and writes them to the warehouse | 🔵 build |

> **How it works:** "had 3 eggs, oatmeal, and a banana" or a photo of the plate → Claude
> estimates calories/protein/carb/fat → confirms → writes a row to `diet.entries`. Running
> daily totals roll up against the target. No MacroFactor, no manual app — the chat *is* the
> logger. Macro target is set from the Whoop/Withings weight trend and your goal rate, recomputed weekly.

### Work / business — VNRE
| Metric | Source | Status |
|---|---|---|
| Calls made, talk time, contacts reached | **Mojo dialer** + **Upfirst** voice agents | 🟡 export/API |
| Appointments **set vs kept**, listings taken | **Follow Up Boss** + Google Calendar `LA:` events | 🟢 (FUB skill + Calendar MCP) |
| Active / pending / closed, GCI YTD vs 75-side plan, pipeline value | FUB + your `ceo-dashboard` + `numbers-analyzer` | 🟢 |
| Database coverage (A/B/C touched) | FUB + `database-coi` skill | 🟢 |
| Listings launched (content) | `content-engine` skill | 🟢 |
| Call quality scores | **Granola** → `call-coach` skill | 🟢 |

### Coaching — DVN Coaching
| Metric | Source | Status |
|---|---|---|
| Active clients, MRR, churn | QBO + FUB/roster | 🟢 |
| 22-Point scorecards, session adherence | `DVN-Coaching-Framework.md` scoring | 🟢 |

### Financial (two walled-off views — per your call)
| View | Metric | Source | Status |
|---|---|---|---|
| **Business** | P&L, margin, AR/AP aging, profit, GCI vs plan | **QuickBooks Online** | 🟢 |
| **Personal** | Net worth, accounts, investments, spend vs budget | **Monarch Money** (Plaid) | 🔵 add (~$8/mo) |
| **Personal** | Credit score + the 6 factors | **Credit Karma** | 🟢 |

> Kept structurally separate: two dashboard tabs, two warehouse schemas (`biz.*`, `personal.*`).
> No combined net-worth number unless you flip that switch later.

### Time & calendar structure
| Metric | Source | Status |
|---|---|---|
| Time-block adherence (did the 3-hr prospecting block hold?), meeting load, category mix (prospect / appt / admin / coaching / personal), focus vs reactive | **Google Calendar** (color/keyword tagging) | 🟢 |

### Personal / lifestyle (light-touch)
| Metric | Source | Status |
|---|---|---|
| Books + listening time | **Audible** | 🟢 |
| Ambient music context | Spotify | 🟢 (not a KPI) |
| *(optional)* daily mood / 1-line journal | Claude check-in or Daylio | 🔵 optional |

---

## 4. KPI scoreboard (targets baked in)

These become the dashboard tiles. Targets pulled from your operating manual where they exist.

**Body** — Recovery (green-day %), RHR trend ↓, **4 workouts/wk**, weight → target, BP in range.
**Sleep** — 7.5 h actual · sleep performance >85% · consistency >80% · debt trending to zero.
**Diet** — calories within band · protein target hit · adherence days/wk · weight trend vs goal rate.
**Prospecting** — 150 calls/day · 30 contacts/day · 3 hrs in the chair · block-adherence %.
**Conversion** — appts **set**, appts **kept** (kept-rate is the discipline metric), ~50 contacts→1 appt, ~70% appt→listing.
**Production** — listings taken vs 75/yr pace · active/pending/closed · GCI YTD vs plan · pipeline $.
**Coaching** — clients vs 10–12 cap · MRR · lowest 22-Point scores across the book.
**Business $** — profit margin · AR aging · cash position.
**Personal $** — net worth Δ · spend vs budget · credit score.
**Time** — % of week in revenue-producing blocks vs reactive.

---

## 5. Refresh cadence (what "always up to date" actually means)

| Tier | Sources | When |
|---|---|---|
| **Realtime-ish** | Calendar, email flags, FUB events | webhook / 15-min poll |
| **Hourly** | Mojo/Upfirst call counts, FUB activity | :00 each hour, business hours |
| **Morning (after wake)** | Whoop recovery + last night's sleep, yesterday's macros, Withings weigh-in, QBO snapshot | 5:00 AM → feeds the **Life Brief** |
| **Weekly** | Monarch net worth, CLV, coaching scorecards, time-category roll-up | Monday early |

The 5 AM **Life Brief** is the keystone: one Claude-generated readout — "Recovery 71% green. Slept 7h12m. Down 0.4 lb on trend. 142 calls / 28 contacts yesterday, 2 appts set / 2 kept. GCI pace 96% of plan. Push prospecting today." It rides the cadence you already run for the lead brief.

---

## 6. What to ADD to the stack (your brainstorm ask)

Ranked by payoff for the money.

1. **Whoop 5.0** — body/sleep/recovery spine. *The API is the reason.* (~$20/mo)
2. **Withings Body scale + BPM Connect** — automated weight, body-fat, blood pressure. No manual entry, both have APIs. (~$200 once)
3. **`macro-log` skill** — conversational/photo macro logging straight to the warehouse. No app, no fee.
4. **Monarch Money** *(deferred — your call)* — personal net worth + budget aggregation via Plaid. (~$8/mo)
5. **Supabase + n8n + Vercel** — the plumbing that makes it one system. (~$30/mo all-in)
6. *(optional)* **CGM (Stelo/Lingo)** — metabolic/glucose response to food and stress. Run a 2–4 week experiment, not forever. (~$50/mo when worn)
7. *(optional)* **RescueTime** — digital/screen time if you want to police focus. (~$12/mo)

**Deliberately skipped:** Oura (redundant with Whoop) · a second budgeting app · any tool that duplicates a feed you already own.

---

## 7. Cost summary (premium but justified)

| | Item | Cost |
|---|---|---|
| One-time | Whoop band + Withings scale + BP monitor | ~$300 |
| Monthly | Whoop $20 · macro-log $0 · Supabase $25 · VPS/n8n $6 · Vercel $0 · domain ~$1 | **~$52/mo** |
| Deferred | Monarch (personal net worth) — add when you decide | +$8/mo |
| Optional | CGM ~$50/mo (when running) · RescueTime $12/mo | as desired |

Roughly **$52/mo + ~$300 hardware** for the full automated system. Monarch (+$8) and CGM are optional add-ons.

---

## 8. Build phases

**Phase 0 — Decide & provision (week 1).** Confirm the open decisions (§10), buy hardware, open Supabase/n8n/Vercel, create Whoop/Monarch/MacroFactor accounts and developer keys.

**Phase 1 — Business layer first (fastest win). ◀ STARTED 2026-06-14.** Warehouse schema, ingestion code, and the first **real** snapshot are in `tools/life/`. Live-wired today: **QuickBooks** (P&L, balance sheet, A/R), **Function Health** (labs), **Credit Karma** (bands), **Google Calendar**, **Granola**. The dashboard's QBO + Labs tiles now show real numbers. **Gap: Follow Up Boss is not connected in the web session** — prospecting stays on the manual Daily Log until FUB is wired (Phase 1.5, top priority).

**Phase 2 — Body layer.** Whoop API + Withings + MacroFactor into the warehouse. Body / sleep / diet tiles live.

**Phase 3 — Financial layer.** QBO (business) and Monarch + Credit Karma (personal) as two separate tabs.

**Phase 4 — Surface.** Ship the mobile-first PWA, install to home screen, launch the 5 AM Life Brief.

**Phase 5 — Harden.** Alerts (recovery red, appt-kept miss, prospecting under pace, AR aging), weekly review view, backfill history.

---

## 9. Where this lives in the brain

- Project brief: `claude/01-projects/Life Tracking System/CLAUDE.md`
- This spec: `claude/01-projects/Life Tracking System/Life Tracking System Design.md`
- Pipeline code (when built): `tools/life/` — mirrors the existing `tools/vnre/` skill pattern.
- New skills: `life-brief` (5 AM roll-up, joins scheduled-tasks) · `macro-log` (text/photo a meal → estimate → write to `diet.entries`).

---

## 10. Decisions

**Locked:**
- Body spine = **Whoop 5.0** (Apple Watch secondary).
- Diet = **`macro-log` skill** — conversational/photo logging to Claude, no app.
- Orchestration = **n8n self-hosted**.
- Workout target = **4×/week** (recovery-gated by Whoop).
- Finances = personal + business, **kept separate**.

**Still open before Phase 0:**
1. **Whoop** — final confirm to buy (recommended) vs Apple-Watch-only fallback.
2. **Personal net worth** — add **Monarch** (link banks via Plaid) or stay Credit-Karma-only for now. *Deferred per your note — flip to "add Monarch" whenever you're ready and Phase 3 lights up.*
3. **CGM** — run a 2–4 week metabolic experiment, or skip.
