---
name: plp-build
description: "Build pre-listing packet (PLP) folders in Google Drive for new listing appointments on David Van Noy's Google Calendar. Use this skill whenever the user says 'run PLP prep', 'build PLP', 'PLP for [name]', mentions a new listing appointment or LA on the calendar, asks to prep for a listing appointment, or wants seller pre-listing folders created. Also use when checking whether any LA: calendar events still need PLP folders built."
---

# PLP Build Workflow

Build a standardized pre-listing packet (PLP) folder in Google Drive for each new listing appointment (`LA:` event) on David's Google Calendar. This runs daily at 7 AM as scheduled task `plp-folder-build`, and on demand when David asks.

The structure below was finalized June 6, 2026 after two revisions — do not reintroduce the full 00–06 seller folder structure at PLP stage. That structure gets built separately after the listing signs. PLP phase uses exactly four subfolders.

## Step 1 — Find new listing appointments

Using the Google Calendar connector, list events from today through +60 days with fullText search "LA:".

Keep only events whose title starts with `LA:`. Exclude the recurring placeholder **"LA: Template"** — it exists only to hold the description template and recurs constantly.

## Step 2 — Dedupe

For each candidate event, search Google Drive with `parentId = '1omqsdvZwqNc6FUdsIPBiIupZLA9x_ChD'` (folder "(01) Pre-Listing" under (02) Sellers) for a folder title containing the client's last name. If a folder exists, skip — never build twice, and never modify or delete existing folders.

## Step 3 — Build the folder

Create under parent `1omqsdvZwqNc6FUdsIPBiIupZLA9x_ChD`:

**Root folder name:** `PLP - {Name}, {Address}, {Year}`
- Name = event title after the `LA:` prefix (trim whitespace)
- Address = event location, street + city (drop zip if the name gets long)
- Year = current year
- Example: `PLP - Edwards, Shannon & Andrew, 16408 Riggs Rd Stilwell KS, 2026`

**Exactly four subfolders:**

```
PLP - {Name}, {Address}, {Year}/
│ 2026 PLP.pdf ← root level
├── 01 Pre-Qual Notes/ ← Pre-Qual Summary Google Doc
├── 02 CMA & Pricing/ ← left empty (CMA, Cloud CMA, Realist added during prep)
├── 03 Previous Inspections/ ← left empty (seller-provided inspection/engineer docs)
└── 04 Agreement & Disclosures/ ← four files below
```

**File copies (use Drive copy_file with these source IDs):**

| Source ID | Copy to | Title |
|---|---|---|
| `1Er_sg82jLZNb--WVqKzZDvQDBgFqUMtb` | root | 2026 PLP.pdf |
| `1hOaZig8KXVkv70IHt3IQvtWqsIDBslgw` | 04 Agreement & Disclosures | 2026 ERS VNRE Exclusive Right to Sell Agreement.pdf |
| `12-mLW8_C6GHluuY7rkYOX77SEN-FWDxh` | 04 Agreement & Disclosures | Sellers Disclosure and Condition of Property Addendum (Residential).pdf |
| `1H6X8rsaIqYmP-EbPIk5au2StyBkSRUZu` | 04 Agreement & Disclosures | Lead Based Paint Disclosure Addendum.pdf |
| `1gnOYdrdyshepE13l5FHOmOS6JjkMvf6p` | 04 Agreement & Disclosures | Sellers Homework.pdf |

The ERS comes from the **VNRE Custom Forms** folder — the authoritative source for current contract forms. If David says a form was updated, look for the new version in VNRE Custom Forms (folder ID `1UI-PKhVAw2YGkf9ORDwhDQ10StL4-_c0`) first, and update this table.

## Step 4 — Pre-Qual Summary doc

Create a Google Doc titled `Pre-Qual Summary - {Last Name}` inside `01 Pre-Qual Notes` (create_file with contentMimeType text/plain so Drive converts it to a Google Doc).

Parse the calendar event description (it follows the LA: Template format) into plain structured headings — no fluff:

```
PRE-QUAL SUMMARY — {NAME}

Appointment: {day, date, time}
Property: {full address}
FUB Profile: {link}
Zillow: {link}

SOURCE & SITUATION
- Source / County / Interviewing / Moving to / Timeline / Plan to hire

PRICING
- Price expectation / Owe / Prior listing history (DOM, expired, etc.)

PROPERTY
- Beds/baths/sqft/garage/lot, condition notes, updates, known issues

QUESTIONS FOR DVN
LOGISTICS / OPEN ITEMS
NOTES (include PLP instructions field)
```

Omit empty fields rather than printing blanks. Pull extra detail (old listing remarks, DOM) from the description when present — it helps the CMA step.

## Step 5 — Report

One line per folder built: `Built: PLP - {Name}... — appointment {date}` or `No new LA appointments.` Keep it short — David wants signal, not narration.

## Edge cases

- Missing event location: use the address in the description's Zillow link. If neither exists, name the folder `PLP - {Name}, {Year}` and flag it in the report.
- Multiple meetings for one client (e.g. "LA: Brad Joiner Meeting 2"): dedupe by last name catches this — one folder per client.
- Land/investment property: the standard packet still applies; note that "Basic PLP for Land or Investment Prop.pdf" lives in the (01) PLP Template 2026 folder (`1XhDUeyEtYj523Kd34h_AxmjY0rS-Hr2y`) if David asks for it.

## What happens after (not this skill's job, but expected next steps)

David or staff add comps/CMA files to `02 CMA & Pricing` (Matrix comps PDF, CMA Cover, Cloud CMA, Realist report). Previous inspection/engineer docs go to `03`. Once comps are in, the **plp-presentation** skill ("build presentation for {client}") generates the VNRE-branded print PDF. The full seller folder (00–06 from "_Template - Seller Folder") is created only after the listing agreement is signed.

Source of truth: `Pre-Listing Preparation Build/PLP Workflow SOP.md` in the Cowork project folder. If the workflow changes, update the SOP, this skill, and the `plp-folder-build` scheduled task prompt together.
