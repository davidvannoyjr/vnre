# Claude brain — GitHub mirror

This `claude/` folder is a **synced copy** of the markdown "brain" from David Van
Noy Jr.'s Google Drive `_Claude md/` working root. Drive stays the day-to-day
workspace; this mirror exists so Claude Code on the web (which clones a GitHub
repo as its working directory) can read the operating manual and SOPs directly.

## What's here

```
claude/
├── CLAUDE.md                 # root operating manual (read first)
├── 02-reference/
│   ├── vnre-agent-roster.md
│   ├── VNRE-Sold-Master-List.md   # pointer — large file kept in Drive
│   └── SOPs/
│       ├── README.md
│       ├── Listings - PLP Build Workflow.md
│       ├── Listings - PLP Presentation Build.md
│       ├── Listings - ERS Send Workflow.md
│       ├── ERS Send - Operator Setup (Jenae).md
│       └── VNRE Pre-Listing Presentation — Claude Handover Specification.md  # pointer
├── 04-tools/
│   └── README.md             # tool index; source stays in Drive
└── projects/                 # per-project CLAUDE.md briefs
    ├── PLP Build.md
    ├── ERS Agreement Send.md
    ├── VNRE Market Updates.md
    ├── Numbers Analyzer.md
    ├── Offer Summaries.md
    └── _Project Template.md
```

## Deliberately NOT mirrored here (stays in Drive)

- **Secrets** — `fub-api-key.local.md` and any `*.local.md` (see `.gitignore`).
- **Tool source code** — `04 Tools/` Node/Python apps, `*.skill` zips, `node_modules`.
- **Binaries** — `.dmg`, `.png`, `.jpg`, PDFs, MLS exports.
- **Two oversized reference docs** — the Sold Master List and the Pre-Listing
  Presentation Handover Specification are large; pointer stubs link to Drive to
  avoid lossy/truncated copies. Copy them via Drive desktop if a full text copy
  is needed in-repo.

## Source of truth & sync

- **Canonical:** Google Drive `_Claude md/` (edited on DVN's devices).
- **This mirror:** refreshed when the manual/SOPs change. Treat Drive as primary;
  if the two disagree, Drive wins.
