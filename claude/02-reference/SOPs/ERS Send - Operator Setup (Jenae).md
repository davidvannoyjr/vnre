# ERS Send — Operator Setup for Jenae

You're authorized to send ERS listing agreements on DVN's behalf. The documents always carry DVN's name and signature — you operate the workflow, he countersigns. One-time setup, about 10 minutes.

## Before you start (have these ready)

1. **Google Drive for desktop** — signed in as jenae@vannoyre.com, syncing the **VNRE Main** shared drive, set to **Mirror files** (Drive settings → not "Stream"). You should see the `_Claude md` folder locally.
2. **Claude desktop app** — signed into your Claude account.
3. **Node.js** — if you don't have it: nodejs.org → download LTS → install.
4. **DocuSeal access** — DVN must add you to the VNRE DocuSeal team first (DocuSeal → Settings → Users). You'll sign the connector in with your own DocuSeal login.

## Setup

1. **Install the skill.** In Drive: `VNRE Main → _Claude md → 02 Reference → SOPs → send-ers-agreement.skill` — open it with Claude desktop → click **Save skill**.
2. **Connect DocuSeal.** Claude → Settings → Connectors → add DocuSeal → sign in with your VNRE DocuSeal login.
3. **Connect Follow Up Boss.** Quit Claude completely (Cmd+Q). Open Terminal, type `bash ` (with the trailing space), then drag the file `_Claude md → 04 Tools → followupboss-mcp → fix-claude-config.sh` from Finder into the Terminal window, press Return. It finds everything, tests the connection, and configures Claude. Reopen Claude.
4. **Verify.** Start a Cowork session, connect the `_Claude md` folder, and say **"test fub"**. You should see the connection confirmed.

## Using it

Say: **"send the ERS to {client name}"** — then answer Claude's questions (list price, end date, second seller) and approve the confirmation summary before anything goes out. Claude pulls the client from Follow Up Boss, prefills the agreement, sends for signatures, and logs the send in FUB.

Rules:
- The signer is always DVN — never change the Designated Agent.
- Review every value in the confirmation summary before approving. Prefills are locked for the client once sent.
- If anything looks off — wrong client, wrong address, two FUB matches — stop and ask DVN.

Full workflow reference: `02 Reference/SOPs/Listings - ERS Send Workflow.md`
