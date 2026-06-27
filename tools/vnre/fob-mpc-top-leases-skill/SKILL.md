---
name: vnre-fob-mpc-top-leases
description: FOB MPC Check — pull the top 3 lease listings that entered Follow Up Boss this week, ranked by list price. Use whenever DVN says "fob MPC check", "MPC check", "top leases this week", "lease listings", or "what leases came in this week".
---

# FOB MPC Check — Top Lease Listings (aiDrVN Stage 01 / Market Pulse)

On-demand snapshot: which lease listings entered FUB this week, ranked by price.
Surfaces the top 3 so DVN sees his active lease pipeline at a glance — no CRM digging.

MPC = Market Pulse Check. FUB = Follow Up Boss. Fast, read-only, no approval gate needed.

## Architecture

Same pattern as the lead-attention and database & COI briefs:
FUB pull → deterministic filter + rank → brief.

Cowork's sandbox cannot reach `api.followupboss.com` directly. All FUB data comes through
the **followupboss MCP server** (`fub_*` tools — load via ToolSearch if deferred). Flow:

1. Pull deals from FUB via `fub_*` MCP tools (in-session) or `scripts/build_top_leases.py`
   (networked Mac with `FUB_API_KEY` set).
2. Filter: type or tags match lease config (`leaseTypes`), stage is active (`activeStages`),
   and `created` or `updated` falls within the current Mon–Sun window.
3. Rank by list price (desc); secondary sort: created date (desc). Surface top 3.
4. Present the brief — no writes, no sends.

If `fub_*` tools are unavailable in-session: stop and tell DVN to restart Claude;
if still missing run `04 Tools/followupboss-mcp/fix-claude-config.sh` with Claude quit.
Never curl the FUB API from the Cowork sandbox — it is blocked.

## Steps

### 1. Pull deals from FUB

**In-session (MCP — preferred in Cowork):**

Use `fub_search_people` or `fub_list_deals` (whichever the followupboss MCP exposes) to
pull all deals or people tagged with "Lease" / "Rental" / "Lease Listing". Grab:
`id, name, type, stage, price (monthlyRent), created, updated, address, people (contact name), description`.

**Standalone (networked Mac):**
```bash
FUB_API_KEY=xxx python3 scripts/build_top_leases.py \
  --config config.json \
  --out "$(date +%F) MPC Top Leases.md"
```

### 2. Filter + rank (script or inline)

- **Week window:** current Monday 00:00 → Sunday 23:59. Today is the anchor; `build_top_leases.py`
  computes this automatically. In-session: compute Monday as `today - today.weekday()` days.
- **Lease match:** deal `type` or `tags` contains any value in `leaseTypes`
  (default: "Lease", "Rental", "Lease Listing").
- **Active match:** deal `stage` matches any value in `activeStages`
  (default: "Active", "Active KO", "Coming Soon", "New"). Omit the stage filter if DVN's
  lease pipeline doesn't use these exact names — adjust `config.json`.
- **Rank:** `price` desc → `created` desc. Cap at top 3 (`topN` in config).

### 3. Present the brief

Output format:
```
# FOB MPC Check — Top Lease Listings
Week of YYYY-MM-DD → YYYY-MM-DD

## #1 — [Address], [City]
Price: $X,XXX/mo  |  Listed: YYYY-MM-DD  |  Stage: Active
Client: [Name]
Notes: [first 120 chars of deal description if present]

## #2 — ...

## #3 — ...
```

No file is written unless DVN asks to save it. Present inline.

## Config

Copy `config.example.json` → `config.json` and fill in:
- `leaseTypes` — deal types or tag values FUB uses for lease listings in DVN's account.
- `activeStages` — stages to include (leave empty `[]` to include all stages).
- `topN` — default 3; bump if DVN wants to see more.
- `apiKeyFile` — path to `fub-api-key.local.md` (Drive only, never committed).

## Verify offline
```bash
python3 scripts/build_top_leases.py --selftest
```

## Cadence
On-demand. No scheduled task — run whenever DVN wants a lease snapshot.
