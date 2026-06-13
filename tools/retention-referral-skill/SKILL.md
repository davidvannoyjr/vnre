---
name: vnre-retention-referral
description: Build DVN's retention & referral brief — the ranked list of past clients and sphere (COI) contacts who have an outreach "moment" right now (equity milestone, home anniversary, move-window, referral ask, or cold-sphere re-engage), each with a drafted message in DVN's voice. Use whenever DVN says "run the retention brief", "retention", "equity and referral check", "who should I reach out to from my database / past clients", "referral opportunities", or when the retention-referral scheduled task fires. Also use to re-run, tune, or backfill a retention brief.
---

# VNRE Retention & Referral Brief (aiDrVN Stage 08)

Surfaces the past clients and sphere contacts most worth a touch this week — name, the
specific trigger (years owned, estimated equity gain, anniversary year, days since
contact), and a one-line draft in DVN's voice. The point: convert the 3,000-contact
database and 1,450-deal sold history into the **50% repeat-and-referral business** that
the VNRE business plan names as a key thrust — without DVN hand-combing the CRM.

This is the Stage 08 (Retention) module of the aiDrVN operating model. Same architecture
as `daily-lead-attention`: MCP pull → deterministic Python → Claude review → deliver.

## Architecture (why it works this way)

Cowork's sandbox cannot reach `api.followupboss.com`. All FUB data comes through the
**followupboss MCP server** (`fub_*` tools — load via ToolSearch if deferred), which runs
on the Mac with full network access. Flow:

1. `fub_*` pull → dump past-client + COI contacts (with last-contact date and, where
   available, deal close date + sale price) to a JSON file.
2. `scripts/build_retention_brief.py` → merges with the sold-history JSON, detects
   moments, scores, dedupes against state, writes the brief.
3. Claude → sanity-check the drafts, tune any that misfire, deliver.

If `fub_*` tools are not available: stop and tell DVN to restart Claude; if still missing,
run `04 Tools/followupboss-mcp/fix-claude-config.sh` with Claude fully quit. Never curl the
FUB API from the sandbox — it is blocked.

## Paths

- **Brief home (deliverables + state):** the `Follow Up Boss Pipeline` project folder
  (resolve the session mount at runtime, same as the lead brief).
- Brief: `<home>/YYYY-MM-DD Retention & Referral Brief.md`
- Working data: `<home>/_data/` → `retention-pull-YYYY-MM-DD.json`, `retention-brief.json`,
  `retention-state.json`
- This skill's script: `04 Tools/retention-referral-skill/scripts/build_retention_brief.py`
- Sold history (for equity/tenure): `04 Tools/plp-presentation-builder/vnre_sold_history.json`

## Steps

### 1. Pull
Two ways to produce `_data/retention-pull-YYYY-MM-DD.json`, both self-owned (no third party):

- **Preferred — `scripts/fub_pull.py`.** Self-contained FUB v1 REST client. On any machine
  with network + the API key: `FUB_API_KEY=… python3 fub_pull.py --config config.json --out
  _data/retention-pull-YYYY-MM-DD.json`. It pulls the Past Client + Sphere segments, joins the
  most-recent **won deal** (close date, sale price, property address), bulk-pulls
  **communications** for a true last-contact date, and reads **property-view events** + person
  custom fields (mortgage rate, birthday, CLV, preferred channel). See [`PULL_SPEC.md`](PULL_SPEC.md)
  for the field contract and [`ENRICHMENTS.md`](ENRICHMENTS.md) for the full data map.
- **In-session fallback — `fub_*` MCP tools.** Inside Cowork (no outbound network), assemble
  the same JSON with `fub_search_people` + the deal/comm tools, then run the engine.

The engine backfills any missing `closeDate` / `salePrice` / `address` from the sold-history
JSON (last name + address), so even a thin pull yields anniversary, move-window, and referral
moments; equity needs a sale price (from a FUB deal, a custom field, or the sold list).

If `fub_*` tools are unavailable in-session: restart Claude; if still missing, run
`04 Tools/followupboss-mcp/fix-claude-config.sh` with Claude fully quit. Never curl the FUB
API from the Cowork sandbox — it is blocked (use `fub_pull.py` on a networked machine instead).

### 2. Score
```bash
python3 "<skill>/scripts/build_retention_brief.py" \
  --pull  "<home>/_data/retention-pull-YYYY-MM-DD.json" \
  --sold  "04 Tools/plp-presentation-builder/vnre_sold_history.json" \
  --state "<home>/_data/retention-state.json" \
  --out-md   "<home>/YYYY-MM-DD Retention & Referral Brief.md" \
  --out-json "<home>/_data/retention-brief.json" \
  --today YYYY-MM-DD
```
(Translate paths to the bash mount prefix.) The script owns: equity estimation
(`salePrice × (1+appreciation)^years`), anniversary/milestone detection, the move-window
band, referral-due and cold-sphere thresholds, tier weighting (past client > COI), the
30-day suppression of anyone contacted recently, scoring, the 40-contact cap, and
day-over-day dedupe via the state file. Tuning constants are at the top of the script —
edit there, not by post-processing.

### 3. Review — judgment earns its keep
Read the draft brief. Spot-check before anything is presented:
- **Kill bad equity claims.** If a sale price looks wrong or the home was a teardown/major
  reno, drop or fix the gain figure — never send a number you can't defend.
- **Personalize the top drafts.** If a note mentions a life event, a specific kid, a job
  change, work it in. The template is a floor, not a ceiling.
- **Respect suppression.** Anyone contacted in the last 30 days is held out on purpose;
  don't override without reason.
- Keep DVN's voice: direct, declarative, no fluff, no "I hope this finds you well."

Edit the brief `.md` directly with corrections.

### 4. Deliver
1. The brief `.md` is in the project folder — present it.
2. **Gmail drafts** (connector drafts, does not send): for the contacts DVN greenlights,
   `create_draft` to the contact's email, subject per moment ("Quick question about
   {address}", "{N} years in the {city} house"), body = the approved draft as simple HTML.
   They land in Drafts as one-tap sends.
3. Optionally log a planned-touch note back to FUB so the team sees it.
4. Housekeeping: delete `_data/retention-pull-*.json` older than 30 days.
5. Chat summary: counts by moment, anything you overruled, anyone high-value you suppressed.

## Cadence
Weekly (Monday AM) via Cowork scheduled task `retention-referral`; manual trigger:
"run the retention brief". Weekly keeps each batch small and the database in constant,
light rotation rather than an annual blast.

## Tuning knobs (when DVN asks)
All at the top of `build_retention_brief.py`: `APPRECIATION_RATE`, `EQUITY_GAIN_THRESHOLD`,
`MOVE_WINDOW_YEARS`, `REFERRAL_DUE_DAYS`, `REENGAGE_COI_DAYS`, `SUPPRESS_CONTACT_DAYS`,
`CAP`, and the moment/tier weights. Cap is also a CLI arg (`--cap`).
