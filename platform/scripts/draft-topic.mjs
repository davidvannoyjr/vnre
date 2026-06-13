#!/usr/bin/env node
/**
 * Draft every `approved` topic in the queue: call Claude to write the .mdx in
 * DVN's voice, save it as status `scheduled` with a publishDate, and flip the
 * queue entry to `drafted`. This is the engine of the approve-topics →
 * auto-publish pipeline. Run locally ("node scripts/draft-topic.mjs") or by the
 * content-draft GitHub Action.
 *
 * Requires ANTHROPIC_API_KEY. Model: CONTENT_MODEL (default claude-opus-4-8).
 *
 * Flags:
 *   --dry        Print what would be drafted; no API calls, no writes.
 *   --id <id>    Draft only this topic id.
 *   --stagger N  Days between scheduled publishDates (default 3).
 */
import fs from "node:fs";
import { readQueue, setTopicStatus, slugify, targetPath } from "./lib/queue.mjs";

const DRY = process.argv.includes("--dry");
const ONLY = (() => {
  const i = process.argv.indexOf("--id");
  return i !== -1 ? process.argv[i + 1] : null;
})();
const STAGGER = (() => {
  const i = process.argv.indexOf("--stagger");
  return i !== -1 ? Number(process.argv[i + 1]) : 3;
})();

const MODEL = process.env.CONTENT_MODEL || "claude-opus-4-8";
const API_KEY = process.env.ANTHROPIC_API_KEY;

const VOICE = `You are writing as David Van Noy Jr. (DVN) — broker/owner of Van Noy Real Estate and founder of DVN Coaching, 23+ years in residential real estate. Voice rules (non-negotiable):
- Direct, blunt, declarative. Short sentences, active voice, strong verbs.
- ROI-driven. Simple > clever. Proven > experimental. No hype, no hedging.
- BANNED: "I'd be happy to", "Great question", "It's important to note", motivational clichés ("crush it", "level up", "you got this"), generic AI filler.
- Talk to a working real estate agent as a peer professional. Every framework reads as proprietary to VNRE/DVN Coaching — never attribute external brands/methodologies.
- Concrete and actionable. Give the exact prompt, the exact steps, the real win. End tutorials with a "Your win" call to action.`;

function frontmatter(topic, slug, publishDate) {
  const common = [
    `title: ${JSON.stringify(topic.title)}`,
    `description: ${JSON.stringify(topic.angle || topic.title)}`,
    `status: scheduled`,
    `publishDate: ${JSON.stringify(publishDate)}`,
    `tier: ${topic.tier}`,
    `topicId: ${JSON.stringify(topic.id)}`
  ];
  if (topic.type === "tutorial") {
    return [
      "---",
      ...common,
      `track: ${topic.track}`,
      `level: ${topic.level}`,
      `estimatedMinutes: 15`,
      `tags: []`,
      `tools: []`,
      "---",
      ""
    ].join("\n");
  }
  return ["---", ...common, `evergreen: true`, `tags: []`, "---", ""].join("\n");
}

async function draftBody(topic) {
  const kind =
    topic.type === "tutorial"
      ? `a ${topic.level}-level tutorial in the "${topic.track}" track`
      : "an evergreen blog post";
  const prompt = `${VOICE}

Write ${kind} for real estate agents.
Title: ${topic.title}
Angle: ${topic.angle || "(none given — choose the highest-ROI angle)"}

Output ONLY the Markdown body (no frontmatter, no title H1 — the title is rendered separately). Use ## and ### headings, short paragraphs, bullet lists, and fenced code blocks for any prompts or scripts. 500–900 words. Make it immediately usable by a working agent today.`;

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": API_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 4000,
      messages: [{ role: "user", content: prompt }]
    })
  });

  if (!res.ok) {
    throw new Error(`Anthropic API ${res.status}: ${await res.text()}`);
  }
  const data = await res.json();
  if (data.stop_reason === "refusal") {
    throw new Error(`Model refused to draft topic ${topic.id}`);
  }
  return data.content.filter((b) => b.type === "text").map((b) => b.text).join("").trim();
}

async function main() {
  const { data } = readQueue();
  let approved = (data.topics || []).filter((t) => t.status === "approved");
  if (ONLY) approved = approved.filter((t) => t.id === ONLY);

  if (approved.length === 0) {
    console.log("No approved topics to draft.");
    return;
  }
  if (!API_KEY && !DRY) {
    console.error("ANTHROPIC_API_KEY not set. Use --dry to preview without drafting.");
    process.exit(1);
  }

  let offset = 1;
  for (const topic of approved) {
    const slug = slugify(topic.title);
    const out = targetPath(topic, slug);
    const publishDate = new Date(Date.now() + offset * STAGGER * 86400000)
      .toISOString()
      .slice(0, 10);
    offset += 1;

    if (DRY) {
      console.log(`[dry] would draft ${topic.id} → ${out} (publish ${publishDate})`);
      continue;
    }

    console.log(`Drafting ${topic.id} …`);
    const body = await draftBody(topic);
    fs.mkdirSync(out.replace(/\/[^/]+$/, ""), { recursive: true });
    fs.writeFileSync(out, frontmatter(topic, slug, publishDate) + body + "\n", "utf8");
    setTopicStatus(topic.id, "drafted");
    console.log(`  ✓ wrote ${out} (scheduled ${publishDate})`);
  }
  console.log("\nDone. Review the drafts, then commit. publish-due.mjs will go live on schedule.");
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
