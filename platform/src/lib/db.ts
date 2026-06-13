import { PrismaClient } from "@prisma/client";

/**
 * Prisma singleton. Safe to import even when DATABASE_URL is unset — the client
 * connects lazily on first query, so the app still boots without a database
 * (auth falls back to JWT, everyone resolves to "free"). See lib/auth.ts.
 */
const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma = globalForPrisma.prisma ?? new PrismaClient();

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

export const dbEnabled = !!process.env.DATABASE_URL;
