import Link from "next/link";
import { auth } from "@/lib/auth";
import { getAllTutorials, getAllBlogPosts } from "@/lib/content";
import { PLANS, LEVELS, type Tier, canAccess } from "@/lib/tiers";
import { ManageBillingButton } from "@/components/manage-billing-button";
import { dbEnabled } from "@/lib/db";
import { completedCount } from "@/lib/progress";

export const metadata = { title: "Dashboard" };

export default async function DashboardPage() {
  const session = await auth();

  if (!session?.user) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-24 text-center">
        <h1 className="text-2xl font-bold">Members only</h1>
        <p className="mt-2 text-steel/70">Log in to see your dashboard.</p>
        <Link href="/login" className="mt-6 inline-block rounded-md bg-accent px-5 py-2.5 text-white">
          Log in
        </Link>
      </div>
    );
  }

  const tier: Tier = session.user.tier ?? "free";
  const plan = PLANS.find((p) => p.id === tier)!;
  const tutorials = getAllTutorials();
  const unlocked = tutorials.filter((t) => canAccess(tier, t.frontmatter.tier));
  const latest = getAllBlogPosts().slice(0, 5);
  const completed = dbEnabled && session.user.id ? await completedCount(session.user.id) : 0;

  return (
    <div className="mx-auto max-w-5xl px-4 py-16">
      <h1 className="text-3xl font-bold tracking-tight">Welcome back{session.user.name ? `, ${session.user.name}` : ""}.</h1>
      <div className="mt-2 flex items-center gap-3">
        <span className="rounded-full bg-accent px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
          {plan.name} plan
        </span>
        {tier !== "elite" && (
          <Link href="/pricing" className="text-sm text-accent hover:underline">Upgrade →</Link>
        )}
        {tier !== "free" && <ManageBillingButton />}
        {(session.user.role === "coach" || tier === "coaching") && (
          <Link
            href={session.user.role === "coach" ? "/coaching/clients" : "/coaching"}
            className="text-sm text-accent hover:underline"
          >
            {session.user.role === "coach" ? "Coaching clients →" : "My coaching →"}
          </Link>
        )}
      </div>

      <section className="mt-10 grid gap-6 sm:grid-cols-3">
        <Stat label="Lessons completed" value={`${completed} / ${unlocked.length}`} />
        <Stat label="Levels you can access" value={plan.unlocks.map((l) => LEVELS[l].name).join(", ") || "Free intros"} />
        <Stat label="New this week" value={`${latest.length} posts`} />
      </section>

      <section className="mt-12">
        <h2 className="text-xl font-bold">Continue learning</h2>
        <ul className="mt-4 divide-y divide-band">
          {unlocked.slice(0, 6).map((t) => (
            <li key={t.slug} className="py-3">
              <Link href={`/tutorials/${t.track}/${t.slug}`} className="group flex justify-between">
                <span className="font-medium group-hover:text-accent">{t.frontmatter.title}</span>
                <span className="text-xs text-steel/50">{LEVELS[t.level].name}</span>
              </Link>
            </li>
          ))}
          {unlocked.length === 0 && <li className="py-3 text-steel/60">No lessons unlocked yet.</li>}
        </ul>
      </section>

      <section className="mt-12">
        <h2 className="text-xl font-bold">Latest from the blog</h2>
        <ul className="mt-4 divide-y divide-band">
          {latest.map((p) => (
            <li key={p.slug} className="py-3">
              <Link href={`/blog/${p.slug}`} className="hover:text-accent">{p.frontmatter.title}</Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-band p-5">
      <div className="text-xs uppercase tracking-wide text-steel/50">{label}</div>
      <div className="mt-1 text-lg font-bold">{value}</div>
    </div>
  );
}
