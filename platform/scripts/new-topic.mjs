#!/usr/bin/env node
/**
 * Append a topic to the queue as `proposed`.
 * Usage:
 *   node scripts/new-topic.mjs --type tutorial --track chatgpt --level basic --tier basic --title "..." --angle "..."
 *   node scripts/new-topic.mjs --type blog --tier free --title "..." --angle "..."
 */
import fs from "node:fs";
import { QUEUE_PATH, readQueue, slugify } from "./lib/queue.mjs";

function arg(flag, def = "") {
  const i = process.argv.indexOf(flag);
  return i !== -1 && process.argv[i + 1] ? process.argv[i + 1] : def;
}

const type = arg("--type", "tutorial");
const title = arg("--title");
if (!title) {
  console.error("Missing --title");
  process.exit(1);
}

const ym = new Date().toISOString().slice(0, 7);
const id = `${ym}-${slugify(title)}`;

const { doc } = readQueue();
const topics = doc.get("topics");

const entry = {
  id,
  type,
  ...(type === "tutorial"
    ? { track: arg("--track", "chatgpt"), level: arg("--level", "basic"), tier: arg("--tier", "basic") }
    : { tier: arg("--tier", "free") }),
  title,
  angle: arg("--angle", ""),
  status: "proposed"
};

topics.add(entry);
fs.writeFileSync(QUEUE_PATH, doc.toString(), "utf8");
console.log(`Added topic ${id} (status: proposed). Approve it by setting status: approved.`);
