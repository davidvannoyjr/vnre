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
- Dashboard = **mobile-first PWA** (Next.js on Vercel; reuses the `vannoy_dashboard.html` look).
- Finances tracked **personal + business, kept separate** — no combined net-worth roll-up.
- Spend posture = **premium but justified** (~$66/mo + ~$300 hardware).
- Stack: Supabase (warehouse) · n8n (orchestration) · Vercel (PWA) · Claude `life-brief` skill (brain).

**Inputs:** Whoop · Withings (scale + BP) · MacroFactor · Google Calendar/Gmail/Drive · FUB ·
Mojo · Upfirst · QBO · Monarch · Credit Karma · Granola · Audible.

**Outputs:** mobile PWA dashboard · `YYYY-MM-DD Life Brief.md` (daily) · warehouse tables · alerts.

**Status:** Design complete, awaiting DVN's call on the 7 open decisions (§10 of the spec) to start Phase 0.

**Next step:** DVN answers open decisions → Phase 1 (wire the already-connected business feeds
into the warehouse — value before hardware arrives).
