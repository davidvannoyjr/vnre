import Link from "next/link";
import { getAllBlogPosts, getAllTutorials } from "@/lib/content";
import { TRACKS, LEVELS } from "@/lib/tiers";

export const metadata = { title: "Search" };

type Result = { title: string; description: string; href: string; kind: string };

function search(q: string): Result[] {
  const needle = q.toLowerCase();
  const match = (...fields: (string | string[])[]) =>
    fields.flat().join(" ").toLowerCase().includes(needle);

  const posts: Result[] = getAllBlogPosts()
    .filter((p) => match(p.frontmatter.title, p.frontmatter.description, p.frontmatter.tags))
    .map((p) => ({
      title: p.frontmatter.title,
      description: p.frontmatter.description,
      href: `/blog/${p.slug}`,
      kind: p.frontmatter.evergreen ? "Evergreen" : "Update"
    }));

  const tutorials: Result[] = getAllTutorials()
    .filter((t) => match(t.frontmatter.title, t.frontmatter.description, t.frontmatter.tags, t.frontmatter.tools))
    .map((t) => ({
      title: t.frontmatter.title,
      description: t.frontmatter.description,
      href: `/tutorials/${t.track}/${t.slug}`,
      kind: `${TRACKS[t.track].name} · ${LEVELS[t.level].name}`
    }));

  return [...tutorials, ...posts];
}

export default async function SearchPage({
  searchParams
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q = "" } = await searchParams;
  const query = q.trim();
  const results = query.length >= 2 ? search(query) : [];

  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <h1 className="text-3xl font-bold tracking-tight">Search</h1>
      <form action="/search" className="mt-4">
        <input
          type="search"
          name="q"
          defaultValue={query}
          autoFocus
          placeholder="Search tutorials and posts…"
          className="w-full rounded-md border border-band px-4 py-2.5"
        />
      </form>

      {query.length >= 2 && (
        <p className="mt-6 text-sm text-steel/60">
          {results.length} result{results.length === 1 ? "" : "s"} for “{query}”
        </p>
      )}

      <ul className="mt-4 divide-y divide-band">
        {results.map((r) => (
          <li key={r.href} className="py-4">
            <Link href={r.href} className="group block">
              <div className="text-xs text-steel/50">{r.kind}</div>
              <div className="mt-0.5 font-semibold group-hover:text-accent">{r.title}</div>
              <div className="mt-0.5 text-sm text-steel/70">{r.description}</div>
            </Link>
          </li>
        ))}
      </ul>

      {query.length >= 2 && results.length === 0 && (
        <p className="mt-6 text-steel/60">Nothing matched. Try a different term or browse the tracks.</p>
      )}
    </div>
  );
}
