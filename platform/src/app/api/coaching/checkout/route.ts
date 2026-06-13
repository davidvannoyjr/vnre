import { NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { prisma, dbEnabled } from "@/lib/db";
import { stripe, priceIdForTier, getOrCreateCustomer } from "@/lib/stripe";
import { siteConfig } from "../../../../../site.config";

/**
 * Coach-only: generate a private monthly ($1,000) checkout link for a coaching
 * client. The coach sends the returned URL to the client. On payment, the
 * webhook flips the client's tier to `coaching`. Not exposed on public pricing.
 */
export async function POST(req: Request) {
  try {
    const session = await auth();
    if (!session?.user?.id || session.user.role !== "coach" || !dbEnabled) {
      return NextResponse.json({ error: "Coach access required." }, { status: 403 });
    }

    const { profileId } = (await req.json()) as { profileId: string };
    const profile = await prisma.clientProfile.findUnique({ where: { id: profileId } });
    if (!profile || profile.coachId !== session.user.id) {
      return NextResponse.json({ error: "Not found." }, { status: 404 });
    }

    const priceId = priceIdForTier("coaching");
    if (!priceId) {
      return NextResponse.json(
        { error: "Set STRIPE_PRICE_COACHING to enable coaching billing." },
        { status: 400 }
      );
    }

    const client = await prisma.user.findUnique({ where: { id: profile.clientId } });
    const customerId = await getOrCreateCustomer(profile.clientId, client?.email);

    const checkout = await stripe().checkout.sessions.create({
      mode: "subscription",
      customer: customerId,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${siteConfig.url}/coaching?welcome=1`,
      cancel_url: `${siteConfig.url}/coaching`,
      metadata: { userId: profile.clientId, tier: "coaching", coaching: "1" }
    });

    return NextResponse.json({ url: checkout.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Could not create link.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
