# 1:1 Coaching tier

A private, invite-only coaching offering layered on top of the platform — how you charge and
run your existing 1:1 clients ($1,000/mo). Separate from the self-serve content tiers: it's a
relationship, not a public product.

## What it is

- A `coaching` tier (rank above Elite) that unlocks all content **plus** a private workspace.
- **Invite-only** — hidden from public pricing (the pricing page shows an "Apply for coaching"
  contact instead). You onboard each client; you cap your own capacity (~10–12).
- A **two-sided portal**: clients log in to their workspace; you get a coach view of everyone.

## The workspace (per client)

- **Business plan** — a living plan, editable by both you and the client.
- **Tasks** — mapped to your five-stage outline: **Forge → Conquer → Anchor → Architect →
  Own**. You create them; either of you checks them off.
- **Coaching notes** — **coach-private by default**; flip a note to "shared" when you want the
  client to see it.

## Roles

- A user is a **coach** if their email is in `COACH_EMAILS` (or their stored `role` is `coach`).
  Put your address in `COACH_EMAILS`.
- Everyone else is a **member**. A member becomes a coaching client when you add them.

## How you run it day to day

1. **Coaching clients** (`/coaching/clients`) → **Add client** (name + email). This creates
   their account + a coaching profile linked to you.
2. On the client's page, **Generate monthly checkout link** and send it to them. When they
   pay, the Stripe webhook flips their tier to `coaching`.
3. The client logs in (magic link) at `/coaching` to see their plan, tasks, and shared notes.
4. You manage their plan, notes, and stage tasks from `/coaching/clients/[id]`.

## Setup

- `COACH_EMAILS=david@vannoyre.com`
- `STRIPE_PRICE_COACHING=price_...` (create a $1,000/mo recurring price in Stripe)
- Requires the database (`DATABASE_URL`) — the workspace is persisted.

## Access control

Every load and mutation is guarded server-side: coach actions require `role: coach` **and**
ownership of the profile; the client may only touch their own profile (toggle tasks, edit
their plan). Notes never reach a client unless explicitly shared. See
`src/app/coaching/actions.ts` and `src/lib/coaching.ts`.
