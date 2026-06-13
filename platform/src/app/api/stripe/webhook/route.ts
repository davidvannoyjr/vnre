import { NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";

/**
 * Stripe webhook. Verifies the signature, then reacts to subscription lifecycle
 * events. Persist the customer→tier mapping here (DB) so the auth session can
 * resolve a member's tier. Scaffolded with the event switch ready to fill in.
 */
export async function POST(req: Request) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secret) {
    return NextResponse.json({ error: "Webhook secret not configured." }, { status: 500 });
  }

  const sig = req.headers.get("stripe-signature");
  if (!sig) return NextResponse.json({ error: "Missing signature." }, { status: 400 });

  const body = await req.text();
  let event;
  try {
    event = stripe().webhooks.constructEvent(body, sig, secret);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Invalid signature.";
    return NextResponse.json({ error: message }, { status: 400 });
  }

  switch (event.type) {
    case "checkout.session.completed":
    case "customer.subscription.created":
    case "customer.subscription.updated":
      // TODO: upsert { customerId, email, tier } in your DB so getTierForCustomer resolves.
      break;
    case "customer.subscription.deleted":
      // TODO: downgrade the member to "free".
      break;
    default:
      break;
  }

  return NextResponse.json({ received: true });
}
