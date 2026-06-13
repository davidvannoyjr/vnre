---
name: plp-presentation
description: "Generate the 16-page VNRE-branded, print-ready Pre-Listing Presentation PDF for a seller client. Use this skill whenever the user says 'build presentation for [client]', 'run the presentation builder', 'PLP presentation', 'pre-listing presentation', or indicates comps/comparables and pre-qual notes are ready in a client's PLP folder and wants the printed packet built. Output is an ink-saving US Letter portrait PDF for printing."
---

# VNRE Pre-Listing Presentation Build

Generate the branded Pre-Listing Presentation PDF for a seller client whose PLP folder (built by the `plp-build` skill) has comps and pre-qual notes in it.

Approved design (June 2026): ink-saving mode only — white pages, VNRE red #dc2626 accents, Lora display serif + Poppins sans, US Letter portrait, 16 pages: cover, principal profile, testimonials, geographic authority, plan of action (x2), media reach (x2 — syndication network with platform logos, stat callouts, social/outreach/print blocks, 14-day exposure timeline), road to closing, seller homework, Sold Near You, CMA divider, generated CMA summary, then net sheet / listing agreement / disclosures dividers. Design source of truth: `_Claude md/02 Reference/SOPs/VNRE Pre-Listing Presentation — Claude Handover Specification.md`.

## Tool location

`_Claude md/04 Tools/plp-presentation-builder/` (Google Drive, synced to every device):
- `vnre_presentation_builder.py` — the generator (needs Python 3 + reportlab; fonts and logo bundled, no network)
- `edwards_config.json` — sample config showing the exact schema
- `README.md` — usage details

## Steps

1. **Locate the client's PLP folder** in Drive: search parentId = '1omqsdvZwqNc6FUdsIPBiIupZLA9x_ChD' ("(01) Pre-Listing") for the client's last name.
2. **Read the inputs:**
 - `01 Pre-Qual Notes/Pre-Qual Summary - {Last Name}` → seller name, property address, property details (beds/baths/sqft/style), Zillow link
 - Files in `02 CMA & Pricing` (Matrix comps PDF, Cloud CMA, Realist report) → comp addresses, status, sold/list prices, beds/baths, sqft, DOM
3. **Run independent comp research — ALWAYS, even when David loaded comps.** David's loaded data is primary and always included; research supplements it and surfaces properties he should consider. Criteria:
 - Radius: within 1.5 miles of the subject property
 - Floor plan match: same style (2-story, ranch, split, reverse 1.5) and beds ±1, sqft ±20%
 - Price band: ±15% of the expected value implied by loaded comps or the pre-qual price expectation
 - Recency: sold within 12 months preferred; include actives/pendings as market-position context
 - Sources, in order: (a) WebSearch for "recently sold homes near {address}" / "{subdivision} {city} sold {year}" on zillow.com and redfin.com; (b) web_fetch the subject's Zillow link and any result pages that allow it; (c) on a manual run, if pages are blocked or client-rendered, use the Claude in Chrome browser tools to pull Zillow/Redfin "recently sold" results directly. Never fabricate a comp — only include properties with a verifiable address, price, and specs, and record the source per comp.
 - On a scheduled/headless run where Zillow and Redfin are unreachable, proceed with David's data alone and say so in the report.
4. **Merge:** David's comps first (source: Matrix/MLS), then research finds. Flag separately any researched property that materially changes the pricing picture — title the flag list "Properties to add / consider" with links.
5. **Build the config JSON** per the sample schema: seller_name, property_address, **city** — pull it from the PLP itself: the appointment city in the PLP folder name / pre-qual summary property address (e.g., "PLP - Edwards, 16408 Riggs Rd Stilwell KS, 2026" → Stilwell). The builder also auto-derives city from property_address as a fallback, but set it explicitly. Plus cma.narrative (2-3 sentence subject-property summary), cma.comps array (mark researched comps' source), cma.pricing with three tiers.
6. **Propose the three pricing tiers** (aggressive / recommended / aspirational) derived from the merged comp set, plus the consider-list, and show David for approval BEFORE generating. If `02 CMA & Pricing` is empty AND research found nothing verifiable, stop and say so — never invent pricing.
7. **Run:** `python3 vnre_presentation_builder.py config.json "VNRE Pre-Listing Presentation - {Last Name}.pdf"`
8. **Spot-check** the output (render a page or two to PNG and look at them — cover and CMA page minimum).
9. **Upload** the PDF into the client's `02 CMA & Pricing` subfolder in Drive (NOT the PLP folder root) and give David the link, plus a `Comp Research - {Last Name}` Google Doc in that same `02 CMA & Pricing` folder listing every comp (his + researched), sources, and the consider-list. (Note: some older client folders use a flat `CMA and Pricing` folder — file into whichever CMA/pricing subfolder exists; create `02 CMA & Pricing` only if none is present.)

## SOLD Near You page (automatic)

The builder adds a "SOLD Near You" page for the PLP city (explicit `city` in config, else derived from property_address): exact-city VNRE sales highlighted in red at the top, then the page fills to 14 rows with the MOST RECENT sales from the subject's state — Kansas appointments fill with Kansas sales, Missouri with Missouri (state from config, the property address, or the city). Only if the same-state pool runs short does it top up metro-wide. Display is family name + address only — no year, no buyer/seller distinction; all sales are presented the same. Data: `assets/vnre_sold_history.json` (1,400+ closings, 2009-2026), regenerated from the yearly Deal Sheet spreadsheets via `parse_deals.py`. Human-readable lookup: `_Claude md/02 Reference/VNRE Sold Master List.md` — also use it during PLP prep to spot past clients near the subject property. Refresh the JSON quarterly or when David asks.

## Rules

- SAMPLE or test PDFs must be clearly marked SAMPLE in the filename and never uploaded to client folders.
- Don't edit the static copy (bio, testimonials, plan of action) without David's explicit direction — it's approved brand copy from the spec.
- If the builder errors on fonts/assets, the bundled `fonts/` and `assets/` directories must sit next to the script — check they synced to this device.
