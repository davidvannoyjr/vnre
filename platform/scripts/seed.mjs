#!/usr/bin/env node
/**
 * Seed local dev data: make the COACH_EMAILS coach exist, and create one sample
 * coaching client with a plan, a few stage tasks, and a note (one shared) so you
 * can click through both sides of the workspace immediately.
 *
 *   DATABASE_URL=... COACH_EMAILS=david@vannoyre.com node scripts/seed.mjs
 *
 * Idempotent. Does NOT touch Stripe — billing is exercised via the real
 * checkout flow (see docs/STRIPE.md).
 */
import { PrismaClient } from "@prisma/client";

if (!process.env.DATABASE_URL) {
  console.error("DATABASE_URL not set. Start Postgres (docker compose up -d), set it, then `npm run db:push`.");
  process.exit(1);
}

const prisma = new PrismaClient();
const coachEmail = (process.env.COACH_EMAILS ?? "david@vannoyre.com").split(",")[0].trim().toLowerCase();
const clientEmail = "test-client@example.com";

async function main() {
  const coach = await prisma.user.upsert({
    where: { email: coachEmail },
    update: { role: "coach" },
    create: { email: coachEmail, name: "David Van Noy Jr.", role: "coach" }
  });

  const client = await prisma.user.upsert({
    where: { email: clientEmail },
    update: {},
    create: { email: clientEmail, name: "Test Client", role: "member" }
  });

  const profile = await prisma.clientProfile.upsert({
    where: { clientId: client.id },
    update: { coachId: coach.id },
    create: {
      clientId: client.id,
      coachId: coach.id,
      plan: { create: { content: "# 2026 Plan\n\nTarget: 30 listing sides.\nDaily: 3 hrs prospecting." } }
    }
  });

  // Only seed sample tasks/notes once.
  const existing = await prisma.coachingTask.count({ where: { clientProfileId: profile.id } });
  if (existing === 0) {
    await prisma.coachingTask.createMany({
      data: [
        { clientProfileId: profile.id, stage: "forge", title: "Write your one-line identity statement" },
        { clientProfileId: profile.id, stage: "conquer", title: "150 dials/day for 5 days", detail: "Log contacts in FUB" },
        { clientProfileId: profile.id, stage: "anchor", title: "Stand up the daily lead-attention routine" }
      ]
    });
    await prisma.coachingNote.create({
      data: { clientProfileId: profile.id, authorId: coach.id, body: "Strong week. Hold the prospecting line.", sharedWithClient: true }
    });
    await prisma.coachingNote.create({
      data: { clientProfileId: profile.id, authorId: coach.id, body: "Private: push harder on price discipline next call." }
    });
  }

  console.log(`Seeded:\n  coach:  ${coachEmail}\n  client: ${clientEmail} (profile ${profile.id})`);
  console.log("Log in as each (magic link) to see both sides at /coaching.");
}

main()
  .catch((e) => {
    console.error(e.message);
    process.exit(1);
  })
  .finally(() => prisma.$disconnect());
