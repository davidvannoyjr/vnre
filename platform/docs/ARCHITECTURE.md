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

Auth.js v5. Passwordless email magic-link (preferred for agents) + optional Google.
**When `DATABASE_URL` is set**, it uses the Prisma adapter with database sessions and
resolves `session.user.tier` from the persisted `User` row (kept current by the Stripe
webhook). **Without a database**, it falls back to JWT sessions and everyone resolves to
`"free"` — so the app boots with zero setup. The email magic-link provider requires the
database (it stores verification tokens), so it's only enabled when both SMTP and
`DATABASE_URL` are configured; Google works either way.

Persistence is **Prisma** (`prisma/schema.prisma`, `src/lib/db.ts`): the Auth.js adapter
models plus billing fields on `User` (`stripeCustomerId`, `tier`, etc.).

## Billing (`src/lib/stripe.ts`, `src/app/api/stripe/*`) — implemented

- `POST /api/stripe/checkout` — looks up (or creates) the member's Stripe customer, then
  creates a subscription Checkout session for the tier.
- `POST /api/stripe/webhook` — verifies signatures and keeps the persisted `User.tier` in
  sync on `checkout.session.completed` and `customer.subscription.created/updated/deleted`
  (downgrades to `free` on cancel) via `syncSubscriptionToUser`.
- `POST /api/stripe/portal` — opens the Stripe billing portal so members manage/cancel
  themselves ("Manage billing" on the dashboard).
- Tier → Stripe Price ID mapping is env-driven (`STRIPE_PRICE_BASIC/PRO/ELITE`); the reverse
  lookup resolves a subscription's price back to a tier.
- **Remaining config (not code):** provision Postgres + `DATABASE_URL` (`npm run db:push`),
  create the 3 Stripe prices, register the webhook endpoint + `STRIPE_WEBHOOK_SECRET`.

## 1:1 Coaching (`src/app/coaching/*`, `src/lib/coaching.ts`)

A private, invite-only `coaching` tier with a two-sided per-client workspace — business plan,
tasks on the five-stage outline (Forge → Own), and coach-private/shareable notes. Coaches are
identified by `COACH_EMAILS` (or stored role); they onboard clients and mint per-client
monthly checkout links (`/api/coaching/checkout`). Hidden from public pricing. All loads and
mutations are guarded server-side by role + profile ownership. Full guide: `docs/COACHING.md`.

## The content pipeline (`scripts/` + `.github/workflows/`)

See `docs/CONTENT-OPS.md`. In short: `queue.yaml` (approve) → `draft-topic.mjs` (Claude
writes `.mdx`) → `publish-due.mjs` (date-based promotion). CI (`ci.yml`) runs
`content:check` + `typecheck` + `build` on every push so a malformed doc can't ship.

## Launch checklist

- [ ] Set brand name/tagline in `site.config.ts`.
- [ ] Deploy to Vercel (zero-config for Next.js). Set `NEXT_PUBLIC_SITE_URL`.
- [ ] Provision Postgres, set `DATABASE_URL`, run `npm run db:push`.
- [ ] Auth: set `AUTH_SECRET` + an email SMTP provider (and/or Google OAuth). The email
      magic-link needs the database; Google works with or without it.
- [ ] Stripe: create 3 products/prices, set `STRIPE_*` envs, register the webhook endpoint
      (`/api/stripe/webhook`) + `STRIPE_WEBHOOK_SECRET`. (Webhook handling is already built.)
- [ ] GitHub: add `ANTHROPIC_API_KEY` secret; enable Actions write permission.
- [ ] Seed/approve the first batch of topics in `content/topics/queue.yaml`.

## Deliberately deferred (see ROADMAP)

Database, full subscription state, community, search, email digest delivery, analytics.
The foundation is structured so each slots in without a rewrite.
