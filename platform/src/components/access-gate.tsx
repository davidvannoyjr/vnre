import Link from "next/link";
import { canAccess, PLANS, type Tier } from "@/lib/tiers";

/**
 * Wraps gated content. If the viewer's plan clears the required tier, render
 * the content; otherwise show an upgrade CTA. `viewerTier` comes from the
 * session (defaults to "free" pre-billing).
 */
export function AccessGate({
  viewerTier,
  requiredTier,
  children
}: {
  viewerTier: Tier;
  requiredTier: Tier;
  children: React.ReactNode;
}) {
  if (canAccess(viewerTier, requiredTier)) return <>{children}</>;

  const plan = PLANS.find((p) => p.id === requiredTier);

  return (
    <div className="rounded-lg border border-band bg-strip p-8 text-center">
      <div className="mx-auto max-w-md">
        <span className="inline-block rounded-full bg-accent px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
          {plan?.name ?? requiredTier} members only
        </span>
        <h3 className="mt-4 text-xl font-bold">This one is gated.</h3>
        <p className="mt-2 text-steel/70">
          Unlock it on the {plan?.name} plan
          {plan?.price ? ` — $${plan.price}/mo` : ""}. Cancel anytime.
        </p>
        <Link
          href="/pricing"
          className="mt-5 inline-block rounded-md bg-accent px-5 py-2.5 font-medium text-white hover:opacity-90"
        >
          See plans
        </Link>
      </div>
    </div>
  );
}
