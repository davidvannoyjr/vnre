import { notFound } from "next/navigation";
import { format } from "date-fns";
import { getAllBlogPosts, getBlogPost } from "@/lib/content";
import { Mdx } from "@/components/mdx";
import { AccessGate } from "@/components/access-gate";
import { auth } from "@/lib/auth";
import type { Tier } from "@/lib/tiers";

export function generateStaticParams() {
  return getAllBlogPosts().map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = getBlogPost(slug);
  return post ? { title: post.frontmatter.title, description: post.frontmatter.description } : {};
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = getBlogPost(slug);
  if (!post || post.frontmatter.status === "draft") notFound();

  const session = await auth();
  const viewerTier: Tier = session?.user?.tier ?? "free";

  return (
    <article className="mx-auto max-w-3xl px-4 py-16">
      <div className="text-xs text-steel/50">
        {format(new Date(post.frontmatter.publishDate), "MMMM d, yyyy")}
        {post.frontmatter.evergreen ? " · Evergreen" : " · Update"}
      </div>
      <h1 className="mt-2 text-3xl font-bold tracking-tight">{post.frontmatter.title}</h1>
      <p className="mt-3 text-lg text-steel/70">{post.frontmatter.description}</p>
      <hr className="my-8 border-band" />
      <AccessGate viewerTier={viewerTier} requiredTier={post.frontmatter.tier}>
        <Mdx source={post.body} />
      </AccessGate>
    </article>
  );
}
