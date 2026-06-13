#!/usr/bin/env node
/**
 * Flip any `scheduled` .mdx whose publishDate has arrived to `published`.
 * Run on a schedule (content-publish GitHub Action). Idempotent.
 *
 * Note: the site already treats status=scheduled + past publishDate as live
 * (see src/lib/content.ts), so this step is for a clean, auditable status —
 * and to trigger a rebuild/commit when something goes live.
 */
import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { CONTENT_DIR } from "./lib/queue.mjs";

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) return walk(full);
    return e.name.endsWith(".mdx") ? [full] : [];
  });
}

let promoted = 0;
for (const file of walk(CONTENT_DIR)) {
  const raw = fs.readFileSync(file, "utf8");
  const parsed = matter(raw);
  const { status, publishDate } = parsed.data;
  if (status === "scheduled" && publishDate && new Date(publishDate).getTime() <= Date.now()) {
    parsed.data.status = "published";
    fs.writeFileSync(file, matter.stringify(parsed.content, parsed.data), "utf8");
    console.log(`Published: ${path.relative(CONTENT_DIR, file)}`);
    promoted += 1;
  }
}

console.log(promoted === 0 ? "Nothing due to publish." : `Promoted ${promoted} item(s).`);
