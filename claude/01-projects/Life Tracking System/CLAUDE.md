# Project — Life Tracking System

**Purpose (DVN):** One always-current system tracking DVN's entire life — body, sleep,
diet/macros, work structure, calls/appointments, business, and money — fed automatically
from the apps he already runs plus a short list of additions, surfaced in a mobile-first
dashboard and a 5 AM Life Brief.

**Full spec:** [`Life Tracking System Design.md`](Life%20Tracking%20System%20Design.md) — the design doc wins on any conflict.

**Cadence:** Standing system. Morning Life Brief 5 AM (joins the existing scheduled-tasks set);
hourly/realtime business feeds; weekly financial + coaching roll-up.

**Locked decisions (2026-06-14):**
- Body spine = **Whoop 5.0** (chosen for its official API; Apple Watch secondary).
- Diet = **`macro-log` skill** — text/photo a meal to Claude → it estimates and writes macros. No app.
- Dashboard = **mobile-first PWA** (Next.js on Vercel; reuses the `vannoy_dashboard.html` look).
- Orchestration = **n8n self-hosted**.
- Workout target = **4×/week** (recovery-gated by Whoop).
- Finances tracked **personal + business, kept separate** — no combined net-worth roll-up.
- Spend posture = **premium but justified** (~$52/mo + ~$300 hardware; Monarch +$8 if added).
- Stack: Supabase (warehouse) · n8n (orchestration) · Vercel (PWA) · Claude `life-brief` + `macro-log` skills.

**Inputs:** Whoop · Withings (scale + BP) · `macro-log` (conversational) · Google Calendar/Gmail/Drive ·
FUB · Mojo · Upfirst · QBO · Credit Karma · Granola · Audible · *(Monarch — deferred)*.

**Outputs:** mobile PWA dashboard · `YYYY-MM-DD Life Brief.md` (daily) · warehouse tables · alerts.

**Status:** Design complete. 3 open items (Whoop buy confirm · Monarch yes/no · CGM yes/no — §10 of the spec).

**Next step:** Phase 1 — wire the already-connected business feeds (FUB, Calendar, QBO, Granola)
into the warehouse. Delivers value before any hardware arrives; doesn't depend on the open items.
