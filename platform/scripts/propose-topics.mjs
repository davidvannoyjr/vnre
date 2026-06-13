#!/usr/bin/env node
/**
 * Auto-fill the backlog: ask Claude for fresh topic ideas across the four tracks
 * and three levels, then append them to the queue as `proposed` for DVN to
 * approve. This is the front of the pipeline — proposing is safe to automate;
 * approval stays manual.
 *
 *   ANTHROPIC_API_KEY=... node scripts/propose-topics.mjs --count 6
 *
 * Flags:
 *   --count N   How many ideas to request (default 6).
 *   --dry       Print ideas; don't write to the queue.
 */
import fs from "node:fs";
import { QUEUE_PATH, readQueue, slugify } from "./lib/queue.mjs";

const COUNT = (() => {
  const i = process.argv.indexOf("--count");
  return i !== -1 ? Number(process.argv[i + 1]) : 6;
})();
const DRY = process.argv.includes("--dry");

const MODEL = process.env.CONTENT_MODEL || "claude-opus-4-8";
const API_KEY = process.env.ANTHROPIC_API_KEY;

const TRACKS = ["chatgpt", "claude", "re-tools", "automation"];
const LEVELS = ["basic", "intermediate", "advanced"];
const TIER_BY_LEVEL = { basic: "basic", intermediate: "pro", advanced: "elite" };

function tierFor(idea) {
  if (idea.type === "blog") return "free";
  return TIER_BY_LEVEL[idea.level] ?? "basic";
}

async function getIdeas(existingTitles) {
  const prompt = `You generate content topic ideas for David Van Noy Jr.'s platform that teaches real estate agents to build AI into their business.

Run every idea through this filter — reject anything that fails:
1. Does it drive listings, GCI, or coaching revenue?
2. ROI-positive within 90 days?
3. Simple enough for a working agent to execute?

Tracks: chatgpt, claude, re-tools (real-estate AI tools, dialers, voice agents), automation (Zapier/Make/n8n, Follow Up Boss AI).
Levels (tutorials): basic, intermediate, advanced.

Propose ${COUNT} NEW ideas, spread across tracks and levels. Mostly tutorials; one or two "blog" ideas are fine (timeless evergreen or a dated AI update).

Do NOT repeat or closely overlap these existing titles:
${existingTitles.map((t) => `- ${t}`).join("\n")}

Output ONLY a JSON array, no prose. Each item:
{"type":"tutorial"|"blog","track":"chatgpt|claude|re-tools|automation","level":"basic|intermediate|advanced","title":"...","angle":"one concrete sentence on the hook/payoff"}
For "blog" items, track/level may be omitted.`;

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": API_KEY,
      "anthropic-version": "2023-06-01"
    },
    body: JSON.stringify({ model: MODEL, max_tokens: 2000, messages: [{ role: "user", content: prompt }] })
  });
  if (!res.ok) throw new Error(`Anthropic API ${res.status}: ${await res.text()}`);
  const data = await res.json();
  if (data.stop_reason === "refusal") throw new Error("Model refused.");
  const text = data.content.filter((b) => b.type === "text").map((b) => b.text).join("");
  const json = text.slice(text.indexOf("["), text.lastIndexOf("]") + 1);
  return JSON.parse(json);
}

function valid(idea) {
  if (idea.type === "blog") return typeof idea.title === "string";
  return (
    typeof idea.title === "string" &&
    TRACKS.includes(idea.track) &&
    LEVELS.includes(idea.level)
  );
}

async function main() {
  if (!API_KEY) {
    console.error("ANTHROPIC_API_KEY not set.");
    process.exit(1);
  }
  const { doc, data } = readQueue();
  const existing = new Set((data.topics || []).map((t) => slugify(t.title)));
  const existingTitles = (data.topics || []).map((t) => t.title);

  const ideas = (await getIdeas(existingTitles)).filter(valid);
  const ym = new Date().toISOString().slice(0, 7);
  const topics = doc.get("topics");

  let added = 0;
  for (const idea of ideas) {
    const slug = slugify(idea.title);
    if (existing.has(slug)) continue;
    existing.add(slug);
    const entry = {
      id: `${ym}-${slug}`,
      type: idea.type === "blog" ? "blog" : "tutorial",
      ...(idea.type === "blog"
        ? { tier: "free" }
        : { track: idea.track, level: idea.level, tier: tierFor(idea) }),
      title: idea.title,
      angle: idea.angle || "",
      status: "proposed"
    };
    if (DRY) {
      console.log(`[dry] ${entry.id} (${entry.type}/${entry.track ?? "blog"}/${entry.level ?? ""})`);
    } else {
      topics.add(entry);
      added += 1;
    }
  }

  if (!DRY && added > 0) fs.writeFileSync(QUEUE_PATH, doc.toString(), "utf8");
  console.log(DRY ? "Dry run complete." : `Added ${added} proposed topic(s). Review and approve in queue.yaml.`);
}

main().catch((err) => {
  console.error(err.message);
  process.exit(1);
});
