import Stripe from "stripe";
import { PLANS, type Tier } from "@/lib/tiers";

/**
 * Stripe billing helpers. Lazy client so the app boots without keys in dev.
 */

let _stripe: Stripe | null = null;

export function stripe(): Stripe {
  if (!process.env.STRIPE_SECRET_KEY) {
    throw new Error("STRIPE_SECRET_KEY is not set. Add it to .env.local.");
  }
  if (!_stripe) {
    _stripe = new Stripe(process.env.STRIPE_SECRET_KEY, { apiVersion: "2024-12-18.acacia" });
  }
  return _stripe;
}

/** Resolve the Stripe Price ID for a tier from env. */
export function priceIdForTier(tier: Tier): string | null {
  const plan = PLANS.find((p) => p.id === tier);
  if (!plan?.stripeEnv) return null;
  return process.env[plan.stripeEnv] ?? null;
}

/** Reverse lookup: given a Stripe price id, which tier is it? */
export function tierForPriceId(priceId: string): Tier {
  for (const plan of PLANS) {
    if (plan.stripeEnv && process.env[plan.stripeEnv] === priceId) return plan.id;
  }
  return "free";
}

/**
 * Map a customer's active subscription to a tier.
 * Wire this into the auth session callback once an adapter stores the customer id.
 */
export async function getTierForCustomer(customerId: string): Promise<Tier> {
  const subs = await stripe().subscriptions.list({
    customer: customerId,
    status: "active",
    limit: 1,
    expand: ["data.items.data.price"]
  });
  const price = subs.data[0]?.items.data[0]?.price?.id;
  return price ? tierForPriceId(price) : "free";
}
