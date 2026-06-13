"use server";

import { revalidatePath } from "next/cache";
import { auth } from "@/lib/auth";
import { prisma, dbEnabled } from "@/lib/db";

/** Toggle a tutorial's completion for the signed-in member. */
export async function toggleLessonComplete(formData: FormData) {
  if (!dbEnabled) return;
  const session = await auth();
  if (!session?.user?.id) return;

  const slug = String(formData.get("slug") || "");
  const track = String(formData.get("track") || "");
  if (!slug) return;

  const existing = await prisma.lessonProgress.findUnique({
    where: { userId_slug: { userId: session.user.id, slug } }
  });

  if (existing) {
    await prisma.lessonProgress.delete({ where: { id: existing.id } });
  } else {
    await prisma.lessonProgress.create({ data: { userId: session.user.id, slug } });
  }

  revalidatePath(`/tutorials/${track}/${slug}`);
  revalidatePath("/dashboard");
}
