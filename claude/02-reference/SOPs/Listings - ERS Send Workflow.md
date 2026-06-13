# Listings — ERS Send Workflow

Send the 2026 VNRE Exclusive Right to Sell Agreement (ERS) for e-signature via DocuSeal, prefilled with seller data from Follow Up Boss and deal terms from DVN.

**Trigger:** "send the ERS to {client}", "send the listing agreement to {client}"
**Skill:** `send-ers-agreement` (install from `02 Reference/SOPs/send-ers-agreement.skill` — open in Claude desktop → Save skill)
**Template:** DocuSeal id 4185542 — "ERS Docuseal Only Workflow 2026 / claude" (supersedes 4148179 and 3551935). Role names: Master Sender (DVN), Seller1, Seller2.

## Flow

1. Look up seller in FUB (`fub_search_people` / `fub_get_person`; curl fallback where network allows)
2. Load the ERS template from DocuSeal — roles identified by fields, not names
3. Gather deal terms from DVN (list price, end date, second seller), apply standing defaults
4. **Confirm with DVN — always.** Recipients + every prefilled value + checked boxes. No send without explicit approval.
5. Send via DocuSeal `send_documents`
6. Log note to seller's FUB record (`fub_add_note`)

**Office copy:** offers@vannoyre.com gets a read-only copy of every completed agreement — via DocuSeal account setting (Settings → Email/Notifications → BCC completed documents), or a no-field CC/viewer role on the template if one exists. One-time setup; skill flags it if missing.

## Roles

| Role | Who | Included |
|---|---|---|
| Seller 1 | Seller from FUB | Always |
| Seller 2 | Co-owner — own signature/initials/date | Only with a second seller |
| Designated Agent | DVN (david@vannoyre.com) by default; another VNRE agent only if DVN names one AND they're listed in `02 Reference/vnre-agent-roster.md` — all prefill fields + agent signature | Always |

No co-listing-agent role. One agent signer: DVN.

## Fill logic — full custom mapping (standing defaults)

Field names exact, per live template 4185542. Roles: Master Sender (DVN — owns all prefill fields), Seller1, Seller2.

| Field (Master Sender role unless noted) | Value |
|---|---|
| Seller(s) Name(s) | Full names joined with "and" (from FUB) |
| Property Address | Property being listed (FUB address as start; DVN confirms) |
| List Price | DVN at send — number type, plain integer, no $ or commas (e.g. 639950) |
| Term Start | Send date unless DVN says otherwise (date, YYYY-MM-DD) |
| Term End | DVN at send time — never defaulted |
| MLS Active Date | Send date + 30 days unless DVN says otherwise |
| Commission Percentage | Number, default 3, override at send (single field — no more checkboxes) |
| Additional Compensation | Number, default 1.9 (unrepresented-buyer comp %), override at send |
| Seller(s) Names on tax record | DVN provides; if none distinct, repeat seller name (required field) |
| Legal Description | DVN provides (required — don't invent; ask if missing) |
| Exclusions | DVN provides; send "None" if none (required field) |
| Seller1 signature date / Seller2 Signature date | Send date, prefilled (locked read-only) |
| All signatures + initials + Master Sender date | Never prefilled — signers fill |

No broker/seller contact fields and no commission checkboxes — removed in this version. All Master Sender text/number fields are Required, so supply a value (or "None") rather than leaving blank. Note: the MCP's load_template serves a stale cache and hides signature/initials fields — this mapping reflects the live editor.

## Requirements per device

- DocuSeal connector (Claude settings)
- `followupboss` MCP server: `04 Tools/followupboss-mcp` — `npm install`, then **quit Claude fully** and run `fix-claude-config.sh` (same folder) in Terminal, then reopen Claude
- API key: `02 Reference/fub-api-key.local.md`

**Setup gotchas (learned 2026-06-06):**
- Never edit `claude_desktop_config.json` while Claude is running — the app overwrites it on quit and your edit is lost. Quit first, then edit (the fix script enforces this).
- Use the absolute path to `node` in the config, not `"node"` — desktop apps can't see Homebrew/nvm paths. The fix script resolves this automatically with `which node`.

## Rules that matter

- Prefilled DocuSeal fields are **read-only for the signer** — only prefill confirmed values
- Never invent missing data; leave the field blank and flag it
- Multiple FUB matches → ask DVN which; never guess
- Wrong-contact send = legal doc to the wrong person; a clarifying question is always cheaper

## DocuSeal email templates (set in DocuSeal Settings → Email)

- **Documents copy email** (signer copy): subject "Fully executed: {template.name} — Van Noy Real Estate"; body confirms full execution, attachment + audit log, em-dash "what this means" section, changes-in-writing-only line, (913) 393-9469, closes "We're moving. I'll be in touch with your next steps shortly."
- **Completed notification email** (internal — DVN + offers@): subject "Signed: {template.name} — {submission.submitters}"; body: fully executed, signers, copy + audit log attached, {submission.link}, "Next: file to the transaction folder and log in FUB."
- Toggles: attach documents ON, attach audit log ON, send automatically on completion ON.
- offers@vannoyre.com receives completed copies via account BCC setting.

## History

- 2026-06-06: Built + live-tested send path (submission 8215274 on old template 3761391, since archived). Canonical template switched to 3551935 after DVN built out its full field set.
- 2026-06-06 (later): Full pipeline verified live on 3551935 (submission 8216239) — FUB lookup, prefill, confirmation gate, send, FUB note write-back.
- 2026-06-06 (final): **Template rebuilt as "Listing Agreement - ERS New 2026" (4148179)** after page-by-page PDF logic audit: roles Seller1/Seller2/Designated Agent, 28 fields, check-one commission design (3.9/4.9/custom blank), warranty + name-on-title language removed from document, broker/seller contact fields on signature page. Old templates archived. **Final live test passed: submission 8216996** (prefill, checkbox logic, contact blocks, locked seller date all verified). FUB note #148638. PRODUCTION READY.
- Possible future modifications: deal-term fields could pull from FUB deals instead of asking; Seller2 email handling when spouse shares an inbox; EBA (buyer agency) variant of this skill using template 3751998.
