import { describe, it, expect } from "vitest";
import { getAllBlogPosts, getAllTutorials, getTrackPath } from "@/lib/content";
import { TRACKS, LEVELS } from "@/lib/tiers";

describe("content loader", () => {
  it("loads published blog posts including the welcome post", () => {
    const posts = getAllBlogPosts();
    expect(posts.length).toBeGreaterThan(0);
    expect(posts.some((p) => p.slug === "welcome-ai-for-real-estate-agents")).toBe(true);
  });

  it("every tutorial has a known track and level", () => {
    const tutorials = getAllTutorials();
    expect(tutorials.length).toBeGreaterThan(0);
    for (const t of tutorials) {
      expect(t.track in TRACKS).toBe(true);
      expect(t.level in LEVELS).toBe(true);
    }
  });

  it("guided path is ordered basic → advanced", () => {
    const path = getTrackPath("chatgpt");
    const orders = path.map((t) => LEVELS[t.level].order);
    const sorted = [...orders].sort((a, b) => a - b);
    expect(orders).toEqual(sorted);
  });
});
