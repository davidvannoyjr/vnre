import { NextResponse } from "next/server";
import { stripe, priceIdForTier } from "@/lib/stripe";
import { auth } from "@/lib/auth";
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
    const customerEmail = session?.user?.email ?? undefined;

    const checkout = await stripe().checkout.sessions.create({
      mode: "subscription",
      line_items: [{ price: priceId, quantity: 1 }],
      customer_email: customerEmail,
      allow_promotion_codes: true,
      success_url: `${siteConfig.url}/dashboard?welcome=1`,
      cancel_url: `${siteConfig.url}/pricing`,
      metadata: { tier }
    });

    return NextResponse.json({ url: checkout.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Checkout failed.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
