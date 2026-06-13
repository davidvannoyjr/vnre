# PLP Build — Project Brief

Standing pre-listing preparation system. Pick up any session, any device, by reading this.

## Purpose

Turn every new `LA:` calendar appointment into a prepared listing appointment with zero manual folder work: auto-built PLP folder, pre-qual summary, comp research, and a print-ready VNRE-branded presentation.

## The pipeline

1. **Folder build (automated)** — daily 7 AM Cowork scheduled task `plp-folder-build` (runs on David's main Mac) scans Google Calendar 60 days out for `LA:` events and builds `PLP - {Name}, {Address}, {Year}` in Drive ((02) Sellers > (01) Pre-Listing) with subfolders: 01 Pre-Qual Notes (incl. generated Pre-Qual Summary doc), 02 CMA & Pricing, 03 Previous Inspections, 04 Agreement & Disclosures (current forms from VNRE Custom Forms). Manual trigger: "run PLP prep".
2. **Comp pre-research (automated)** — same task: appointments within 3 days with empty `02 CMA & Pricing` get a "Comp Research" doc (Zillow/Redfin, 1.5 mi radius, similar floor plan/price). David's Matrix comps always take precedence.
3. **Presentation build (on demand)** — "build presentation for {client}": parses pre-qual + comps, runs independent comp research, proposes 3-tier pricing for David's approval, generates the 16-page ink-saving print PDF (incl. Media Reach marketing pages with platform logos + Sold Near You page for the appointment city), uploads to the PLP folder.

## Assets (all in _Claude md, synced)

| Asset | Path |
|---|---|
| Folder-build SOP / skill | `02 Reference/SOPs/Listings - PLP Build Workflow.md` + `plp-build.skill` |
| Presentation SOP / skill | `02 Reference/SOPs/Listings - PLP Presentation Build.md` + `plp-presentation.skill` |
| Design spec (approved copy) | `02 Reference/SOPs/VNRE Pre-Listing Presentation — Claude Handover Specification.md` |
| Generator tool | `04 Tools/plp-presentation-builder/` (script, fonts, logo, sold-history JSON, README) |
| Sold master list (lookup) | `02 Reference/VNRE Sold Master List.md` (1,450+ deals by city) |
| KC metro cities reference | `01 Projects/PLP Build/KC Metro Cities.md` (canonical city list, normalization rules, sold counts — sync with code lists) |

## Key decisions (do not relitigate)

- PLP folders use 4 subfolders only; the full 00–06 seller folder is built post-signing.
- Presentation is ink-saving mode only; static copy (bio, testimonials, plan of action) is approved — change only on David's direction.
- Contract form source of truth: VNRE Custom Forms folder in Drive.
- Comp research always runs, but David's loaded comps are always primary; never fabricate a comp.
- SOLD Near You page: exact-city sales highlighted first, fill with most recent same-state (KS/MO) sales, family + address only (no year/side). Full logic: `KC Metro Cities.md` in this folder.

## Cadence / maintenance

- Scheduled task: daily 7 AM (this device only; other devices run skills on demand).
- Refresh sold master list quarterly: "refresh the sold master list" (see tool README for mechanics).
- Update the current-year Deal Sheet ID in regen instructions each January.

## Status

- Built and live June 6, 2026. First live build: Edwards, 16408 Riggs Rd, Stilwell (sample presentation in Cowork project folder).
- Open: Edwards real comps pending → first production presentation run.
