import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import {
  blogFrontmatter,
  tutorialFrontmatter,
  type BlogFrontmatter,
  type TutorialFrontmatter
} from "@/content-schema";
import { LEVELS, type Level, type Track } from "@/lib/tiers";

/**
 * Git-as-CMS loader. Content lives as .mdx files under /content.
 * The repo IS the CMS — committing a file publishes it (subject to status/date).
 */

const CONTENT_ROOT = path.join(process.cwd(), "content");
const BLOG_DIR = path.join(CONTENT_ROOT, "blog");
const TUTORIALS_DIR = path.join(CONTENT_ROOT, "tutorials");

export interface BlogPost {
  slug: string;
  frontmatter: BlogFrontmatter;
  body: string;
}

export interface Tutorial {
  slug: string;
  track: Track;
  level: Level;
  frontmatter: TutorialFrontmatter;
  body: string;
}

function walk(dir: string): string[] {
  if (!fs.existsSync(dir)) return [];
  const out: string[] = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(full));
    else if (entry.name.endsWith(".mdx")) out.push(full);
  }
  return out;
}

/** A doc is live if status=published, or status=scheduled and the date has passed. */
function isLive(status: string, publishDate: string): boolean {
  if (status === "published") return true;
  if (status === "scheduled") return new Date(publishDate).getTime() <= Date.now();
  return false;
}

function slugFromFile(file: string, base: string): string {
  return path
    .relative(base, file)
    .replace(/\.mdx$/, "")
    .split(path.sep)
    .pop()!;
}

// ── Blog ────────────────────────────────────────────────────────────────────

export function getAllBlogPosts({ includeUnpublished = false } = {}): BlogPost[] {
  return walk(BLOG_DIR)
    .map((file) => {
      const raw = fs.readFileSync(file, "utf8");
      const { data, content } = matter(raw);
      const frontmatter = blogFrontmatter.parse(data);
      return { slug: slugFromFile(file, BLOG_DIR), frontmatter, body: content };
    })
    .filter((p) => includeUnpublished || isLive(p.frontmatter.status, p.frontmatter.publishDate))
    .sort(
      (a, b) =>
        new Date(b.frontmatter.publishDate).getTime() - new Date(a.frontmatter.publishDate).getTime()
    );
}

export function getBlogPost(slug: string): BlogPost | null {
  return getAllBlogPosts({ includeUnpublished: true }).find((p) => p.slug === slug) ?? null;
}

// ── Tutorials ─────────────────────────────────────────────────────────────────

export function getAllTutorials({ includeUnpublished = false } = {}): Tutorial[] {
  return walk(TUTORIALS_DIR)
    .map((file) => {
      const raw = fs.readFileSync(file, "utf8");
      const { data, content } = matter(raw);
      const frontmatter = tutorialFrontmatter.parse(data);
      return {
        slug: slugFromFile(file, TUTORIALS_DIR),
        track: frontmatter.track,
        level: frontmatter.level,
        frontmatter,
        body: content
      };
    })
    .filter((t) => includeUnpublished || isLive(t.frontmatter.status, t.frontmatter.publishDate))
    .sort((a, b) => a.frontmatter.title.localeCompare(b.frontmatter.title));
}

export function getTutorial(slug: string): Tutorial | null {
  return getAllTutorials({ includeUnpublished: true }).find((t) => t.slug === slug) ?? null;
}

export function getTutorialsByTrack(track: Track): Tutorial[] {
  return getAllTutorials().filter((t) => t.track === track);
}

/** Ordered guided path within a track: basic → intermediate → advanced, then title. */
export function getTrackPath(track: Track): Tutorial[] {
  return getTutorialsByTrack(track).sort((a, b) => {
    const byLevel = LEVELS[a.level].order - LEVELS[b.level].order;
    return byLevel !== 0 ? byLevel : a.frontmatter.title.localeCompare(b.frontmatter.title);
  });
}

/** Previous/next lesson in a track's guided path, for in-lesson navigation. */
export function getTutorialNeighbors(track: Track, slug: string): {
  prev: Tutorial | null;
  next: Tutorial | null;
} {
  const path = getTrackPath(track);
  const i = path.findIndex((t) => t.slug === slug);
  if (i === -1) return { prev: null, next: null };
  return { prev: path[i - 1] ?? null, next: path[i + 1] ?? null };
}
