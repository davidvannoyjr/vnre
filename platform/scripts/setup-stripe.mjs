#!/usr/bin/env node
/**
 * Create (idempotently) the Stripe products + monthly prices for every paid
 * tier, and print the STRIPE_PRICE_* lines to paste into .env.local. Run in
 * TEST mode first.
 *
 *   STRIPE_SECRET_KEY=sk_test_... node scripts/setup-stripe.mjs
 *
 * Safe to re-run: it reuses an existing product (matched by metadata.dvn_tier)
 * and an existing price with the same amount/interval rather than duplicating.
 *
 * Amounts mirror src/lib/tiers.ts — keep them in sync if you change pricing.
 */
import Stripe from "stripe";

const TIERS = [
  { tier: "basic", name: "DVN AI Lab — Basic", amount: 2900, env: "STRIPE_PRICE_BASIC" },
  { tier: "pro", name: "DVN AI Lab — Pro", amount: 7900, env: "STRIPE_PRICE_PRO" },
  { tier: "elite", name: "DVN AI Lab — Elite", amount: 19900, env: "STRIPE_PRICE_ELITE" },
  { tier: "coaching", name: "DVN 1:1 Coaching", amount: 100000, env: "STRIPE_PRICE_COACHING" }
];

const key = process.env.STRIPE_SECRET_KEY;
if (!key) {
  console.error(
    "STRIPE_SECRET_KEY is not set.\n" +
      "Get your TEST secret key from https://dashboard.stripe.com/test/apikeys and run:\n" +
      "  STRIPE_SECRET_KEY=sk_test_... node scripts/setup-stripe.mjs"
  );
  process.exit(1);
}
if (!key.startsWith("sk_test_")) {
  console.warn("⚠  This key is not a test key (sk_test_…). Continuing — make sure that's intended.\n");
}

const stripe = new Stripe(key, { apiVersion: "2024-12-18.acacia" });

async function ensureProduct(t) {
  const products = await stripe.products.list({ limit: 100, active: true });
  let product = products.data.find((p) => p.metadata?.dvn_tier === t.tier);
  if (!product) {
    product = await stripe.products.create({ name: t.name, metadata: { dvn_tier: t.tier } });
    console.error(`  created product ${product.id} (${t.tier})`);
  }
  return product;
}

async function ensurePrice(product, t) {
  const prices = await stripe.prices.list({ product: product.id, active: true, limit: 100 });
  let price = prices.data.find(
    (p) => p.unit_amount === t.amount && p.currency === "usd" && p.recurring?.interval === "month"
  );
  if (!price) {
    price = await stripe.prices.create({
      product: product.id,
      unit_amount: t.amount,
      currency: "usd",
      recurring: { interval: "month" }
    });
    console.error(`  created price ${price.id} ($${t.amount / 100}/mo)`);
  }
  return price;
}

const lines = [];
for (const t of TIERS) {
  const product = await ensureProduct(t);
  const price = await ensurePrice(product, t);
  lines.push(`${t.env}=${price.id}`);
}

console.error("\nPaste these into .env.local:\n");
console.log(lines.join("\n"));
