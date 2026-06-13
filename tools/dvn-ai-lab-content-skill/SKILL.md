---
name: dvn-ai-lab-content
description: >
  Manage the DVN AI Lab subscriber platform's content pipeline by voice. Use when
  DVN says "propose topics", "approve the {…} topic", "draft the approved topics",
  "what's in the content queue", "publish due posts", or wants new blog/tutorial
  content for the platform. Operates on platform/content/topics/queue.yaml and the
  .mdx content under platform/content/.
---

# DVN AI Lab — Content Pipeline Skill

The platform (`platform/`) teaches real estate agents to build AI skills. Content is
git-as-CMS: `.mdx` files + a topic queue. DVN's only required job is approving topics;
this skill lets him do that — and everything around it — conversationally.

## Triggers → actions

**"What's in the queue?" / "what's pending?"**
Read `platform/content/topics/queue.yaml`. Summarize by status (proposed / approved /
drafted / published), grouped by track. Flag anything stuck.

**"Propose {N} topics for {track} {level}" / "ideas for …"**
Generate topic ideas that pass DVN's decision filter (drives listings/GCI/coaching;
ROI-positive in 90 days; simple enough to execute daily). Append each to `queue.yaml`
with `status: proposed` (use `scripts/new-topic.mjs` or edit the YAML directly). Tracks:
`chatgpt`, `claude`, `re-tools`, `automation`. Levels: `basic`, `intermediate`,
`advanced`. Set `tier` sensibly (free intros, basic→Basic, intermediate→Pro,
advanced→Elite). Show DVN the list; do not approve on his behalf.

**"Approve {the … topic}" / "greenlight {…}"**
Set that topic's `status: approved` in `queue.yaml`. Confirm which one. Commit.

**"Draft the approved topics" / "write them up"**
Run `npm run topic:draft` (needs `ANTHROPIC_API_KEY`). Or, if drafting in-session, write
each `.mdx` yourself in DVN voice (see `claude/CLAUDE.md §2` and the `dvn-voice` skill),
following the frontmatter contract in `platform/src/content-schema.ts`: status
`scheduled`, a `publishDate`, correct `tier`/`track`/`level`, and `topicId` pointing back
to the queue entry. Then flip the queue entry to `drafted`. Validate with
`npm run content:check`.

**"Publish what's due" / "anything go live?"**
Run `npm run content:publish-due` (promotes scheduled → published by date).

## Rules

- **Never auto-approve.** Proposing and drafting are fine to do proactively; approval is
  DVN's call — surface options and wait.
- **Voice is non-negotiable.** All drafted content is DVN's voice: direct, blunt, ROI-driven,
  no hype, no clichés, no external brand attribution. Read `claude/CLAUDE.md §2`.
- **Validate before commit.** `npm run content:check` must pass; a malformed doc breaks the
  pipeline.
- **One file is the control surface.** When in doubt, the source of truth for "what should
  exist" is `platform/content/topics/queue.yaml`; for "what's live" it's the `.mdx`
  `status` + `publishDate`.

## Reference

Full runbook: `platform/docs/CONTENT-OPS.md`. Architecture: `platform/docs/ARCHITECTURE.md`.
