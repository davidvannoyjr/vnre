import Link from "next/link";
import { getAllTutorials } from "@/lib/content";
import { TRACKS, type Track } from "@/lib/tiers";

export const metadata = { title: "Tutorials" };

export default function TutorialsIndex() {
  const all = getAllTutorials();
  const counts = (Object.keys(TRACKS) as Track[]).reduce(
    (acc, t) => ({ ...acc, [t]: all.filter((x) => x.track === t).length }),
    {} as Record<Track, number>
  );

  return (
    <div className="mx-auto max-w-5xl px-4 py-16">
      <h1 className="text-3xl font-bold tracking-tight">Tutorials</h1>
      <p className="mt-2 text-steel/70">
        Four tracks, three levels each. Pick a tool and start where you are.
      </p>
      <div className="mt-10 grid gap-6 sm:grid-cols-2">
        {(Object.keys(TRACKS) as Track[]).map((t) => (
          <Link
            key={t}
            href={`/tutorials/${t}`}
            className="group rounded-lg border border-band p-6 hover:border-accent"
          >
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold group-hover:text-accent">{TRACKS[t].name}</h2>
              <span className="text-sm text-steel/50">{counts[t]} lessons</span>
            </div>
            <p className="mt-2 text-sm text-steel/70">{TRACKS[t].blurb}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
