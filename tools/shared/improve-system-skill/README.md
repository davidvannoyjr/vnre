# improve-system-skill

The feedback loop of the Internal Operating System. After a task, capture the
lesson and turn it into a concrete, approval-gated edit to Knowledge or a Skill.
Propose, never self-modify.

```
improve-system-skill/
├── SKILL.md      # the skill (trigger + the four steps + rules)
├── README.md     # this file
├── LEARNINGS.md  # running changelog (auto-created/appended)
└── scripts/
    └── capture_feedback.py  # append a learning + draft the edit (--selftest)
```

## Quickstart
At the end of a task:
```
python3 scripts/capture_feedback.py \
    --task "what the task was" \
    --worked "what worked" \
    --change "the one specific improvement" \
    --target {knowledge|skill|new-skill|project} \
    --file path/to/target/file
```
It appends a dated entry to `LEARNINGS.md` and prints a proposed-edit block. The
brain edit is applied separately, only after DVN approves.

## Verify
`python3 scripts/capture_feedback.py --selftest`

## Why approval-gated
Master manual §3: nothing self-modifies, no regurgitating memory back at DVN. This
skill proposes the edit and logs it; DVN approves; only then does the brain change.
Knowledge edits land in the repo (source of truth) and then overwrite the single
Drive `CLAUDE.md` copy in place (§11).

## Reading the log
`LEARNINGS.md` is the system's changelog. Three entries on the same friction =
stop patching symptoms and fix the system. That review *is* the compounding.
