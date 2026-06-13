import { PLANS } from "@/lib/tiers";
import { CheckoutButton } from "@/components/checkout-button";

export const metadata = { title: "Pricing" };

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-16">
      <div className="text-center">
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Plans that match your level.</h1>
        <p className="mx-auto mt-3 max-w-2xl text-steel/70">
          Start free. Upgrade when you outgrow it. Every plan includes the evergreen blog and weekly
          AI digest. Cancel anytime.
        </p>
      </div>

      <div className="mt-12 grid gap-6 lg:grid-cols-4">
        {PLANS.map((plan) => (
          <div
            key={plan.id}
            className={`flex flex-col rounded-lg border p-6 ${
              plan.highlight ? "border-accent ring-1 ring-accent" : "border-band"
            }`}
          >
            {plan.highlight && (
              <span className="mb-3 self-start rounded-full bg-accent px-2.5 py-0.5 text-xs font-semibold uppercase tracking-wide text-white">
                Most popular
              </span>
            )}
            <h2 className="text-lg font-bold">{plan.name}</h2>
            <div className="mt-2">
              <span className="text-3xl font-bold">${plan.price}</span>
              {plan.price > 0 && <span className="text-steel/60">/mo</span>}
            </div>
            <p className="mt-3 text-sm text-steel/70">{plan.blurb}</p>
            <ul className="mt-5 flex-1 space-y-2 text-sm">
              {plan.features.map((f) => (
                <li key={f} className="flex gap-2">
                  <span className="text-accent">✓</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
            <div className="mt-6">
              {plan.id === "free" ? (
                <a
                  href="/login"
                  className="block rounded-md border border-steel px-4 py-2 text-center font-medium hover:bg-strip"
                >
                  Create free account
                </a>
              ) : (
                <CheckoutButton tier={plan.id} highlight={plan.highlight} />
              )}
            </div>
          </div>
        ))}
      </div>

      <p className="mx-auto mt-10 max-w-2xl text-center text-xs text-steel/50">
        Elite includes done-with-you build sessions and a direct line into DVN Coaching — the
        natural step up into 1:1 coaching for producing agents.
      </p>
    </div>
  );
}
