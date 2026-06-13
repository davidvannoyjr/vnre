# Claude brain — GitHub mirror

This `claude/` folder is a **synced copy** of the markdown "brain" from David Van
Noy Jr.'s Google Drive working root. Drive stays the day-to-day workspace; this
mirror exists so Claude Code on the web (which clones a GitHub repo as its working
directory) can read the operating manual directly.

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

- **Canonical:** Google Drive `Claude md/` (VNRE shared drive). If the two disagree, Drive wins — **except** for the one GitHub-canonical file below.
- **Refresh this mirror** after Drive edits: ask "re-sync the Claude brain to GitHub."

### GitHub-canonical exception — the DVN Coaching Framework

- **[`DVN-Coaching-Framework.md`](DVN-Coaching-Framework.md) is GitHub-canonical, single source of truth.** It is static reference content — no skills, no Follow Up Boss, no live artifacts, no MCP dependency — so it lives and is edited in this repo. **Drive holds no copy.** Nothing to reconcile, no sync schedule.
- `CLAUDE.md` §5 carries only a **derived pointer/summary** of the framework, not a second copy of the substance. **If §5 and the framework doc ever disagree, the doc wins.** A re-sync from Drive must preserve the §5 pointer; the framework block in Drive's `CLAUDE.md` is kept as a thin pointer to this doc for exactly that reason.
