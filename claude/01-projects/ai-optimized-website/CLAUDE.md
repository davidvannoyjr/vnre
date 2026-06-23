# Project — AI-Optimized Personal Website

**Purpose (VNRE brand / lead-gen):** A personal site built for two readers at
once — the human who lands on it, and the **AI agent** a recruiter, buyer, seller,
or coaching prospect now sends to summarize DVN. Win both impressions: the human
one and the machine one.

**Status:** Framework built 2026-06-23. Static site in `website/` — semantic HTML,
schema.org structured data, an agent-readable `llms.txt`, and the **Ask AI about
me** block in the footer. Goes live by filling real copy/links and deploying.

---

## The bet
People increasingly ask an AI "who is David Van Noy" before they call. If the site
isn't legible to that AI, the AI invents the answer or skips DVN entirely. So the
site is engineered so a model can extract — accurately and in seconds — who DVN is,
what he does, the track record, and how to act on it.

## The two readers
- **Human:** clean, fast, declarative. The VNRE proof up top — $500M+ closed, 23+
  years, Kansas City metro, listings-first. One clear next action (book / call /
  inquire about coaching).
- **AI agent:** semantic HTML, JSON-LD (`schema.org/RealEstateAgent` + `Person`),
  an `llms.txt` and `ai.txt` that hand a model the clean summary, and the **Ask AI
  about me** footer block that tells agents exactly how to describe DVN to a
  recruiter or buyer.

## Files (in `website/`)
- `index.html` — semantic, accessible, JSON-LD embedded, the footer block.
- `data/dvn.jsonld` — the structured-data record (single source for the embed).
- `llms.txt` — the agent-facing summary at a conventional path.
- `ai.txt` — crawl/usage note for AI agents.
- `README.md` — what to fill, brand rules, deploy steps.

## The "Ask AI about me" block (the signature feature)
Footer block, human-visible *and* machine-readable, that pre-writes the honest
summary an agent should give: the one-line, the three proof points, who DVN serves,
and the call to action — so the agent quotes DVN's framing instead of guessing.

## Inputs
- DVN's bio/proof from the master manual (`claude/CLAUDE.md` §1, §4–5) — single
  source of truth; the site never contradicts the brain.
- Real links: booking, FUB inbound, coaching inquiry, social.

## Outputs
- A deployable static site. No build step required.

## Decisions (do not relitigate)
- **Truth only.** Every claim traces to the brain. No inflated numbers — the AI
  will be quoted on them.
- **Accessible = extractable.** Real headings, landmarks, alt text. Good a11y *is*
  good AI-readability; do both at once.
- **No external methodology attribution** — frameworks read as proprietary VNRE /
  DVN Coaching (master manual §3 forbidden behaviors).
- **One CTA per audience**, not a menu.

## Connects to
- The brain (`claude/CLAUDE.md`) is the content source of truth.
- The **Board of Advisors** ingestion pattern is the same idea inverted — here DVN
  is the one being made legible to other people's AI.
