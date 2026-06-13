import Link from "next/link";
import { getAllBlogPosts } from "@/lib/content";
import { format } from "date-fns";

export const metadata = { title: "Blog & AI Updates" };

export default function BlogIndex() {
  const posts = getAllBlogPosts();
  const evergreen = posts.filter((p) => p.frontmatter.evergreen);
  const updates = posts.filter((p) => !p.frontmatter.evergreen);

  return (
    <div className="mx-auto max-w-4xl px-4 py-16">
      <h1 className="text-3xl font-bold tracking-tight">Blog & AI Updates</h1>
      <p className="mt-2 text-steel/70">
        Evergreen guidance that stays true, plus dated updates when the tools change.
      </p>

      {posts.length === 0 && (
        <p className="mt-10 text-steel/60">No posts published yet. The pipeline will fill this in.</p>
      )}

      {updates.length > 0 && (
        <section className="mt-12">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-accent">Latest updates</h2>
          <ul className="mt-4 divide-y divide-band">
            {updates.map((p) => (
              <PostRow key={p.slug} slug={p.slug} title={p.frontmatter.title}
                description={p.frontmatter.description} date={p.frontmatter.publishDate} />
            ))}
          </ul>
        </section>
      )}

      {evergreen.length > 0 && (
        <section className="mt-12">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-accent">Evergreen</h2>
          <ul className="mt-4 divide-y divide-band">
            {evergreen.map((p) => (
              <PostRow key={p.slug} slug={p.slug} title={p.frontmatter.title}
                description={p.frontmatter.description} date={p.frontmatter.publishDate} />
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}

function PostRow({ slug, title, description, date }: {
  slug: string; title: string; description: string; date: string;
}) {
  return (
    <li className="py-5">
      <Link href={`/blog/${slug}`} className="group block">
        <div className="text-xs text-steel/50">{format(new Date(date), "MMM d, yyyy")}</div>
        <h3 className="mt-1 text-lg font-semibold group-hover:text-accent">{title}</h3>
        <p className="mt-1 text-sm text-steel/70">{description}</p>
      </Link>
    </li>
  );
}
