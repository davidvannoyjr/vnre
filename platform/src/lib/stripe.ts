import Stripe from "stripe";
import { PLANS, type Tier } from "@/lib/tiers";
import { prisma } from "@/lib/db";

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
export function tierForPriceId(priceId: string | null | undefined): Tier {
  if (!priceId) return "free";
  for (const plan of PLANS) {
    if (plan.stripeEnv && process.env[plan.stripeEnv] === priceId) return plan.id;
  }
  return "free";
}

/**
 * Get the member's Stripe customer id, creating the customer (and persisting
 * the id on the user) the first time. Requires a database.
 */
export async function getOrCreateCustomer(userId: string, email?: string | null): Promise<string> {
  const user = await prisma.user.findUnique({ where: { id: userId } });
  if (user?.stripeCustomerId) return user.stripeCustomerId;

  const customer = await stripe().customers.create({
    email: email ?? undefined,
    metadata: { userId }
  });
  await prisma.user.update({ where: { id: userId }, data: { stripeCustomerId: customer.id } });
  return customer.id;
}

/**
 * Persist a subscription's state to the owning user, resolving the tier from
 * its price. Called by the webhook on create/update; pass null to downgrade.
 */
export async function syncSubscriptionToUser(subscription: Stripe.Subscription | null, customerId: string) {
  const priceId = subscription?.items.data[0]?.price?.id ?? null;
  await prisma.user.updateMany({
    where: { stripeCustomerId: customerId },
    data: {
      tier: tierForPriceId(priceId),
      stripeSubscriptionId: subscription?.id ?? null,
      stripePriceId: priceId,
      stripeCurrentPeriodEnd: subscription?.current_period_end
        ? new Date(subscription.current_period_end * 1000)
        : null
    }
  });
}
