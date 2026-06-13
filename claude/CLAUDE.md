# CLAUDE.md — Root Operating Manual

This folder is the working root for all Claude projects for David Van Noy Jr. (DVN). Read this first in every session.

## Who I'm working for

- **DVN** — Broker/Owner, Van Noy Real Estate (VNRE) + Founder, DVN Coaching. Kansas City Metro (Johnson County KS, Jackson County MO). 20+ years, $500M+ closed.
- **Model:** Listings > buyers. Prospecting-heavy (expireds, FSBO, database, circle). Goal: ~75 listings/yr at ~$450k–$550k avg.
- **Coaching:** ~10 clients at ~$1k/mo, producing agents ($100k–$700k GCI).
- **Tech stack:** Follow Up Boss (CRM), Mojo (dialer), Heartland MLS, Dotloop/Skyslope, Google Workspace.

## How to respond

- Direct, blunt, structured. No fluff, no motivational filler.
- Use the `dvn-voice` skill for ALL outbound copy: emails, follow-ups, marketing, coaching content.
- Read `02 Reference/Brand/` guides before producing branded content.
- ROI-driven recommendations. Simple > clever. Proven > experimental.

## Tier structure

| Tier | Purpose | Rules |
|---|---|---|
| `01 Projects/` | Active work, one folder per project | Every project has a `CLAUDE.md` (purpose, inputs, outputs, cadence). New project = duplicate `_Project Template/`, rename, fill in. All deliverables save here — never loose at root. |
| `02 Reference/` | Standing knowledge Claude reads, rarely writes | `Brand/` (voice guides), `Scripts/` (prospecting dialogues), `SOPs/` (processes), `Templates/` (reusable deliverable shells). |
| `03 Archive/` | Finished projects, moved whole from 01 | Read-only history. Reactivate by moving back to `01 Projects/`. |
| `04 Tools/` | Code: MCP servers, apps, integrations | `followupboss-mcp`, `vnre-dashboard`. `node_modules` never synced — `npm install` per device. |

### Current projects (01)
- `PLP Build/` — pre-listing preparation pipeline: auto folder build, comp research, presentation generator (see its CLAUDE.md — the pick-up point for all PLP work)
- `VNRE Market Updates/` — monthly KC market content package (see its CLAUDE.md)
- `Numbers Analyzer/` — business planning + production numbers (pairs with `vnre-numbers-analyzer` artifact)
- `Homelight Leads Campaign/` — Homelight follow-up reference material
- `ERS Agreement Send/` — listing-agreement e-signature workflow (DocuSeal + FUB); see its CLAUDE.md. Runs via the `send-ers-agreement` skill.

### System folders — do not move, rename, or reorganize
| Folder | Owner |
|---|---|
| `AI Ideas Vault/` | Obsidian — aiDrVN brokerage operating model (116+ notes). **Master map: its `README.md`.** New ideas: numbered note in the matching `0X` category. Wiki-links depend on structure. |
| `Claude/` | Claude app — artifacts live in `Claude/Artifacts/`. |
| `Cowork OS/` | Google Drive cloud stub, not synced locally. Leave alone. |

## Conventions

1. **Naming dated work:** `YYYY-MM <Topic> - <Deliverable>.ext` (e.g., `2026-04 KC Market Update - FUB Email.html`).
2. **Folder names:** Title Case, no special characters.
3. **Source data** (MLS exports, PDFs) stays in the project folder next to the deliverable it feeds.
4. **One CLAUDE.md per project** — that's the project brief. READMEs in Reference subfolders explain what belongs there.

## Multi-device sync (Google Drive)

