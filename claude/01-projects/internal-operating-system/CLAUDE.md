# Project — Internal Operating System

**Purpose (meta / all):** Tie every tool, document, and process into one operating
system with a single mental model — **Knowledge · Skills · Projects** — and a
feedback loop (`/improve-system`) that makes the whole thing get better every time
DVN uses it. This is the house the other three projects live in.

**Status:** Framework built 2026-06-23. The model is mapped onto the existing repo
(below); the `/improve-system` skill is scaffolded in
`tools/shared/improve-system-skill/`. Goes live the first time a task ends with a
captured improvement.

---

## The model (three folders, one map)
The source prescribes three top-level areas. The repo already has them — this brief
just names them so the mapping is explicit and stops drifting.

| OS area | What it is | Where it lives today |
|---|---|---|
| **Knowledge** | DVN's brain + standing reference Claude reads | `claude/` — `CLAUDE.md`, `DVN-Coaching-Framework.md`, `02-reference/` (+ the AI Ideas Vault in Drive) |
| **Skills** | Repeatable processes / code modules | `tools/` — the aiDrVN suite + `board-of-advisors` + `improve-system` |
| **Projects** | Active work | `claude/01-projects/` |

> In Drive the same three map to `02 Reference/` (Knowledge), `04 Tools/` +
> `*.skill` (Skills), `01 Projects/` (Projects). `03 Archive/` is finished
> Projects. The repo is the source of truth; Drive is the downstream copy
> (master manual §11).

## Key component — the `/improve-system` skill
The multiplier. After a task, it captures what worked and what didn't and turns
that into a concrete change to the Knowledge or a Skill — so the next run is
better, not the same. Without this, the OS is a filing cabinet; with it, the OS
compounds.

- **Trigger:** "improve the system", "capture that", "what did we learn", or run at
  the end of any non-trivial task.
- **What it does:** records a structured learning, classifies it (Knowledge edit /
  Skill edit / new Skill / Project decision), and drafts the exact edit —
  approval-gated, nothing self-modifies.
- **Where it writes:** appends to `tools/shared/improve-system-skill/LEARNINGS.md`
  and proposes the diff to the target file.
- Source: `tools/shared/improve-system-skill/SKILL.md`.

## Inputs
- A finished task + DVN's read on it (one line of what to keep / change).

## Outputs
- A `LEARNINGS.md` entry + a proposed edit to the right file in Knowledge or
  Skills.

## Process
1. Finish a task.
2. Run `/improve-system` (or DVN says "capture that").
3. The skill writes the learning and drafts the edit.
4. DVN approves; the edit lands; the system is now better.

## Decisions (do not relitigate)
- **Three areas, no fourth.** Anything that isn't Knowledge, a Skill, or a Project
  is in the wrong place.
- **Nothing self-modifies.** `/improve-system` proposes; DVN approves; only then is
  the brain edited. (Master manual §3.)
- **The repo is the source of truth.** Drive is downstream. Edits to the brain
  happen here, then overwrite the single Drive copy in place (§11).
- **The loop is non-optional.** A task without a capture is a missed compounding
  step.

## Connects to
- Wraps all three other builds: each one's outcomes route through `/improve-system`.
- Formalizes, doesn't replace, the tier structure in master manual §6.
