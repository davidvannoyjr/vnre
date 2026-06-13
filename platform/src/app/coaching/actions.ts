"use server";

import { revalidatePath } from "next/cache";
import { auth } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { STAGE_IDS, type Stage } from "@/lib/coaching";

/**
 * Mutations for the coaching workspace. Every action re-checks auth and
 * ownership server-side — never trust the form. Coach actions require role
 * "coach"; client actions require the caller to own the profile.
 */

async function requireCoach() {
  const session = await auth();
  if (!session?.user?.id || session.user.role !== "coach") {
    throw new Error("Coach access required.");
  }
  return session.user.id;
}

/** Resolve the profile id the caller may act on: coach who owns it, or its client. */
async function profileForCaller(profileId: string) {
  const session = await auth();
  if (!session?.user?.id) throw new Error("Not signed in.");
  const profile = await prisma.clientProfile.findUnique({ where: { id: profileId } });
  if (!profile) throw new Error("Not found.");
  const isOwnerCoach = session.user.role === "coach" && profile.coachId === session.user.id;
  const isClient = profile.clientId === session.user.id;
  if (!isOwnerCoach && !isClient) throw new Error("No access.");
  return { profile, userId: session.user.id, isCoach: isOwnerCoach };
}

// ── Coach: onboard a client ──────────────────────────────────────────────────

export async function inviteClient(formData: FormData) {
  const coachId = await requireCoach();
  const email = String(formData.get("email") || "").trim().toLowerCase();
  const name = String(formData.get("name") || "").trim() || null;
  if (!email) throw new Error("Email required.");

  const user = await prisma.user.upsert({
    where: { email },
    update: { name: name ?? undefined },
    create: { email, name }
  });

  await prisma.clientProfile.upsert({
    where: { clientId: user.id },
    update: { coachId, status: "active" },
    create: { clientId: user.id, coachId, plan: { create: { content: "" } } }
  });

  revalidatePath("/coaching/clients");
}

// ── Business plan (shared) ────────────────────────────────────────────────────

export async function savePlan(formData: FormData) {
  const profileId = String(formData.get("profileId"));
  const content = String(formData.get("content") || "");
  await profileForCaller(profileId);
  await prisma.businessPlan.upsert({
    where: { clientProfileId: profileId },
    update: { content },
    create: { clientProfileId: profileId, content }
  });
  revalidatePath("/coaching");
  revalidatePath(`/coaching/clients/${profileId}`);
}

// ── Notes (coach-authored; coach-private by default) ──────────────────────────

export async function addNote(formData: FormData) {
  const coachId = await requireCoach();
  const profileId = String(formData.get("profileId"));
  const body = String(formData.get("body") || "").trim();
  const sharedWithClient = formData.get("share") === "on";
  if (!body) return;
  const profile = await prisma.clientProfile.findUnique({ where: { id: profileId } });
  if (!profile || profile.coachId !== coachId) throw new Error("No access.");
  await prisma.coachingNote.create({
    data: { clientProfileId: profileId, authorId: coachId, body, sharedWithClient }
  });
  revalidatePath(`/coaching/clients/${profileId}`);
  revalidatePath("/coaching");
}

export async function toggleNoteShare(formData: FormData) {
  const coachId = await requireCoach();
  const noteId = String(formData.get("noteId"));
  const note = await prisma.coachingNote.findUnique({
    where: { id: noteId },
    include: { clientProfile: true }
  });
  if (!note || note.clientProfile.coachId !== coachId) throw new Error("No access.");
  await prisma.coachingNote.update({
    where: { id: noteId },
    data: { sharedWithClient: !note.sharedWithClient }
  });
  revalidatePath(`/coaching/clients/${note.clientProfileId}`);
}

// ── Tasks (mapped to the five-stage outline) ──────────────────────────────────

export async function addTask(formData: FormData) {
  const coachId = await requireCoach();
  const profileId = String(formData.get("profileId"));
  const title = String(formData.get("title") || "").trim();
  const detail = String(formData.get("detail") || "").trim();
  const stage = String(formData.get("stage") || "forge") as Stage;
  const due = String(formData.get("dueDate") || "");
  if (!title) return;
  if (!STAGE_IDS.includes(stage)) throw new Error("Invalid stage.");
  const profile = await prisma.clientProfile.findUnique({ where: { id: profileId } });
  if (!profile || profile.coachId !== coachId) throw new Error("No access.");
  await prisma.coachingTask.create({
    data: {
      clientProfileId: profileId,
      stage,
      title,
      detail,
      dueDate: due ? new Date(due) : null
    }
  });
  revalidatePath(`/coaching/clients/${profileId}`);
  revalidatePath("/coaching");
}

/** Toggle a task done/undone. Either the coach or the client may do this. */
export async function toggleTask(formData: FormData) {
  const taskId = String(formData.get("taskId"));
  const task = await prisma.coachingTask.findUnique({ where: { id: taskId } });
  if (!task) throw new Error("Not found.");
  const { profile } = await profileForCaller(task.clientProfileId);
  const done = task.status !== "done";
  await prisma.coachingTask.update({
    where: { id: taskId },
    data: { status: done ? "done" : "todo", completedAt: done ? new Date() : null }
  });
  revalidatePath("/coaching");
  revalidatePath(`/coaching/clients/${profile.id}`);
}
