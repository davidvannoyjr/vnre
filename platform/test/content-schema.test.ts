import { describe, it, expect } from "vitest";
import { tutorialFrontmatter, blogFrontmatter } from "@/content-schema";

describe("frontmatter schema", () => {
  it("accepts a valid tutorial and applies defaults", () => {
    const fm = tutorialFrontmatter.parse({
      title: "Test Lesson",
      description: "A valid description over ten chars.",
      publishDate: "2026-06-13",
      track: "chatgpt",
      level: "basic",
      tier: "basic"
    });
    expect(fm.status).toBe("draft");
    expect(fm.estimatedMinutes).toBe(15);
    expect(fm.tools).toEqual([]);
  });

  it("rejects a tutorial with an invalid track", () => {
    expect(() =>
      tutorialFrontmatter.parse({
        title: "Bad",
        description: "Long enough description.",
        publishDate: "2026-06-13",
        track: "nope",
        level: "basic",
        tier: "basic"
      })
    ).toThrow();
  });

  it("blog posts default to evergreen + free", () => {
    const fm = blogFrontmatter.parse({
      title: "Post",
      description: "Long enough description.",
      publishDate: "2026-06-13"
    });
    expect(fm.evergreen).toBe(true);
    expect(fm.tier).toBe("free");
  });
});
