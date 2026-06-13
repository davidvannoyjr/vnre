import { getAllBlogPosts } from "@/lib/content";
import { siteConfig } from "../../../site.config";

export const dynamic = "force-static";

function esc(s: string) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

/** RSS 2.0 feed of published blog posts + updates. */
export function GET() {
  const posts = getAllBlogPosts();
  const items = posts
    .map(
      (p) => `    <item>
      <title>${esc(p.frontmatter.title)}</title>
      <link>${siteConfig.url}/blog/${p.slug}</link>
      <guid>${siteConfig.url}/blog/${p.slug}</guid>
      <pubDate>${new Date(p.frontmatter.publishDate).toUTCString()}</pubDate>
      <description>${esc(p.frontmatter.description)}</description>
    </item>`
    )
    .join("\n");

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${esc(siteConfig.name)} — Blog &amp; AI Updates</title>
    <link>${siteConfig.url}</link>
    <description>${esc(siteConfig.description)}</description>
    <language>en-us</language>
${items}
  </channel>
</rss>`;

  return new Response(xml, { headers: { "Content-Type": "application/xml; charset=utf-8" } });
}
