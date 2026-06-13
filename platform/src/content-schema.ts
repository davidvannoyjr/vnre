import { z } from "zod";

/**
 * Frontmatter contract for every piece of content.
 * Validated at load time — a malformed file fails the build / content:check,
 * so the auto-publish pipeline can never ship a broken doc.
 */

export const tierEnum = z.enum(["free", "basic", "pro", "elite"]);
export const levelEnum = z.enum(["basic", "intermediate", "advanced"]);
export const trackEnum = z.enum(["chatgpt", "claude", "re-tools", "automation"]);
export const statusEnum = z.enum(["draft", "scheduled", "published"]);

export const blogFrontmatter = z.object({
  title: z.string().min(3),
  description: z.string().min(10),
  status: statusEnum.default("draft"),
  // Visible/published only when status=published OR publishDate has passed (publish-due flips it).
  publishDate: z.string(), // ISO date
  updatedDate: z.string().optional(),
  tier: tierEnum.default("free"),
  tags: z.array(z.string()).default([]),
  author: z.string().default("David Van Noy Jr."),
  // Evergreen = timeless reference; false = dated update/news.
  evergreen: z.boolean().default(true),
  // Source topic id from the queue (audit trail for auto-generated content).
  topicId: z.string().optional()
});

export const tutorialFrontmatter = z.object({
  title: z.string().min(3),
  description: z.string().min(10),
  status: statusEnum.default("draft"),
  publishDate: z.string(),
  updatedDate: z.string().optional(),
  track: trackEnum,
  level: levelEnum,
  tier: tierEnum,
  estimatedMinutes: z.number().int().positive().default(15),
  // Ordered prerequisites by slug, for the guided path.
  prerequisites: z.array(z.string()).default([]),
  tools: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
  topicId: z.string().optional()
});

export type BlogFrontmatter = z.infer<typeof blogFrontmatter>;
export type TutorialFrontmatter = z.infer<typeof tutorialFrontmatter>;
