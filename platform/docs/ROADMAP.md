# Roadmap

The current build is **complete basic infrastructure**: a runnable, gated, content-driven
platform with an automated approve→publish pipeline. This is the order to harden it into a
revenue product.

## Phase 1 — Take payments  ✅ code complete; remaining items are deploy-time config
- [x] DB (Postgres) + `@auth/prisma-adapter`: persists users + Stripe customer id (`prisma/schema.prisma`).
- [x] Stripe webhook keeps each member's `tier` in sync (create/update/cancel → `syncSubscriptionToUser`).
- [x] `session.user.tier` resolves from the persisted user row (`lib/auth.ts`).
- [x] Customer billing portal (`/api/stripe/portal` + "Manage billing" on the dashboard).
- [x] Checkout attaches a reusable Stripe customer (`/api/stripe/checkout`).
- [ ] **Provision a Postgres DB**, set `DATABASE_URL`, run `npm run db:push`.
- [ ] **Create the 3 prices in Stripe**, set `STRIPE_PRICE_BASIC/PRO/ELITE`.
- [ ] **Register the webhook endpoint** (`/api/stripe/webhook`), set `STRIPE_WEBHOOK_SECRET`.

## Phase 2 — Make it sticky
- [ ] Progress tracking (mark lessons complete) — per-user, in the DB.
- [ ] Guided learning paths per track (prerequisites already in frontmatter).
- [ ] Search across blog + tutorials (e.g. Pagefind — static, no infra).
- [ ] Email: deliver the weekly "what changed in AI" digest to free + paid lists.

## Phase 3 — Lean into automation
- [ ] Auto-propose topics: a scheduled job that drafts *proposed* topics from AI news +
      your coaching themes, for you to approve (extends the pipeline you already have).
- [ ] Auto-generate the monthly "what changed in AI" update from a curated source list.
- [ ] Per-tier content recommendations on the dashboard.

## Phase 4 — Coaching upsell
- [x] **1:1 Coaching tier** — invite-only `coaching` plan, two-sided client workspace
      (business plan, five-stage task outline, coach-private/shareable notes), per-client
      monthly checkout links. See `docs/COACHING.md`. (Config left: `STRIPE_PRICE_COACHING`,
      `COACH_EMAILS`.)
- [ ] Pricing-page "Apply for coaching" → a real application form/funnel (currently mailto).
- [ ] Cohort/workshop scheduling; gate recordings by tier.
- [ ] Community (start off-the-shelf — Circle/Skool — linked from the dashboard).

## Phase 5 — Scale & insight
- [ ] Analytics: which lessons convert free→paid, where members churn.
- [ ] A/B pricing and landing copy.
- [ ] Referral / affiliate program for member growth.
