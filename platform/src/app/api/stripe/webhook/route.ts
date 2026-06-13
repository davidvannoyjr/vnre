import { NextResponse } from "next/server";
import type Stripe from "stripe";
import { stripe, syncSubscriptionToUser } from "@/lib/stripe";

/**
 * Stripe webhook. Verifies the signature, then keeps each member's persisted
 * tier in sync with their subscription lifecycle. The auth session reads that
 * tier (lib/auth.ts), so this is what actually unlocks gated content.
 */
export async function POST(req: Request) {
  const secret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!secret) {
    return NextResponse.json({ error: "Webhook secret not configured." }, { status: 500 });
  }

  const sig = req.headers.get("stripe-signature");
  if (!sig) return NextResponse.json({ error: "Missing signature." }, { status: 400 });

  const body = await req.text();
  let event: Stripe.Event;
  try {
    event = stripe().webhooks.constructEvent(body, sig, secret);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Invalid signature.";
    return NextResponse.json({ error: message }, { status: 400 });
  }

  try {
    switch (event.type) {
      case "checkout.session.completed": {
        const session = event.data.object as Stripe.Checkout.Session;
        const customerId = session.customer as string;
        if (session.subscription) {
          const subscription = await stripe().subscriptions.retrieve(session.subscription as string);
          await syncSubscriptionToUser(subscription, customerId);
        }
        break;
      }
      case "customer.subscription.created":
      case "customer.subscription.updated": {
        const subscription = event.data.object as Stripe.Subscription;
        await syncSubscriptionToUser(subscription, subscription.customer as string);
        break;
      }
      case "customer.subscription.deleted": {
        const subscription = event.data.object as Stripe.Subscription;
        // Downgrade to free.
        await syncSubscriptionToUser(null, subscription.customer as string);
        break;
      }
      default:
        break;
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : "Webhook handler failed.";
    return NextResponse.json({ error: message }, { status: 500 });
  }

  return NextResponse.json({ received: true });
}
