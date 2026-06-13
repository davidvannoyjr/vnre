import "server-only";
import { prisma } from "@/lib/db";

/** Slugs of tutorials the user has marked complete. */
export async function getCompletedSlugs(userId: string): Promise<Set<string>> {
  const rows = await prisma.lessonProgress.findMany({
    where: { userId },
    select: { slug: true }
  });
  return new Set(rows.map((r) => r.slug));
}

export async function isCompleted(userId: string, slug: string): Promise<boolean> {
  const row = await prisma.lessonProgress.findUnique({
    where: { userId_slug: { userId, slug } }
  });
  return !!row;
}

export async function completedCount(userId: string): Promise<number> {
  return prisma.lessonProgress.count({ where: { userId } });
}
