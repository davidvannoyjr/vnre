#!/usr/bin/env node
/**
 * Validate every .mdx against the frontmatter schema. Fails CI on a bad doc so
 * the auto-publish pipeline can never ship something malformed.
 * Run: npm run content:check
 */
import fs from "node:fs";
import path from "node:path";
import matter from "gray-matter";
import { CONTENT_DIR } from "./lib/queue.mjs";

// Reuse the zod schema from src via a tiny inline copy of the rules would drift;
// instead validate the essentials here (kept in sync with src/content-schema.ts).
const TIERS = ["free", "basic", "pro", "elite"];
const LEVELS = ["basic", "intermediate", "advanced"];
const TRACKS = ["chatgpt", "claude", "re-tools", "automation"];
const STATUSES = ["draft", "scheduled", "published"];

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap((e) => {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) return walk(full);
    return e.name.endsWith(".mdx") ? [full] : [];
  });
}

const errors = [];
function check(cond, file, msg) {
  if (!cond) errors.push(`${path.relative(CONTENT_DIR, file)}: ${msg}`);
}

for (const file of walk(CONTENT_DIR)) {
  const fm = matter(fs.readFileSync(file, "utf8")).data;
  const isTutorial = file.includes(`${path.sep}tutorials${path.sep}`);

  check(typeof fm.title === "string" && fm.title.length >= 3, file, "title missing/too short");
  check(typeof fm.description === "string" && fm.description.length >= 10, file, "description missing/too short");
  check(STATUSES.includes(fm.status), file, `status must be one of ${STATUSES.join("|")}`);
  check(!!fm.publishDate && !isNaN(Date.parse(fm.publishDate)), file, "publishDate missing/invalid");
  check(TIERS.includes(fm.tier), file, `tier must be one of ${TIERS.join("|")}`);

  if (isTutorial) {
    check(TRACKS.includes(fm.track), file, `track must be one of ${TRACKS.join("|")}`);
    check(LEVELS.includes(fm.level), file, `level must be one of ${LEVELS.join("|")}`);
  }
}

if (errors.length) {
  console.error("Content validation failed:\n" + errors.map((e) => "  • " + e).join("\n"));
  process.exit(1);
}
console.log("All content valid.");
