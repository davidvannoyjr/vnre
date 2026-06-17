# CLAUDE.md

`vnre` is the GitHub-hosted mirror of David Van Noy Jr.'s (DVN) Claude "operating
brain" **plus** the source for the VNRE / aiDrVN automation tool suite. Claude Code
on the web clones this repo, so it's the manual Claude reads automatically.

There are two distinct kinds of content here, and they answer two different questions:

| If you need… | Read |
|---|---|
| **Who DVN is, how to write/respond in his voice, the business + coaching context, standing workflows, skills index** | **[`claude/CLAUDE.md`](claude/CLAUDE.md)** — the consolidated operating manual. Read it first for any client-facing or content work. |
| **How this repository is laid out, how the tools work, how to run/test/extend them** | this file (below). |

---

## Repository structure

```
vnre/
├── CLAUDE.md                  # this file — repo orientation for AI assistants
├── vannoy_dashboard.html      # standalone VNRE brokerage assets dashboard (single file)
├── .gitignore                 # secrets, node_modules, binaries, config.json all excluded
├── claude/                    # the operating brain (markdown) — source of truth for the manual
│   ├── CLAUDE.md              #   consolidated master: persona, voice, business, workflows, skills
│   ├── DVN-Coaching-Framework.md  # THE 22-Point coaching framework (GitHub-only, no Drive copy)
│   ├── README.md             #   what's mirrored vs left in Drive, and how the two sync
│   └── 02-reference/
│       ├── VNRE-Sold-Master-List.md   # pointer stub (full ~54KB file lives in Drive)
│       └── SOPs/             #   full operational procedures (PLP build, ERS send, etc.)
└── tools/                     # the aiDrVN automation suite (Python skills)
    ├── README.md             #   module index + 9-stage coverage map + pipeline diagram
    ├── MANIFEST.md           #   authoritative per-module classification (VNRE vs coaching)
    ├── vnre/                 #   🏢 modules that run the brokerage (almost everything)
    └── shared/               #   🔁 dual-use VNRE + DVN Coaching (call-coach today)
```

The two halves are independent: editing a tool never touches the brain, and vice
versa. The brain is prose Claude *reads*; the tools are code Claude *runs*.

---

## The tool suite (`tools/`)

Each subfolder under `tools/vnre/` or `tools/shared/` is a **skill** mapped to one
stage of DVN's aiDrVN 9-stage model (Prospect → Attraction → Prep → Closing →
Operations → Compliance → Finance → Database/COI → Scale). Read
[`tools/README.md`](tools/README.md) for the stage map and how modules chain into a
pipeline, and [`tools/MANIFEST.md`](tools/MANIFEST.md) for the per-module business
classification and maturity.

### Skill anatomy

A typical skill folder looks like:

```
<name>-skill/
├── SKILL.md            # frontmatter (name + description/trigger) + architecture & usage
├── README.md           # human-facing overview
├── scripts/*.py        # the deterministic engine(s)
├── sample/*.json       # sample inputs for --selftest and manual runs
├── config.example.json # template → copy to config.json (gitignored) and fill in
└── *.example.json      # rubric/checklist/plan templates, same copy-and-fill pattern
```

`SKILL.md` carries YAML frontmatter (`name`, `description`) — the `description` is
the trigger phrasing Claude matches on (e.g. "build my call list"). The Drive paths
written inside each `SKILL.md` (`04 Tools/...`) describe the flat Drive home; the
`vnre/` vs `shared/` split is a repo-clarity choice only.

### Design rules (hold for every module)

- **Deterministic Python, stdlib-only in the scoring layer — no network.** The
  ranking/scoring/report logic is pure and offline-testable. The only scripts that
  touch the network are the explicit FUB I/O ones (`fub_pull.py`, `fub_push.py`,
  `fub_field_setup.py`); keep that boundary.
- **Offline self-test.** Every engine supports `python3 scripts/<name>.py --selftest`
  using the bundled `sample/` data. Run it after any change.
