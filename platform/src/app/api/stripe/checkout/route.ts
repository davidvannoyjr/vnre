import { NextResponse } from "next/server";
import { stripe, priceIdForTier, getOrCreateCustomer } from "@/lib/stripe";
import { auth } from "@/lib/auth";
import { dbEnabled } from "@/lib/db";
import { siteConfig } from "../../../../../site.config";
import type { Tier } from "@/lib/tiers";

/** Create a Stripe Checkout session for a subscription tier. */
export async function POST(req: Request) {
  try {
    const { tier } = (await req.json()) as { tier: Tier };
    const priceId = priceIdForTier(tier);
    if (!priceId) {
      return NextResponse.json(
        { error: "This tier isn't configured for billing yet." },
        { status: 400 }
      );
    }

    const session = await auth();
    if (!session?.user?.id || !dbEnabled) {
      return NextResponse.json(
        { error: "Log in first, then subscribe." },
        { status: 401 }
      );
    }

    // Reuse (or create) the member's Stripe customer so upgrades/downgrades and
    // the billing portal all attach to one record.
    const customerId = await getOrCreateCustomer(session.user.id, session.user.email);

    const checkout = await stripe().checkout.sessions.create({
      mode: "subscription",
      customer: customerId,
      line_items: [{ price: priceId, quantity: 1 }],
      allow_promotion_codes: true,
      success_url: `${siteConfig.url}/dashboard?welcome=1`,
      cancel_url: `${siteConfig.url}/pricing`,
      metadata: { userId: session.user.id, tier }
    });

    return NextResponse.json({ url: checkout.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Checkout failed.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
