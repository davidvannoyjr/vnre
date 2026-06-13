import Link from "next/link";
import { siteConfig } from "../../../site.config";

export const metadata = {
  title: "About & FAQ",
  description: "Who's behind the platform and how it works."
};

const FAQ = [
  {
    q: "Who is this for?",
    a: "Working real estate agents who want AI to drive more listings — not a computer science degree. From your first prompt to a business that runs on systems."
  },
  {
    q: "Do I need to be technical?",
    a: "No. The Basic track assumes you've never touched AI. Every lesson is the exact prompt, the exact steps, and the real win — built to execute today, not someday."
  },
  {
    q: "How do the levels work?",
    a: "Three levels in every track — basic, intermediate, advanced. Start where you actually are. Basic gets you off zero; intermediate builds repeatable systems; advanced automates and integrates."
  },
  {
    q: "How often is there new content?",
    a: "Weekly. The tools change monthly — this platform keeps up so you don't have to. Evergreen tutorials that stay true, plus dated updates on what actually matters."
  },
  {
    q: "Can I cancel anytime?",
    a: "Yes. Subscriptions are month-to-month. No contracts."
  },
  {
    q: "What's the 1:1 Coaching tier?",
    a: "Private monthly coaching with DVN for producing agents — a living business plan, an accountability outline, and direct access. It's invite-only and capped, so it's an application, not a checkout button."
  }
];

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-16">
      <h1 className="text-3xl font-bold tracking-tight">Why this exists</h1>
      <div className="prose-vnre mt-6">
        <p>
          Most agents read think-pieces about AI and never change a thing. The agent who actually
          builds the skill takes the listings. This platform exists to make you that agent.
        </p>
        <p>
          It's built by <strong>{siteConfig.author}</strong> — broker/owner of Van Noy Real Estate
          and founder of DVN Coaching. 23+ years in residential real estate, $500M+ closed, ~13
          years coaching producing agents. The same AI systems taught here run a real solo listing
          operation every day. Nothing theoretical. Proven, simple, ROI-first.
        </p>
        <h2>How it's built</h2>
        <p>
          Four tracks — ChatGPT, Claude, Real Estate AI Tools, and Automation &amp; CRM AI. Three
          levels each. Pick a tool, start where you are, get a win this week, then build. New
          content lands weekly, and every piece is written to be used, not admired.
        </p>
        <h2>The promise</h2>
        <p>
          AI won't replace you. It removes the friction that keeps you off the phone and out of
          listing appointments. Used right, it's the cheapest leverage you will ever buy.
        </p>
      </div>

      <div className="mt-8">
        <Link href="/pricing" className="inline-block rounded-md bg-accent px-6 py-3 font-medium text-white hover:opacity-90">
          See plans
        </Link>
      </div>

      <h2 className="mt-16 text-2xl font-bold tracking-tight">FAQ</h2>
      <dl className="mt-6 divide-y divide-band">
        {FAQ.map((item) => (
          <div key={item.q} className="py-5">
            <dt className="font-semibold">{item.q}</dt>
            <dd className="mt-1 text-steel/70">{item.a}</dd>
          </div>
        ))}
      </dl>

      <p className="mt-10 text-sm text-steel/60">
        Questions, or applying for 1:1 coaching?{" "}
        <a href={`mailto:${siteConfig.contactEmail}`} className="text-accent underline">
          {siteConfig.contactEmail}
        </a>
      </p>
    </div>
  );
}