- **Tunable constants at the top.** Weights, caps, and suppression windows live in an
  ALL-CAPS block near the top of the script (see `build_call_list.py`) — tune there,
  not inline.
- **Approval-gated.** Nothing sends or writes automatically. Outputs are briefs,
  drafts, and dry-runs. Write/commit actions require an explicit flag (e.g.
  `--commit` on `clv-sync`) that a human flips after validating runs.
- **Secrets and financials stay out of git.** API keys, `config.json`, and `_data/`
  are gitignored. Never commit them.

### Common CLI flags

Scripts use `argparse` with a shared vocabulary: `--selftest` (offline test),
`--pull` (input JSON), `--out` / `--out-md` / `--out-json` (output paths), `--config`,
`--today` (date override for deterministic runs), `--cap`. Module-specific inputs
(`--sold`, `--plan`, `--qbo`, `--transcript`, `--manifest`, `--checklist`, etc.) are
documented in each `SKILL.md`.

### Running / testing a module

```bash
# Self-test (no setup, no network):
python3 tools/vnre/active-hunter-skill/scripts/build_call_list.py --selftest

# Real run against a pulled JSON:
python3 tools/vnre/active-hunter-skill/scripts/build_call_list.py \
    --pull pull.json --out "<home>/<today> Call List.md"
```

There is no repo-wide build, test runner, or dependency manifest — each script is
self-contained stdlib Python 3. The verification gate for a change is the module's
own `--selftest` plus a manual run on its `sample/` data.

### Adding or changing a module

1. Match the skill anatomy above; keep the scoring layer pure and offline.
2. Add/keep a `--selftest` path that runs on bundled `sample/` data.
3. Put tunable constants in the top-of-file block.
4. Ship a `*.example.json` for any config; never commit the filled `config.json`.
5. Update [`tools/README.md`](tools/README.md) (module index + 9-stage map) and
   [`tools/MANIFEST.md`](tools/MANIFEST.md) (classification) so the indexes stay true.
6. If it needs a cadence, add a task file under `tools/vnre/scheduled-tasks/` and
   register it in that folder's `README.md` (collision-check the time).

---

## Source-of-truth & sync model

- **GitHub is the source of truth** for the brain markdown and all tool source. Edit
  here — it's versioned and diffable.
- **Google Drive (`_Claude md/` → `04 Tools/`) holds downstream copies** for the
  desktop Claude app and Drive-connected sessions. After editing `claude/CLAUDE.md`,
  overwrite Drive's single `Claude md/CLAUDE.md` **in place — never create a second
  file** (duplicate `CLAUDE.md` files are the failure mode this repo exists to
  prevent). `DVN-Coaching-Framework.md` is GitHub-only; nothing to sync.
- **Deliberately not mirrored to git:** secrets (`*.local.md`, FUB keys), `config.json`,
  `node_modules/`, `.skill` zips, binaries (`.png/.jpg/.dmg/.pdf`), and two oversized
  reference docs (Sold Master List, Pre-Listing Handover Spec) that exist as pointer
  stubs here. See [`claude/README.md`](claude/README.md) and `.gitignore`.

---

## Conventions for working in this repo

- **Voice matters for prose.** Any client-facing, marketing, coaching, or content
  output must follow the voice rules in [`claude/CLAUDE.md`](claude/CLAUDE.md) §2
  (direct, blunt, zero-hedging; banned-language list). This applies to deliverables,
  not to internal docs like this one.
- **Tool code is plain and deterministic** — match the existing style: stdlib only,
  constants at top, pure scoring layer, `--selftest` on sample data.
- **Never commit secrets or filled configs.** Check `.gitignore` before adding files.
- **Keep the indexes honest.** `tools/README.md` and `tools/MANIFEST.md` are the maps;
  update them when you add, remove, or re-stage a module.
- **Git:** develop on the designated feature branch, commit with clear messages, and
  push only to that branch. Do not open a pull request unless explicitly asked.
