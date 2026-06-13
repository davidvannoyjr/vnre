# Architecture

## Principle: boots with zero secrets, scales to a real product

Everything optional is lazy. No `ANTHROPIC_API_KEY` → drafting is the only thing that
can't run. No Stripe keys → checkout returns a clear error, the rest of the site works.
No auth provider → login shows a "not configured" notice. This means you can `npm run dev`
and see the whole product on minute one, then wire in services as you go.

## Content = the repo (git-as-CMS)

- Content is `.mdx` files under `content/`. No database, no headless CMS.
- `src/lib/content.ts` reads and validates them at build/request time
  (`gray-matter` + the zod schema in `src/content-schema.ts`).
- A post is **live** when `status: published`, OR `status: scheduled` and `publishDate`
  has passed. That dual rule lets the schedule "just work" even before the publisher
  workflow flips the status.
- Gating: every doc has a `tier` (min plan to read). `src/components/access-gate.tsx`
  shows the content or an upgrade CTA based on the viewer's session tier.

## Tiers & gating (`src/lib/tiers.ts`)

- Subscription tiers: `free` < `basic` < `pro` < `elite` (ranked).
- Content difficulty levels: `basic` / `intermediate` / `advanced`.
- Plans unlock levels: Basic→basic, Pro→+intermediate, Elite→+advanced. A member can read
  any content whose required `tier` rank ≤ their plan rank.
- Four tracks: `chatgpt`, `claude`, `re-tools`, `automation`.

## Auth (`src/lib/auth.ts`)

Auth.js v5. Passwordless email magic-link (preferred for agents) + optional Google. JWT
sessions out of the box. The session's `user.tier` resolves the member's plan — wired to
`"free"` until billing is connected. **For production**, add a database adapter (e.g.
`@auth/prisma-adapter`) so you can persist the user ↔ Stripe customer mapping, then have
the `session` callback call `getTierForCustomer()`.

## Billing (`src/lib/stripe.ts`, `src/app/api/stripe/*`)

- `POST /api/stripe/checkout` creates a Stripe Checkout subscription session for a tier.
- `POST /api/stripe/webhook` verifies signatures and is where you persist customer→tier on
  subscription lifecycle events (the switch is scaffolded with TODOs).
- Tier → Stripe Price ID mapping is env-driven (`STRIPE_PRICE_BASIC/PRO/ELITE`).

## The content pipeline (`scripts/` + `.github/workflows/`)

See `docs/CONTENT-OPS.md`. In short: `queue.yaml` (approve) → `draft-topic.mjs` (Claude
writes `.mdx`) → `publish-due.mjs` (date-based promotion). CI (`ci.yml`) runs
`content:check` + `typecheck` + `build` on every push so a malformed doc can't ship.

## Launch checklist

- [ ] Set brand name/tagline in `site.config.ts`.
- [ ] Deploy to Vercel (zero-config for Next.js). Set `NEXT_PUBLIC_SITE_URL`.
- [ ] Auth: set `AUTH_SECRET` + an email SMTP provider (and/or Google OAuth).
- [ ] Add a DB adapter for persistent users + Stripe customer IDs.
- [ ] Stripe: create 3 products/prices, set `STRIPE_*` envs, register the webhook endpoint,
      finish the webhook switch + `getTierForCustomer` wiring in the session callback.
- [ ] GitHub: add `ANTHROPIC_API_KEY` secret; enable Actions write permission.
- [ ] Seed/approve the first batch of topics in `content/topics/queue.yaml`.

## Deliberately deferred (see ROADMAP)

Database, full subscription state, community, search, email digest delivery, analytics.
The foundation is structured so each slots in without a rewrite.
