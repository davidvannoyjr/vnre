import Link from "next/link";
import { notFound } from "next/navigation";
import { getTutorialsByTrack } from "@/lib/content";
import { TRACKS, LEVELS, PLANS, type Track, type Level } from "@/lib/tiers";

export function generateStaticParams() {
  return (Object.keys(TRACKS) as Track[]).map((track) => ({ track }));
}

export async function generateMetadata({ params }: { params: Promise<{ track: string }> }) {
  const { track } = await params;
  const t = TRACKS[track as Track];
  return t ? { title: t.name } : {};
}

export default async function TrackPage({ params }: { params: Promise<{ track: string }> }) {
  const { track } = await params;
  if (!(track in TRACKS)) notFound();
  const t = track as Track;
  const tutorials = getTutorialsByTrack(t);

  return (
    <div className="mx-auto max-w-4xl px-4 py-16">
      <Link href="/tutorials" className="text-sm text-accent hover:underline">← All tracks</Link>
      <h1 className="mt-3 text-3xl font-bold tracking-tight">{TRACKS[t].name}</h1>
      <p className="mt-2 text-steel/70">{TRACKS[t].blurb}</p>

      {(Object.keys(LEVELS) as Level[])
        .sort((a, b) => LEVELS[a].order - LEVELS[b].order)
        .map((level) => {
          const items = tutorials.filter((x) => x.level === level);
          if (items.length === 0) return null;
          const plan = PLANS.find((p) => p.unlocks.includes(level));
          return (
            <section key={level} className="mt-10">
              <div className="flex items-baseline justify-between border-b border-band pb-2">
                <h2 className="text-xl font-bold">{LEVELS[level].name}</h2>
                <span className="text-xs text-steel/50">
                  {plan ? `${plan.name}+` : "Free"} · {LEVELS[level].blurb}
                </span>
              </div>
              <ul className="mt-4 divide-y divide-band">
                {items.map((x) => (
                  <li key={x.slug} className="py-4">
                    <Link href={`/tutorials/${t}/${x.slug}`} className="group block">
                      <h3 className="font-semibold group-hover:text-accent">{x.frontmatter.title}</h3>
                      <p className="mt-1 text-sm text-steel/70">{x.frontmatter.description}</p>
                      <div className="mt-1 text-xs text-steel/50">
                        ~{x.frontmatter.estimatedMinutes} min
                        {x.frontmatter.tools.length > 0 && ` · ${x.frontmatter.tools.join(", ")}`}
                      </div>
                    </Link>
                  </li>
                ))}
              </ul>
            </section>
          );
        })}

      {tutorials.length === 0 && (
        <p className="mt-10 text-steel/60">No lessons published in this track yet.</p>
      )}
    </div>
  );
}