1. Drive for desktop set to **Mirror files** on every device (never Stream — placeholders break Claude's file access).
2. **One device works at a time.** Let Drive show "up to date" before switching machines.
3. Close Obsidian on one device before opening the vault on another (avoids `.obsidian/workspace.json` conflicts).
4. `node_modules` is never synced — after syncing to a new device, run `npm install` in each `04 Tools/` app folder.
5. If a `<name> (1).ext` conflict file appears, the newest content wins; merge manually and delete the duplicate.

## Standing context

- Conversion math: ~50 contacts → 1 appt; ~70% appt → listing; 150 calls/30 contacts daily.
- Database: 3,000+ contacts; under-contacted segment is the #1 opportunity.
- Counties tracked: Johnson (KS), Jackson (MO).

## Standing workflows

- **PLP Build** — new `LA:` calendar events get a PLP folder auto-built in Drive ((02) Sellers > (01) Pre-Listing). Full spec: `02 Reference/SOPs/Listings - PLP Build Workflow.md`. Installable skill for any device: `02 Reference/SOPs/plp-build.skill` (open in Claude desktop → Save skill). Runs daily 7 AM via Cowork scheduled task `plp-folder-build`; trigger manually with "run PLP prep". Structure: 4 subfolders only (Pre-Qual Notes, CMA & Pricing, Previous Inspections, Agreement & Disclosures) — full 00–06 seller folder is post-signing only. Contract form source of truth: VNRE Custom Forms folder.
- **PLP Presentation Build** — once comps + pre-qual notes are in a PLP folder, "build presentation for {client}" generates the 16-page VNRE-branded print PDF (cover, bio, testimonials, global exposure, plan of action, media reach w/ platform logos + 14-day timeline, road to closing, Sold Near You for the appointment city, CMA summary from comps, dividers). Tool: `04 Tools/plp-presentation-builder/` (see README). Installable skill: `02 Reference/SOPs/plp-presentation.skill`. SOP: `02 Reference/SOPs/Listings - PLP Presentation Build.md`. Design spec: `02 Reference/SOPs/VNRE Pre-Listing Presentation — Claude Handover Specification.md`.
- **ERS Agreement Send** — "send the ERS / listing agreement to {client}" sends the 2026 ERS VNRE listing agreement for e-signature via DocuSeal, prefilled from Follow Up Boss (seller contact + property address; deal terms provided at send time). Always confirms recipients + every prefilled value with DVN before sending; logs a note back to FUB after. Installable skill: `02 Reference/SOPs/send-ers-agreement.skill` (open in Claude desktop → Save skill). SOP: `02 Reference/SOPs/Listings - ERS Send Workflow.md`. Skill source + tests: `04 Tools/send-ers-agreement-skill/`. Requires: DocuSeal connector + `followupboss` MCP server per device (setup: `npm install` then run `04 Tools/followupboss-mcp/fix-claude-config.sh` with Claude quit; key: `02 Reference/fub-api-key.local.md`). Live-verified end-to-end 2026-06-06 on DocuSeal template 4148179 ("Listing Agreement - ERS New 2026" — the canonical ERS; older templates archived).
- **Daily Lead Attention Brief** — every day 5 AM via Cowork scheduled task `daily-lead-attention` (trigger manually with "run the lead brief"). Pulls FUB leads in Hot/Watch/Nurture (+ other stages on strong signal only), reads actual notes/texts/calls/emails via the `fub_lead_attention_pull` MCP tool, scores High/Med/Low (signal strength × stage priority × tier; Tier 1 = DVN COI / Agent COI / Past Client; Source=Import suppressed unless strong signal), flags stalls (Hot >7d, Watch >21d, Nurture >60d) and backward stage moves, caps at top 50 with tail note. Brief lands in the `Follow Up Boss Pipeline` project folder as `YYYY-MM-DD Lead Attention Brief.md` + a Gmail draft (connector can't send). Skill source: `04 Tools/daily-lead-attention-skill/`. Installable: `02 Reference/SOPs/daily-lead-attention.skill`. State/dumps: `Follow Up Boss Pipeline/_data/` (state file tracks day-over-day stage history — don't hand-edit). Requires the `followupboss` MCP server connected (same setup as ERS workflow).
- **VNRE Sold Master List** — `02 Reference/VNRE Sold Master List.md`: 1,450+ closed deals (2009–2026) with family, address, city, grouped by city. Use for PLP prep (Recently Sold page, past-client recognition near subject property). Machine-readable: `04 Tools/plp-presentation-builder/vnre_sold_history.json`; regenerate from yearly Deal Sheets via `parse_deals.py`.

## Offer Summary / Net Sheet — Design Standard (offer-to-spreadsheet skill)

Output is a 4-tab xlsx built from scratch by build_workbook.py (no template fill).
Tabs: Offer Comparison/Summary, Net Proceeds, Team Commission Breakdown, Commission Letter.
Commission tabs build only when JSON has a `commission` object.

**Naming keys off offer count (automatic):**
- 1 offer → tab "Offer Summary", title OFFER SUMMARY, single column headed "OFFER", no #1/#2, no best-term highlighting (nothing to compare), summary strip shows price / est. net / delta-vs-list.
- 2+ offers → tab "Offer Comparison", one column per offer headed "OFFER #1/#2…", best-term highlighting on, strip shows count / highest price / best net.
- Net Proceeds links auto-retarget to whichever tab name applies — never hardcode the source tab name.

**Palette — neutral base, red as accent ONLY:**
- Header/title bar: steel #2A2A2A, white text, thin red #C8102E rule beneath.
- Section bands: light shading #EDEDED, charcoal text (NOT red blocks).
- Summary strip: #F4F4F4 fill, charcoal text, thin gray border.
- Offer column headers: steel #2A2A2A, white text.
- Red #C8102E reserved for: Net to Seller hero, best-term highlights, the read-full-offer flag, before-payoff qualifier, Amount Due Co-op / Net to Agent figures.
- Brand hexes: RED C8102E, CHARCOAL 1C1C1C, GRAY 6E6E6E, WHITE FFFFFF. Row shading F4F4F4, label band E8E8E8, TBD-flag YELLOW FFF3B0, best-term tint HILITE FBE3E6.

**Fonts:**
- Headers: Roboto Condensed Bold. Body/narrative: Roboto.
- Client-facing tabs (Offer Comparison/Summary, Net Proceeds): numbers in Roboto (soft) — NOT Roboto Mono. Intentional deviation from the "Mono for stats" brand rule for a cleaner client feel.
- Internal tabs (Commission Breakdown, Letter): numbers in Roboto Mono for column alignment.

**Required elements:**
- Read-full-offer flag near bottom of every Offer Summary/Comparison: red bold on light-red fill — "THIS IS A SUMMARY ONLY. Read the complete offer and all addenda…the full contract controls." Appears on both single and multi.
- Inputs DVN changes: blue text + yellow fill. Unfound values: "TBD" + yellow fill (never invented).
- Net Proceeds: Net to Seller is the red hero; before-payoff qualifier auto-hides once a loan balance is entered.

**Logo:** white header band (logo is dark+red on transparent — invisible on dark). Falls back to "VAN NOY REAL ESTATE" wordmark if asset missing.

**Always recalc** (xlsx skill recalc.py) and confirm zero formula errors before delivering.
