import Link from "next/link";
import { siteConfig } from "../../site.config";
import { TRACKS, LEVELS, type Track, type Level } from "@/lib/tiers";

export default function HomePage() {
  return (
    <>
      {/* Hero */}
      <section className="border-b border-band bg-strip">
        <div className="mx-auto max-w-6xl px-4 py-20 text-center">
          <h1 className="mx-auto max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl">
            {siteConfig.tagline}
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-lg text-steel/70">
            Stop reading think-pieces about AI. Build skills that close more listings — from your
            first prompt to a business that runs on systems. Structured for where you actually are:
            basic, intermediate, or advanced.
          </p>
          <div className="mt-8 flex justify-center gap-4">
            <Link
              href="/pricing"
              className="rounded-md bg-accent px-6 py-3 font-medium text-white hover:opacity-90"
            >
              Start now
            </Link>
            <Link
              href="/tutorials"
              className="rounded-md border border-steel px-6 py-3 font-medium hover:bg-white"
            >
              Browse tutorials
            </Link>
          </div>
        </div>
      </section>

      {/* Tracks */}
      <section className="mx-auto max-w-6xl px-4 py-16">
        <h2 className="text-2xl font-bold tracking-tight">Four tracks. Pick your tool.</h2>
        <p className="mt-2 text-steel/70">
          Every track runs basic → intermediate → advanced. Start anywhere.
        </p>
        <div className="mt-8 grid gap-6 sm:grid-cols-2">
          {(Object.keys(TRACKS) as Track[]).map((key) => (
            <Link
              key={key}
              href={`/tutorials/${key}`}
              className="group rounded-lg border border-band p-6 hover:border-accent"
            >
              <h3 className="text-lg font-semibold group-hover:text-accent">{TRACKS[key].name}</h3>
              <p className="mt-2 text-sm text-steel/70">{TRACKS[key].blurb}</p>
            </Link>
          ))}
        </div>
      </section>

      {/* Levels */}
      <section className="border-t border-band bg-strip">
        <div className="mx-auto max-w-6xl px-4 py-16">
          <h2 className="text-2xl font-bold tracking-tight">Built for your level — no overwhelm.</h2>
          <div className="mt-8 grid gap-6 sm:grid-cols-3">
            {(Object.keys(LEVELS) as Level[])
              .sort((a, b) => LEVELS[a].order - LEVELS[b].order)
              .map((key) => (
                <div key={key} className="rounded-lg border border-band bg-white p-6">
                  <div className="text-sm font-semibold uppercase tracking-wide text-accent">
                    {LEVELS[key].name}
                  </div>
                  <p className="mt-2 text-steel/70">{LEVELS[key].blurb}</p>
                </div>
              ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-6xl px-4 py-16 text-center">
        <h2 className="text-2xl font-bold tracking-tight">New AI content every week. Approved by DVN.</h2>
        <p className="mx-auto mt-2 max-w-2xl text-steel/70">
          The tools change monthly. This platform keeps up — evergreen tutorials, dated updates, and
          a weekly digest of what actually matters for a listing business.
        </p>
        <Link
          href="/pricing"
          className="mt-6 inline-block rounded-md bg-accent px-6 py-3 font-medium text-white hover:opacity-90"
        >
          See plans
        </Link>
      </section>
    </>
  );
}
