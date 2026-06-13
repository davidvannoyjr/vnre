---
name: vnre-compliance-auditor
description: Audit a transaction folder against the required-documents checklist per stage (listing / under-contract / closing) — flag missing documents, docs that need signature verification, and deadline risks. Use whenever DVN says "compliance check {client}", "audit the file", "is this file complete", "what's missing on {transaction}", or before broker sign-off / file-to-close. aiDrVN Stage 06. A completeness aid, NOT legal certification.
---

# VNRE Compliance Auditor — Stage 06

Catches an incomplete transaction file before it becomes a problem: what's missing, what still
needs signatures, and which deadline is about to hit. Protects against the slow, expensive errors
(missing disclosure, unsigned addendum) — the plan's "clean backend support" thrust.

> **Completeness aid, not legal certification.** A licensed broker must review and approve. The
> auditor checks document **presence + naming** and flags signature docs for **human**
> verification; it does not validate e-signature legal sufficiency.

## Architecture
Claude lists the Drive transaction folder → deterministic checklist evaluation → report.

1. **Build the manifest:** with the Drive MCP, `search_files parentId = '<transaction folder id>'`;
   collect the filenames into a JSON list (`_data/manifest.json`).
2. **Context (optional):** `{"yearBuilt": 1956, "dates": {"inspectionDeadline": "...", "closingDate":
   "..."}}` — drives the pre-1978 lead-paint conditional and the deadline flags.
3. **Audit:** `python3 scripts/audit_file.py --manifest _data/manifest.json --checklist checklist.json
   --stage listing|under_contract|closing --context _data/ctx.json --out "<folder>/Compliance Check.md"`.
4. **Act:** fix 🔴 missing docs, verify ⚠️ signatures, watch ⏰ deadlines. Then route to the broker
   for the actual sign-off.

## The checklist
`checklist.json` (copy from `checklist.example.json`) defines required docs per stage, each with
filename `match` patterns, a `signature` flag, and an optional `conditional` (e.g. `pre1978` for
lead paint). **Confirm the form set with your broker / Heartland MLS** — requirements change.
Editing the checklist is how you tune the audit; don't hardcode in the script.

## Stages
- `listing` — pre-MLS signed file (ERS, seller's disclosure, agency, lead paint if pre-1978, wire
  advisory, MLS profile…). Pairs with the PLP "04 Agreement & Disclosures" folder.
- `under_contract` — sale contract + addenda, earnest money, inspection/resolution…
- `closing` — fully executed contract, settlement statement / CD, commission disbursement…

## Deadlines
Any dates in `context.dates` matching `dateChecks` are flagged 🔴 overdue / 🟡 due ≤3 days / 🟢 ok.

## Roadmap (deeper, later)
Signature-field validation is human today. A later pass could download each PDF and parse its
AcroForm signature fields (PyPDF) to auto-confirm execution — gated on not pulling client docs
anywhere they shouldn't go.

## Verify offline
`python3 scripts/audit_file.py --selftest`
