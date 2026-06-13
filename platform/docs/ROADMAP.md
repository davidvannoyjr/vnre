# Roadmap

The current build is **complete basic infrastructure**: a runnable, gated, content-driven
platform with an automated approve→publish pipeline. This is the order to harden it into a
revenue product.

## Phase 1 — Take payments (the only thing between you and revenue)
- [ ] Add a DB (Postgres) + `@auth/prisma-adapter`: persist users + Stripe customer id.
- [ ] Finish the Stripe webhook switch (upsert customer→tier; downgrade on cancel).
- [ ] Resolve `session.user.tier` from `getTierForCustomer()` in the auth callback.
- [ ] Customer billing portal link (`stripe.billingPortal.sessions.create`).
- [ ] Create the 3 prices in Stripe; set the env IDs.

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
- [ ] Elite → DVN Coaching application funnel (the natural step up).
- [ ] Cohort/workshop scheduling; gate recordings by tier.
- [ ] Community (start off-the-shelf — Circle/Skool — linked from the dashboard).

## Phase 5 — Scale & insight
- [ ] Analytics: which lessons convert free→paid, where members churn.
- [ ] A/B pricing and landing copy.
- [ ] Referral / affiliate program for member growth.
