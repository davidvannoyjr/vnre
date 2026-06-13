import "server-only";
import { prisma } from "@/lib/db";

/**
 * 1:1 coaching domain: the five-stage outline (DVN Coaching framework) and the
 * access-controlled loaders that back the client portal + coach views.
 *
 * Roles: a `coach` (DVN) manages many `ClientProfile`s; each links to one client
 * user. Notes are coach-private unless `sharedWithClient`. The business plan and
 * tasks are shared. Tasks hang off a stage of the outline below.
 */

export type Stage = "forge" | "conquer" | "anchor" | "architect" | "own";

export const STAGES: { id: Stage; name: string; blurb: string }[] = [
  { id: "forge", name: "Forge", blurb: "Identity foundation" },
  { id: "conquer", name: "Conquer", blurb: "Prospecting and production" },
  { id: "anchor", name: "Anchor", blurb: "Systems and consistency" },
  { id: "architect", name: "Architect", blurb: "Leverage and scale" },
  { id: "own", name: "Own", blurb: "Mastery and ownership" }
];

export const STAGE_IDS = STAGES.map((s) => s.id);

/** Emails granted coach access regardless of stored role (bootstrap). */
export function isCoachEmail(email?: string | null): boolean {
  if (!email) return false;
  const list = (process.env.COACH_EMAILS ?? "")
    .split(",")
    .map((e) => e.trim().toLowerCase())
    .filter(Boolean);
  return list.includes(email.toLowerCase());
}

/** The signed-in client's own profile with plan, shared notes, and tasks. */
export async function getMyClientWorkspace(userId: string) {
  return prisma.clientProfile.findUnique({
    where: { clientId: userId },
    include: {
      coach: { select: { name: true, email: true } },
      plan: true,
      notes: { where: { sharedWithClient: true }, orderBy: { createdAt: "desc" } },
      tasks: { orderBy: [{ stage: "asc" }, { sortOrder: "asc" }, { createdAt: "asc" }] }
    }
  });
}

/** All clients a coach manages (lightweight, for the roster). */
export async function listCoachClients(coachId: string) {
  return prisma.clientProfile.findMany({
    where: { coachId },
    orderBy: { createdAt: "asc" },
    include: {
      client: { select: { name: true, email: true, tier: true, stripeCurrentPeriodEnd: true } },
      tasks: { select: { status: true } }
    }
  });
}

/** One client's full profile for the coach — enforces coach ownership. */
export async function getClientForCoach(coachId: string, profileId: string) {
  const profile = await prisma.clientProfile.findUnique({
    where: { id: profileId },
    include: {
      client: { select: { id: true, name: true, email: true, tier: true, stripeCurrentPeriodEnd: true } },
      plan: true,
      notes: { orderBy: { createdAt: "desc" }, include: { author: { select: { name: true } } } },
      tasks: { orderBy: [{ stage: "asc" }, { sortOrder: "asc" }, { createdAt: "asc" }] }
    }
  });
  if (!profile || profile.coachId !== coachId) return null;
  return profile;
}
