import Link from "next/link";
import { notFound } from "next/navigation";
import { getAllTutorials, getTutorial } from "@/lib/content";
import { Mdx } from "@/components/mdx";
import { AccessGate } from "@/components/access-gate";
import { auth } from "@/lib/auth";
import { TRACKS, LEVELS, type Tier } from "@/lib/tiers";

export function generateStaticParams() {
  return getAllTutorials().map((t) => ({ track: t.track, slug: t.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const t = getTutorial(slug);
  return t ? { title: t.frontmatter.title, description: t.frontmatter.description } : {};
}

export default async function TutorialPage({
  params
}: {
  params: Promise<{ track: string; slug: string }>;
}) {
  const { track, slug } = await params;
  const tutorial = getTutorial(slug);
  if (!tutorial || tutorial.track !== track || tutorial.frontmatter.status === "draft") notFound();

  const session = await auth();
  const viewerTier: Tier = session?.user?.tier ?? "free";
  const fm = tutorial.frontmatter;

  return (
    <article className="mx-auto max-w-3xl px-4 py-16">
      <Link href={`/tutorials/${track}`} className="text-sm text-accent hover:underline">
        ← {TRACKS[tutorial.track].name}
      </Link>
      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <span className="rounded bg-steel px-2 py-0.5 font-semibold uppercase tracking-wide text-white">
          {LEVELS[tutorial.level].name}
        </span>
        <span className="rounded bg-strip px-2 py-0.5 text-steel/70">~{fm.estimatedMinutes} min</span>
        {fm.tools.map((tool) => (
          <span key={tool} className="rounded bg-strip px-2 py-0.5 text-steel/70">{tool}</span>
        ))}
      </div>
      <h1 className="mt-3 text-3xl font-bold tracking-tight">{fm.title}</h1>
      <p className="mt-3 text-lg text-steel/70">{fm.description}</p>

      {fm.prerequisites.length > 0 && (
        <div className="mt-4 rounded-md border border-band bg-strip p-3 text-sm">
          <span className="font-semibold">Before this: </span>
          {fm.prerequisites.map((pre, i) => (
            <span key={pre}>
              {i > 0 && ", "}
              <Link href={`/tutorials/${track}/${pre}`} className="text-accent hover:underline">{pre}</Link>
            </span>
          ))}
        </div>
      )}

      <hr className="my-8 border-band" />
      <AccessGate viewerTier={viewerTier} requiredTier={fm.tier}>
        <Mdx source={tutorial.body} />
      </AccessGate>
    </article>
  );
}
