# website — AI-Optimized Personal Site

A static personal site built for two readers at once: the human who lands on it,
and the **AI agent** a recruiter, buyer, seller, or coaching prospect sends to
summarize DVN. No build step.

```
website/
├── index.html      # semantic site; JSON-LD embedded; "Ask AI about me" footer block
├── llms.txt        # agent-readable summary (serve at /llms.txt)
├── ai.txt          # crawl/usage note for AI agents (serve at /ai.txt)
├── data/
│   └── dvn.jsonld  # schema.org RealEstateAgent + Person (single source for the embed)
└── README.md       # this file
```

## The signature feature — "Ask AI about me"
The footer block (`#ask-ai`) is human-visible *and* machine-readable. It pre-writes
the honest summary an AI should give — one-line, proof points, who DVN serves, the
CTA — so an agent quotes DVN's framing instead of guessing.

## Why it's "AI-optimized"
- **Semantic HTML + landmarks + alt text** — good accessibility *is* good
  AI-readability.
- **JSON-LD** (`schema.org/RealEstateAgent` + `Person`) embedded and mirrored in
  `data/dvn.jsonld`.
- **`/llms.txt`** — the conventional clean summary path for LLMs.
- **`/ai.txt`** — usage + accuracy note for agents/crawlers.

## Before deploy (fill these)
- Real links: booking URL, social, coaching inquiry (placeholders use the email).
- Real image at `/dvn.jpg` (referenced by `dvn.jsonld`; images are gitignored —
  keep the binary in Drive/host, not git).
- Confirm the canonical domain (`https://www.vannoyre.com/`).
- Deploy `index.html`, `llms.txt`, `ai.txt`, and `data/` to the web root so
  `/llms.txt`, `/ai.txt`, `/data/dvn.jsonld` resolve.

## Truth invariant
Every claim traces to the brain (`claude/CLAUDE.md` §1, §4–5). The numbers are
exact — the AI will be quoted on them. Update the brain first, then this site;
never let the site contradict it. Brief:
[`../claude/01-projects/ai-optimized-website/CLAUDE.md`](../claude/01-projects/ai-optimized-website/CLAUDE.md).
