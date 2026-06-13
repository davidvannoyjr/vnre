import { describe, it, expect } from "vitest";
import { canAccess, planForLevel, PLANS, PUBLIC_PLANS } from "@/lib/tiers";

describe("tier gating", () => {
  it("higher plans clear lower-tier content", () => {
    expect(canAccess("pro", "basic")).toBe(true);
    expect(canAccess("pro", "pro")).toBe(true);
    expect(canAccess("coaching", "elite")).toBe(true);
    expect(canAccess("elite", "coaching")).toBe(false);
  });

  it("lower plans cannot reach higher-tier content", () => {
    expect(canAccess("basic", "pro")).toBe(false);
    expect(canAccess("free", "basic")).toBe(false);
  });

  it("advanced content unlocks at Elite", () => {
    expect(planForLevel("advanced").id).toBe("elite");
    expect(planForLevel("basic").id).toBe("basic");
  });

  it("coaching is hidden from public pricing", () => {
    expect(PLANS.some((p) => p.id === "coaching")).toBe(true);
    expect(PUBLIC_PLANS.some((p) => p.id === "coaching")).toBe(false);
  });
});
