# ERS Agreement Send

Sends the VNRE 2026 Exclusive Right to Sell listing agreement for e-signature via DocuSeal, prefilled with seller data pulled live from Follow Up Boss. For VNRE listings.

## Cadence
On-demand. Triggered whenever DVN (or authorized operator Jenae) says "send the ERS to {client}" / "get {client} under agreement." Not scheduled.

## Inputs
- Seller identity: a Follow Up Boss contact (name, URL, or ID)
- Deal terms provided at send time: list price, agreement end date, commission rate, second-seller info
- Standing config (don't re-supply): FUB API key, DocuSeal template, broker office values

## Outputs
- A DocuSeal signature envelope to the seller(s) + DVN (countersign)
- A note logged back to the seller's FUB record
- Completed copy routed to offers@vannoyre.com via DocuSeal BCC

## Process
The work is the `send-ers-agreement` skill — it carries the full field mapping and rules. Flow: FUB lookup → load template 4148179 → gather terms → confirmation gate → send → FUB note. Just say the trigger phrase; the skill runs.

## Key locations (all under _Claude md)
- Skill (installable): `02 Reference/SOPs/send-ers-agreement.skill`
- Skill source + tests: `04 Tools/send-ers-agreement-skill/`
- SOP (full reference): `02 Reference/SOPs/Listings - ERS Send Workflow.md`
- Operator setup for Jenae: `02 Reference/SOPs/ERS Send - Operator Setup (Jenae).md`
- Authorized operators: `02 Reference/vnre-agent-roster.md`
- FUB MCP server + setup script: `04 Tools/followupboss-mcp/`
- FUB API key: `02 Reference/fub-api-key.local.md`

## Current state (2026-06)
PRODUCTION. Canonical template: DocuSeal 4148179 "Listing Agreement - ERS New 2026" (older templates archived). Live-verified end to end; first real send (Edwards, 16408 Riggs Rd) out 2026-06-06. FUB API registered as system "VNRE-Claude" (higher rate limits). Signer always DVN; Jenae authorized to operate on his behalf.

## Open / future
- Roll out to Jenae's Mac (DocuSeal team invite + her setup doc) — see operator setup SOP.
- Re-run `fix-claude-config.sh` on DVN's Mac + laptop to pick up X-System headers.
- Possible later: pull deal terms from FUB deals; EBA (buyer agency) variant on template 3751998.

## Status
Active. Reference project — stays in 01 Projects (recurring use), not archived.

---
*This is a thin project brief. The skill + SOP hold the operational detail — start there.*
