/**
 * Subscription tiers, content difficulty levels, and AI tracks.
 * Gating rule: a member can view content whose `tier` rank is <= their plan rank.
 */

export type Tier = "free" | "basic" | "pro" | "elite" | "coaching";
export type Level = "basic" | "intermediate" | "advanced";
export type Track = "chatgpt" | "claude" | "re-tools" | "automation";

export const TIER_RANK: Record<Tier, number> = {
  free: 0,
  basic: 1,
  pro: 2,
  elite: 3,
  coaching: 4
};

export interface TierPlan {
  id: Tier;
  name: string;
  price: number; // USD / month
  blurb: string;
  features: string[];
  // Difficulty levels unlocked at this plan.
  unlocks: Level[];
  // Maps to STRIPE_PRICE_* env var. null for the free tier.
  stripeEnv: string | null;
  highlight?: boolean;
  // Invite-only tiers are hidden from public pricing (coach onboards directly).
  invite?: boolean;
}

export const PLANS: TierPlan[] = [
  {
    id: "free",
    name: "Free",
    price: 0,
    blurb: "Evergreen blog + the first lesson in every track. Lead-gen front door.",
    features: [
      "Full evergreen blog & AI updates",
      "Intro lesson in all four tracks",
      "Weekly 'what changed in AI' digest"
    ],
    unlocks: [],
    stripeEnv: null
  },
  {
    id: "basic",
    name: "Basic",
    price: 29,
    blurb: "Get off zero. The foundational AI skills every agent needs.",
    features: [
      "All Basic-level tutorials, all four tracks",
      "Copy-paste prompt library (starter)",
      "Tool setup guides (ChatGPT, Claude, FUB AI)",
      "Member-only blog deep dives"
    ],
    unlocks: ["basic"],
    stripeEnv: "STRIPE_PRICE_BASIC",
    highlight: false
  },
  {
    id: "pro",
    name: "Pro",
    price: 79,
    blurb: "Build real systems. For producing agents who want leverage.",
    features: [
      "Everything in Basic",
      "All Intermediate tutorials",
      "Full prompt + automation template library",
      "Monthly live AI implementation workshop (recording)",
      "Workflow blueprints (listings, follow-up, content)"
    ],
    unlocks: ["basic", "intermediate"],
    stripeEnv: "STRIPE_PRICE_PRO",
    highlight: true
  },
  {
    id: "elite",
    name: "Elite",
    price: 199,
    blurb: "Operator-level. Automate your business end to end.",
    features: [
      "Everything in Pro",
      "All Advanced tutorials (MCP, voice agents, custom builds)",
      "Done-with-you build sessions (quarterly)",
      "Priority topic requests",
      "Direct line into DVN Coaching"
    ],
    unlocks: ["basic", "intermediate", "advanced"],
    stripeEnv: "STRIPE_PRICE_ELITE"
  },
  {
    id: "coaching",
    name: "1:1 Coaching",
    price: 1000,
    blurb: "Private monthly coaching with DVN. Invite-only — capped at 10–12 clients.",
    features: [
      "Everything in Elite",
      "Private 1:1 coaching workspace",
      "Your living business plan",
      "Tasks mapped to your coaching outline (Forge → Own)",
      "Coaching notes shared with you",
      "Direct accountability with DVN"
    ],
    unlocks: ["basic", "intermediate", "advanced"],
    stripeEnv: "STRIPE_PRICE_COACHING",
    invite: true
  }
];

/** Plans shown on the public pricing page (invite-only tiers excluded). */
export const PUBLIC_PLANS = PLANS.filter((p) => !p.invite);

export const TRACKS: Record<Track, { name: string; blurb: string }> = {
  chatgpt: {
    name: "ChatGPT & OpenAI",
    blurb: "Prompting, custom GPTs, writing, and listing content with the tool most agents start with."
  },
  claude: {
    name: "Claude & Agents",
    blurb: "Long-document work, skills, MCP, and the automation systems that run a listing business."
  },
  "re-tools": {
    name: "Real Estate AI Tools",
    blurb: "CMA/listing AI, AI dialers, and voice agents (inbound + routing) built for production."
  },
  automation: {
    name: "Automation & CRM AI",
    blurb: "Zapier / Make / n8n, Follow Up Boss AI, and wiring your tools into one system."
  }
};

export const LEVELS: Record<Level, { name: string; order: number; blurb: string }> = {
  basic: { name: "Basic", order: 1, blurb: "New to AI. Get a real win this week." },
  intermediate: { name: "Intermediate", order: 2, blurb: "Comfortable with the tools. Build repeatable systems." },
  advanced: { name: "Advanced", order: 3, blurb: "Operator level. Automate and integrate." }
};

/** Can a member on `plan` view content requiring `requiredTier`? */
export function canAccess(plan: Tier, requiredTier: Tier): boolean {
  return TIER_RANK[plan] >= TIER_RANK[requiredTier];
}

/** Lowest plan that unlocks a given difficulty level — used for upgrade CTAs. */
export function planForLevel(level: Level): TierPlan {
  return PLANS.find((p) => p.unlocks.includes(level)) ?? PLANS[0];
}
