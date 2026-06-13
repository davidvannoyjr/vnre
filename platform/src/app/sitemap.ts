import type { MetadataRoute } from "next";
import { getAllBlogPosts, getAllTutorials } from "@/lib/content";
import { TRACKS, type Track } from "@/lib/tiers";
import { siteConfig } from "../../site.config";

export default function sitemap(): MetadataRoute.Sitemap {
  const base = siteConfig.url;
  const staticPages = ["", "/pricing", "/blog", "/tutorials"].map((p) => ({
    url: `${base}${p}`,
    changeFrequency: "weekly" as const,
    priority: p === "" ? 1 : 0.7
  }));

  const tracks = (Object.keys(TRACKS) as Track[]).map((t) => ({
    url: `${base}/tutorials/${t}`,
    changeFrequency: "weekly" as const,
    priority: 0.6
  }));

  const posts = getAllBlogPosts().map((p) => ({
    url: `${base}/blog/${p.slug}`,
    lastModified: new Date(p.frontmatter.updatedDate ?? p.frontmatter.publishDate),
    changeFrequency: "monthly" as const,
    priority: 0.6
  }));

  const tutorials = getAllTutorials().map((t) => ({
    url: `${base}/tutorials/${t.track}/${t.slug}`,
    lastModified: new Date(t.frontmatter.updatedDate ?? t.frontmatter.publishDate),
    changeFrequency: "monthly" as const,
    priority: 0.6
  }));

  return [...staticPages, ...tracks, ...posts, ...tutorials];
}
