import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import Nodemailer from "next-auth/providers/nodemailer";
import { PrismaAdapter } from "@auth/prisma-adapter";
import { prisma, dbEnabled } from "@/lib/db";
import { isCoachEmail } from "@/lib/coaching";
import type { Tier } from "@/lib/tiers";

/**
 * Auth.js v5. When DATABASE_URL is set, uses the Prisma adapter with database
 * sessions and resolves the member's tier from the persisted User row (kept
 * current by the Stripe webhook). Without a database it falls back to JWT
 * sessions and everyone resolves to "free" — so the app boots with zero setup.
 *
 * Note: the email magic-link provider requires the database adapter, so it's
 * only enabled when both the SMTP server and DATABASE_URL are configured.
 */

declare module "next-auth" {
  interface Session {
    user: {
      id?: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
      tier: Tier;
      role: "member" | "coach";
    };
  }
}

const providers = [];

if (process.env.AUTH_EMAIL_SERVER && process.env.AUTH_EMAIL_FROM && dbEnabled) {
  providers.push(
    Nodemailer({
      server: process.env.AUTH_EMAIL_SERVER,
      from: process.env.AUTH_EMAIL_FROM
    })
  );
}

// Dev-only: a magic-link provider that prints the sign-in URL to the server
// console instead of sending email — so you can log in locally without SMTP.
// Never active in production, and only when no real SMTP is configured.
if (
  process.env.AUTH_DEV_LOGIN === "true" &&
  dbEnabled &&
  !process.env.AUTH_EMAIL_SERVER &&
  process.env.NODE_ENV !== "production"
) {
  providers.push(
    Nodemailer({
      server: { host: "localhost", port: 1025, auth: { user: "dev", pass: "dev" } },
      from: "dev@localhost",
      async sendVerificationRequest({ identifier, url }) {
        console.log(`\n🔑  DEV login link for ${identifier}:\n${url}\n`);
      }
    })
  );
}

if (process.env.AUTH_GOOGLE_ID && process.env.AUTH_GOOGLE_SECRET) {
  providers.push(
    Google({
      clientId: process.env.AUTH_GOOGLE_ID,
      clientSecret: process.env.AUTH_GOOGLE_SECRET
    })
  );
}

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: dbEnabled ? PrismaAdapter(prisma) : undefined,
  session: { strategy: dbEnabled ? "database" : "jwt" },
  providers,
  pages: {
    signIn: "/login"
  },
  callbacks: {
    // With the database strategy, `user` is the persisted row (carrying `tier`).
    // With JWT (no DB), `user` is absent and we default to "free".
    async session({ session, user }) {
      const dbUser = user as { id?: string; tier?: Tier; role?: string } | undefined;
      if (dbUser?.id) session.user.id = dbUser.id;
      session.user.tier = dbUser?.tier ?? "free";
      // Coach access comes from the stored role or the COACH_EMAILS allowlist.
      session.user.role =
        dbUser?.role === "coach" || isCoachEmail(session.user.email) ? "coach" : "member";
      return session;
    }
  }
});
