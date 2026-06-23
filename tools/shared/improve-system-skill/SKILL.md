---
name: improve-system
description: Capture what worked and what didn't after a task, and turn it into a concrete, approval-gated edit to DVN's Knowledge or a Skill — so the next run is better, not the same. Use at the end of any non-trivial task, or when DVN says "improve the system", "capture that", "what did we learn", "log that lesson", or "make sure next time is better". Proposes the exact edit; never self-modifies the brain.
---

# /improve-system — the loop that makes the OS compound

The multiplier in the Internal Operating System. Every task leaves a lesson; this
skill catches it and converts it into a real change to the right file. Without the
loop the OS is a filing cabinet. With it, the OS gets better every time DVN uses
it.

## When it runs
- End of any non-trivial task (default — don't skip).
- On demand: "improve the system", "capture that", "what did we learn".

## What it does (four steps)
1. **Capture** — record a structured learning: what the task was, what worked,
   what didn't, the one change that would have made it better.
2. **Classify** the change into exactly one target:
   - **Knowledge edit** → a file in `claude/` (master manual, coaching framework,
     `02-reference/`).
   - **Skill edit** → an existing `tools/.../SKILL.md` or script.
   - **New skill** → a new `tools/` module (scaffold only; build is a separate
     task).
   - **Project decision** → a "do not relitigate" line in a project `CLAUDE.md`.
3. **Draft the edit** — the exact diff to the target file. Approval-gated:
   proposes, never applies without DVN's yes (master manual §3 — nothing
   self-modifies).
4. **Log** — append the learning to `LEARNINGS.md` with date, target, and status.

## Usage
```
python3 scripts/capture_feedback.py \
    --task "ERS send to Smith" \
    --worked "Prefill from FUB was clean" \
    --change "Confirm recipient list BEFORE drafting, not after" \
    --target skill --file "tools/vnre/send-ers-agreement/SKILL.md" \
    --log tools/shared/improve-system-skill/LEARNINGS.md
python3 scripts/capture_feedback.py --selftest
```
The script appends a structured, dated entry and prints the proposed-edit block for
DVN to approve. It writes only to the log; the target-file edit is applied
separately, by hand or by Claude, after approval.

## Rules (non-negotiable)
- **Propose, don't self-modify.** The brain is edited only after DVN approves.
- **One target per learning.** If it touches two files, split it into two entries.
- **The repo is the source of truth.** Knowledge edits land here, then overwrite
  the single Drive copy in place (master manual §11).
- **Specific over vague.** "Be more careful" is not a learning. "Confirm
  recipients before drafting" is.

## Cadence
Per task. The `LEARNINGS.md` log is the system's running changelog — review it
when patterns repeat (three entries on the same friction = fix the system, not the
symptom).

## Verify offline
`python3 scripts/capture_feedback.py --selftest`
