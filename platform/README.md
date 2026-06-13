# DVN AI Lab — the platform

A subscription platform that teaches real estate agents how to build AI skills into their
business. Four tracks (ChatGPT, Claude, Real Estate AI Tools, Automation & CRM AI), three
levels each (basic / intermediate / advanced), tiered subscriptions, and an automated
content pipeline you control by approving topics.

> Working brand name is **DVN AI Lab** — change it in one place: `site.config.ts`.

## Stack

- **Next.js 15** (App Router, TypeScript, Tailwind) — marketing, blog, tutorials, dashboard.
- **Git-as-CMS** — content lives as `.mdx` files under `content/`. Committing a file
  publishes it. No external CMS, no database required to launch.
- **Auth.js (NextAuth)** — passwordless email magic-link + optional Google.
- **Stripe** — tiered subscriptions (Basic / Pro / Elite), content gated by plan.
- **GitHub Actions** — the automated content pipeline (draft + publish on a schedule).

## Run it

```bash
cd platform
npm install
cp .env.example .env.local   # fill in what you have; the app boots without secrets
npm run dev                  # http://localhost:3000
```

The site runs with **zero secrets** — auth and billing degrade gracefully (login shows a
"not configured" notice; checkout returns a clear error). Add keys when you're ready to
take payments. See `docs/ARCHITECTURE.md` for the launch checklist.

**Run it end-to-end (real subscribe + coaching onboarding) in ~10 min:** `docs/STRIPE.md`.
`docker compose up -d` for Postgres, `npm run db:push && npm run db:seed`, then
`npm run stripe:setup` to create the test prices and `stripe listen` to forward webhooks.

## The thing that makes this run itself

You approve topics. Claude drafts them in your voice. They publish on a schedule. Full
runbook: **`docs/CONTENT-OPS.md`**. Day-to-day, your only job is editing one file:
`content/topics/queue.yaml` — change a topic's `status` to `approved` and the pipeline
takes it from there.

## Scripts

| Command | What it does |
|---|---|
| `npm run dev` / `build` / `start` | Next.js dev / production build / serve |
| `npm run typecheck` | TypeScript check |
| `npm run content:check` | Validate all content frontmatter (CI gate) |
| `npm run topic:new -- --title "..."` | Add a topic to the queue (proposed) |
| `npm run topic:draft` | Draft all `approved` topics via Claude (needs `ANTHROPIC_API_KEY`) |
| `npm run content:publish-due` | Promote scheduled posts whose date has arrived |

## Layout

```
platform/
├── site.config.ts          # brand name, tagline — edit here
├── content/                # the CMS
│   ├── topics/queue.yaml    # ← your control surface: approve topics here
│   ├── blog/*.mdx
│   └── tutorials/<track>/*.mdx
├── src/
│   ├── app/                 # pages + API routes
│   ├── components/
│   └── lib/                 # content loader, tiers/gating, auth, stripe
├── scripts/                 # pipeline: new-topic, draft-topic, publish-due, check-content
├── .github/workflows/       # CI + automated draft/publish
└── docs/                    # ARCHITECTURE, CONTENT-OPS, ROADMAP
```
