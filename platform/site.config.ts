/**
 * Single source of truth for brand + product config.
 * Rename the product in ONE place here — everything reads from this.
 */
export const siteConfig = {
  // Working name — change to your final brand and it propagates everywhere.
  name: "DVN AI Lab",
  tagline: "AI skills for real estate agents who list.",
  description:
    "A subscription platform that teaches real estate agents how to build real AI skills into their business — from first prompt to fully automated systems. Built by David Van Noy Jr., DVN Coaching.",
  url: process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000",
  author: "David Van Noy Jr.",
  contactEmail: "david@vannoyre.com",
  social: {
    youtube: "",
    instagram: "",
    linkedin: ""
  },
  // Brand voice reminder for any UI copy or auto-generated content.
  // Full rules: ../claude/CLAUDE.md §2 + the dvn-voice skill.
  voice:
    "Direct, blunt, declarative. Short sentences, active voice, strong verbs. ROI-driven. No hype, no hedging, no clichés."
} as const;

export type SiteConfig = typeof siteConfig;
