import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import Nodemailer from "next-auth/providers/nodemailer";
import type { Tier } from "@/lib/tiers";

/**
 * Auth.js v5. Email magic-link (no passwords — friction-free for agents) + optional Google.
 * The member's active subscription tier is resolved from Stripe (see lib/stripe.ts)
 * and attached to the session. Until billing is wired, everyone resolves to "free".
 *
 * For production add a database adapter (e.g. @auth/prisma-adapter) to persist
 * users + the Stripe customer id. Scaffolded JWT-only here so it runs day one.
 */

declare module "next-auth" {
  interface Session {
    user: {
      id?: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
      tier: Tier;
    };
  }
}

const providers = [];

if (process.env.AUTH_EMAIL_SERVER && process.env.AUTH_EMAIL_FROM) {
  providers.push(
    Nodemailer({
      server: process.env.AUTH_EMAIL_SERVER,
      from: process.env.AUTH_EMAIL_FROM
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
  providers,
  pages: {
    signIn: "/login"
  },
  callbacks: {
    async session({ session }) {
      // TODO: resolve tier from Stripe subscription for session.user.email.
      // See lib/stripe.ts → getTierForCustomer(). Defaults to "free" pre-billing.
      session.user.tier = "free";
      return session;
    }
  }
});
