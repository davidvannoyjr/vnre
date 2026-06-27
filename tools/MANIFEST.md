# Tools Manifest — what each module is, and where it belongs

The one table to answer "what is this piece and does it stay." Built so you can merge without
worrying that VNRE and Coaching get tangled. **The short version: it's not tangled.** Almost
everything runs the brokerage; the overlap with Coaching is narrow and clearly marked.

## Layout
```
tools/
├── vnre/      🏢 runs Van Noy Real Estate (the brokerage). This is ~all of it.
├── shared/    🔁 dual-use: same engine serves VNRE and DVN Coaching (just call-coach today)
├── README.md  module index + 9-stage coverage map + pipeline diagram
└── MANIFEST.md (this file)
```
> In Google Drive these all live flat under `04 Tools/` — the `vnre/` vs `shared/` split is a
> repo-clarity choice. The `04 Tools/...` paths inside each SKILL.md describe the Drive home and
> stay flat.

## The modules

| Module | Folder | Business | Stage | Maturity | Keep? |
|---|---|---|---|---|---|
| `active-hunter-skill` | vnre | 🏢 VNRE | 01 Prospect | ✅ production | **keep** |
| `stage01-prospecting` (book-appointment) | vnre | 🏢 VNRE | 01 Prospect | ✅ production | **keep** |
| `stage01-prospecting/SCOPE.md` | vnre | 🏢 VNRE | 01 (voice) | 📋 scope only (not code) | keep as plan |
| `content-engine-skill` | vnre | 🏢 VNRE | 02 Attraction | ✅ production | **keep** |
| `compliance-auditor-skill` | vnre | 🏢 VNRE | 06 Compliance | ✅ production | **keep** |
| `ceo-dashboard-skill` | vnre | 🏢 VNRE | 07 Finance | ✅ production | **keep** |
| `database-coi-skill` | vnre | 🏢 VNRE | 08 Database/COI | ✅ production | **keep** |
| `clv-sync-skill` | vnre | 🏢 VNRE | (cross) | ✅ production | **keep** |
| `fob-mpc-top-leases-skill` | vnre | 🏢 VNRE | 01 Prospect | ✅ production | **keep** |
| `scheduled-tasks` | vnre | 🏢 VNRE | — | ✅ definitions | **keep** |
| `call-coach-skill` | shared | 🔁 VNRE + Coaching | 09 Scale | ✅ self mode · 🧪 client/agent modes | **keep** |

**Nothing here is throwaway.** The only non-production items are the Stage 01 **SCOPE** (a
planning doc) and the voice overlay it describes (scoped, gated on a compliance + vendor decision).

## Where Coaching actually overlaps (the whole answer)

1. **`call-coach-skill` (shared).** Built in `--mode self` for your own calls (VNRE). It also has
   `--mode client` and `--mode agent` — those are the DVN Coaching / new-agent product. Same code,
   different report framing. Lives in `shared/` because of this.
2. **The aiDrVN product layer (not a folder).** *Every* VNRE-ops tool is also a candidate sellable
   aiDrVN module. That's a go-to-market decision, not a code split — the tool that runs your
   brokerage and the tool you'd license are the same file. Track productization in your business
   plan, not by forking the code.

So: merge `tools/vnre/` with confidence (pure brokerage), treat `tools/shared/` as the one place
where a coaching use exists, and decide aiDrVN packaging separately whenever you're ready.

## Cross-cutting facts
- Every module: deterministic Python, offline `--selftest`, tunable constants, **approval-gated**
  (nothing sends/writes without you), secrets + financials kept out of git.
- Live dependencies are listed per module and in `README.md`'s "open items."
