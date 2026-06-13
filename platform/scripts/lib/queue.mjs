import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import YAML from "yaml";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const ROOT = path.resolve(__dirname, "..", "..");
export const QUEUE_PATH = path.join(ROOT, "content", "topics", "queue.yaml");
export const CONTENT_DIR = path.join(ROOT, "content");

export function readQueue() {
  const raw = fs.readFileSync(QUEUE_PATH, "utf8");
  return { doc: YAML.parseDocument(raw), data: YAML.parse(raw) };
}

/** Persist a status change for one topic id, preserving comments/formatting. */
export function setTopicStatus(id, status) {
  const { doc } = readQueue();
  const topics = doc.get("topics");
  for (const item of topics.items) {
    if (item.get("id") === id) {
      item.set("status", status);
      break;
    }
  }
  fs.writeFileSync(QUEUE_PATH, doc.toString(), "utf8");
}

export function slugify(s) {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")
    .slice(0, 80);
}

/** Where a drafted topic's .mdx file should live. */
export function targetPath(topic, slug) {
  if (topic.type === "tutorial") {
    return path.join(CONTENT_DIR, "tutorials", topic.track, `${slug}.mdx`);
  }
  return path.join(CONTENT_DIR, "blog", `${slug}.mdx`);
}
