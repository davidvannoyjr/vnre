# Content Operations — the runbook

This platform is built so you do not manage it day to day. Your one recurring job is
**approving topics**. Everything after that is automated.

## The loop

```
  propose            approve            draft (Claude)        schedule         publish
 ┌────────┐  you    ┌──────────┐  bot  ┌──────────────┐  bot ┌───────────┐ bot ┌───────────┐
 │ topic  │ ──────▶ │ approved │ ────▶ │ .mdx draft   │ ───▶ │ scheduled │ ──▶ │ published │
 │(queue) │  edit   │ (queue)  │       │ in your voice│      │ (date set)│     │ (live)    │
 └────────┘  status └──────────┘       └──────────────┘      └───────────┘     └───────────┘
        ▲                                      │
        │ Claude or you propose                │ you glance & edit (optional)
        └──────────────────────────────────────┘
```

## Your only required action: approve a topic

Open `content/topics/queue.yaml`. Each topic has a `status`. To greenlight one, change
its status to `approved`:

```yaml
  - id: 2026-06-fub-ai-followup
    type: tutorial
    track: automation
    level: intermediate
    tier: pro
    title: "Automate Lead Follow-Up with Follow Up Boss + AI"
    angle: "Wire an AI step into your FUB action plans so no lead goes cold."
    status: approved        # ← was: proposed
```

Commit. That's it. The next pipeline run drafts it.

> Prefer to do this by talking to Claude? Say **"approve the FUB follow-up topic"** or
> **"propose 5 new ChatGPT basic topics"** — see the `dvn-ai-lab-content` skill.

## What the automation does

Two GitHub Actions, both committing back to the repo:

1. **Draft approved topics** (`content-draft.yml`) — weekly (Mon 13:00 UTC) or on demand.
   Runs `scripts/draft-topic.mjs`: for every `approved` topic, calls Claude
   (`claude-opus-4-8`) with your voice rules, writes a `.mdx` file as `status: scheduled`
   with a staggered `publishDate`, flips the queue entry to `drafted`, validates, commits.

2. **Publish due content** (`content-publish.yml`) — daily (12:00 UTC). Runs
   `scripts/publish-due.mjs`: any `scheduled` post whose `publishDate` has arrived becomes
   `published`, committed (which redeploys the site).

You can run both manually from the GitHub **Actions** tab ("Run workflow") any time.

## Status values

| status | meaning | who sets it |
|---|---|---|
| `proposed` | idea in the backlog | you or Claude |
| `approved` | greenlit — draft it | **you** |
| `drafted` | `.mdx` written, scheduled | the drafter |
| `published` | live on the site | the publisher (by date) |
| `rejected` | skip it | you |

## Control knobs

- **How much you review.** Trust the lane and let it draft + schedule + publish hands-off,
  or open each new `.mdx` (status `scheduled`) and edit before its date. Both work; nothing
  goes live until the `publishDate`.
- **Pacing.** `draft-topic.mjs --stagger N` sets days between publish dates (default 3).
- **Voice.** The drafter embeds your voice rules. To tighten them, edit the `VOICE` constant
  in `scripts/draft-topic.mjs` (kept in sync with `claude/CLAUDE.md §2`).
- **Pull a piece.** Set a `.mdx`'s `status` back to `draft` (or delete the file) — it won't
  publish.

## Run it locally (optional)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
npm run topic:draft -- --dry     # preview which approved topics would draft
npm run topic:draft              # draft for real
npm run content:publish-due      # promote anything past its date
```

## Setup the automation once

1. GitHub repo → **Settings → Secrets and variables → Actions** → add `ANTHROPIC_API_KEY`.
2. Confirm Actions has write permission (Settings → Actions → General → Workflow permissions
   → Read and write). The workflows commit drafts back to the repo.
3. Done. The schedules run on their own; approve topics and walk away.
