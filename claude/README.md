# Claude brain — GitHub mirror

This `claude/` folder is the **source of truth** for David Van Noy Jr.'s markdown
Claude "brain." Edit it here — it's versioned, diffable, and structurally can't
spawn the duplicate-`CLAUDE.md` problem that hand-editing Drive can. Claude Code on
the web reads it directly (it clones this repo). Google Drive holds a downstream
**copy** of `CLAUDE.md` so the desktop Claude app and Drive-connected sessions read
the same manual — that copy is overwritten in place after changes here, never
duplicated.

## The one file that matters

**[`CLAUDE.md`](CLAUDE.md) is the single consolidated master** — operator persona,
voice rules, both business contexts, the coaching framework, tier structure,
standing workflows, skills index, project briefs, and the reference index, all in
one place. It was consolidated 2026-06-13 from the most-recent version of every
Claude file in Drive (see its "Audit & Provenance" section). Read it first.

Everything else here is **supporting detail**, linked from the master:

```
claude/
├── CLAUDE.md                     # ← the consolidated master (read first)
├── DVN-Coaching-Framework.md     # THE DVN Coaching framework — the 22-Point System
├── README.md                     # this file
└── 02-reference/
    ├── VNRE-Sold-Master-List.md  # pointer — large file kept in Drive
    └── SOPs/                      # full operational procedures
        ├── README.md
        ├── Listings - PLP Build Workflow.md
        ├── Listings - PLP Presentation Build.md
        ├── Listings - ERS Send Workflow.md
        ├── ERS Send - Operator Setup (Jenae).md
        └── VNRE Pre-Listing Presentation — Claude Handover Specification.md  # pointer
```

## Deliberately NOT mirrored here (stays in Drive)

- **Secrets** — `fub-api-key.local.md` and any `*.local.md` (see `.gitignore`).
- **Tool source / skills** — `04 Tools/` Node/Python apps, `*.skill` zips, `node_modules`.
- **Binaries** — `.dmg`, `.png`, `.jpg`, PDFs, MLS exports.
- **Two oversized reference docs** — the Sold Master List (~54 KB) and the
  Pre-Listing Presentation Handover Spec (~59 KB); pointer stubs link to Drive to
  avoid lossy/truncated copies.

## Source of truth & sync

- **Source of truth = this GitHub repo `claude/`.** Edit the brain here. Version-controlled, diffable, and it structurally can't produce the duplicate-`CLAUDE.md` problem that hand-editing Drive can.
- **Drive holds one downstream copy: `Claude md/CLAUDE.md`** — so the desktop Claude app and Drive-connected sessions read the same manual. After editing here, push it down by **overwriting that single Drive file in place. Never create a new file** — that is what spawns duplicates.
- **[`DVN-Coaching-Framework.md`](DVN-Coaching-Framework.md) lives only in GitHub** — Drive holds no copy, nothing to sync. `CLAUDE.md` §5 is a derived summary; the framework doc wins on conflict.
- Drive remains the home for what GitHub doesn't hold: skills (`*.skill`), tool source (`04 Tools/`), FUB keys / secrets, binaries, and the two oversized reference docs.

### How to update the brain

1. **Edit the file in GitHub** (web UI or a local clone).
2. **Changed `CLAUDE.md`?** Open Drive's single `Claude md/CLAUDE.md`, select-all, paste the new content over it, save. **Overwrite — never add a new file.** Wait for Drive to show "up to date."
3. **Changed `DVN-Coaching-Framework.md` or anything else GitHub-only?** Nothing to do in Drive.
4. **Invariant:** exactly one file named `CLAUDE.md` in Drive, always. If you ever see two, newest content wins — merge and delete the rest.
