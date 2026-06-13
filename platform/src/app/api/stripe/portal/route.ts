import { NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { auth } from "@/lib/auth";
import { prisma, dbEnabled } from "@/lib/db";
import { siteConfig } from "../../../../../site.config";

/** Open the Stripe billing portal so members manage/cancel their own subscription. */
export async function POST() {
  try {
    const session = await auth();
    if (!session?.user?.id || !dbEnabled) {
      return NextResponse.json({ error: "Log in first." }, { status: 401 });
    }

    const user = await prisma.user.findUnique({ where: { id: session.user.id } });
    if (!user?.stripeCustomerId) {
      return NextResponse.json({ error: "No billing account yet." }, { status: 400 });
    }

    const portal = await stripe().billingPortal.sessions.create({
      customer: user.stripeCustomerId,
      return_url: `${siteConfig.url}/dashboard`
    });

    return NextResponse.json({ url: portal.url });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Could not open billing portal.";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
