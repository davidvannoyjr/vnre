# Run it end-to-end in dev (database + Stripe)

Goal: a working local environment where you can actually subscribe, watch a member's tier
flip, open the billing portal, and onboard a coaching client. ~10 minutes, all in Stripe
**test mode** (no real charges).

## 0. Prerequisites
- Docker (for local Postgres), or any Postgres you can point at.
- A Stripe account (test mode). [Stripe CLI](https://stripe.com/docs/stripe-cli) installed
  (`brew install stripe/stripe-cli/stripe`).

## 1. Database
```bash
cd platform
docker compose up -d                 # local Postgres on :5432
cp .env.example .env.local           # then edit values below
```
In `.env.local`:
```
DATABASE_URL=postgresql://dvn:dvn@localhost:5432/dvn_ai_lab
AUTH_SECRET=            # generate: openssl rand -base64 32
COACH_EMAILS=david@vannoyre.com
```
Create the schema:
```bash
npm run db:push
npm run db:seed                      # you as coach + a test client w/ sample workspace
```

## 2. Stripe products + prices (test mode)
Grab your **test** secret key from https://dashboard.stripe.com/test/apikeys, then:
```bash
STRIPE_SECRET_KEY=sk_test_... npm run stripe:setup
```
It prints four lines — paste them into `.env.local`:
```
STRIPE_PRICE_BASIC=price_...
STRIPE_PRICE_PRO=price_...
STRIPE_PRICE_ELITE=price_...
STRIPE_PRICE_COACHING=price_...
```
Also add to `.env.local`:
```
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

## 3. Webhook forwarding (this is what flips the tier)
In a separate terminal:
```bash
stripe listen --forward-to localhost:3000/api/stripe/webhook
```
It prints a signing secret. Put it in `.env.local`:
```
STRIPE_WEBHOOK_SECRET=whsec_...
```

## 4. Login (so you have a session to subscribe with)
Easiest for local: add Google OAuth creds, **or** set an SMTP server for the magic link.
For a no-email quick path, use [Mailtrap](https://mailtrap.io) or a Gmail app password as
`AUTH_EMAIL_SERVER` + `AUTH_EMAIL_FROM`. (The magic-link provider needs the database, which
you set up in step 1.)

## 5. Run it
```bash
npm run dev                          # http://localhost:3000
```

### Test a self-serve subscription
1. Log in (magic link / Google).
2. Go to **/pricing**, click **Subscribe** on Pro.
3. Use Stripe test card `4242 4242 4242 4242`, any future expiry, any CVC/ZIP.
4. The `stripe listen` terminal shows `checkout.session.completed` →
   `customer.subscription.created`. Your `User.tier` flips to `pro`.
5. **/dashboard** now shows Pro, gated Pro tutorials unlock, and **Manage billing** opens the
   Stripe portal.

### Test coaching onboarding
1. Logged in as the coach (your `COACH_EMAILS` address), go to **/coaching/clients**.
2. **Add client** (or use the seeded `test-client@example.com`).
3. On the client page, **Generate monthly checkout link**, open it, pay with `4242…`.
4. The client's tier flips to `coaching`. Log in as that client → **/coaching** shows their
   plan, stage tasks, and shared notes.

## Useful test cards
| Scenario | Card |
|---|---|
| Success | `4242 4242 4242 4242` |
| Requires authentication (3DS) | `4000 0025 0000 3155` |
| Declined | `4000 0000 0000 9995` |

## Trigger webhook events without checking out
```bash
stripe trigger checkout.session.completed
stripe trigger customer.subscription.deleted   # exercises the downgrade path
```

## Going to production
Same envs on your host (Vercel), but **live** keys, a managed Postgres (`npm run db:push` or
a migration), and a real webhook endpoint registered at
`https://yourdomain.com/api/stripe/webhook` (copy that endpoint's signing secret into
`STRIPE_WEBHOOK_SECRET`). Run `npm run stripe:setup` once with your **live** key to create the
live prices.
