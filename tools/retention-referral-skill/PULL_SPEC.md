# FUB Pull Spec — vnre-retention-referral (Stage 08)

The engine (`build_retention_brief.py`) is done. The only thing standing between it and a
live weekly brief is the **pull**: getting Past Client + COI contacts out of Follow Up Boss
with the fields the engine needs. This spec defines that contract.

Same constraint as the lead brief: the sandbox can't reach `api.followupboss.com`. The pull
runs through the **followupboss MCP server** on the Mac (`fub_*` tools), exactly like
`fub_lead_attention_pull` does for Stage 01.

---

## 1. Output contract (what the engine consumes)

Write a JSON array (or `{"contacts": [...]}`) to
`<home>/_data/retention-pull-YYYY-MM-DD.json`. One object per contact:

```jsonc
{
  "id": "12345",                  // FUB person id (REQUIRED — dedupe key)
  "firstName": "Andrew",          // REQUIRED for the draft greeting
  "lastName": "Edwards",          // REQUIRED (sold-list match key)
  "address": "16408 Riggs Rd",    // property they own (see field mapping)
  "city": "Stilwell",
  "tags": ["Past Client"],        // tags + stage decide tier (past_client > coi)
  "stage": "Past Client",
  "closeDate": "2021-06-10",      // their purchase/closing date (anniversary, tenure, equity)
  "salePrice": 400000,            // original sale price (equity math) — number, no $/commas
  "lastContactDate": "2026-01-01" // most recent touch of any kind (referral/suppression)
}
```

**Graceful degradation (already handled by the engine):**
- No `salePrice` → no Equity moment, but anniversary / move-window / referral still fire.
- No `closeDate` → no anniversary/tenure/equity, but referral / re-engage still fire.
- No `lastContactDate` → treated as "no contact on file" → referral fires; nothing is suppressed.
- Missing `closeDate`/`salePrice`/`address` are **backfilled** from `vnre_sold_history.json`
  by `lastName` + `address`. So a thin pull still produces a useful brief.

---

## 2. Field mapping — where each value lives in FUB

| Output field | FUB source | Notes |
|---|---|---|
| `id`, `firstName`, `lastName`, `tags`, `stage` | `GET /people` | Standard person fields. |
| `address`, `city` | the **closed deal's property**, else `person.addresses[0]` | Past clients' mailing address is usually the home they bought — usable fallback. |
| `closeDate` | **closed deal** date, or a person custom field | See §4 confirmations. |
| `salePrice` | **closed deal** value/price, or a person custom field | See §4 confirmations. |
| `lastContactDate` | most recent of calls / texts / emails / notes / appointments, or a "Last Touch" custom field | Server-side max is cleanest (see helper, §3b). |

FUB API basics: base `https://api.followupboss.com/v1`, HTTP Basic auth with the API key as
username (`02 Reference/fub-api-key.local.md`), pagination via `limit` (max 100) + `offset`
or `_metadata.next`.

---

## 3. Two implementation paths

### 3a. Thin path — works TODAY with existing `fub_*` tools (no Joey)

Use this to ship now; equity precision improves later.

1. **Pull Past Clients.** `fub_search_people` with the Past Client stage/tag, paginate at
   limit 100. Request fields: `id, firstName, lastName, stage, tags, addresses, emails,
   customFields, updated`.
2. **Pull COI / Sphere.** Same call with the COI stage/tag.
3. **Per contact, set:**
   - `address`/`city` ← closed-deal property if you already surface deals, else
     `addresses[0].street`/`.city`.
   - `closeDate`/`salePrice` ← the matching custom fields **if** your team stores them
     (see §4); otherwise leave null and let the sold-list backfill handle it.
   - `lastContactDate` ← a "Last Touch" custom field if maintained; otherwise leave null
     (referral still fires) or fall back to `updated` (imprecise — flag it in the brief).
4. Write the array to the pull path. Run the engine (SKILL.md §2).

**Limitation:** without per-person deal/comm calls, equity depends on the sold-list carrying
prices, and suppression is weaker (no true last-contact). Acceptable for a first live run.

### 3b. Proper path — `fub_retention_pull` MCP helper (spec for Joey)

Mirror `fub_lead_attention_pull`: one server-side tool that does the joins and emits the
exact §1 schema, so Claude makes a single call.

```
fub_retention_pull({
  segments: ["Past Client", "COI"],   // stage/tag names to include
  outputPath: ".../retention-pull-YYYY-MM-DD.json",
  lookbackDays: 1095,                 // optional: ignore contacts with no deal in N days
  includeComms: true                  // compute lastContactDate server-side
})
```

Server logic:
1. Page `GET /people?stage=… / tags=…` for each segment → base records.
2. `GET /deals` filtered to **won/closed**, map by `people[].id` → `closeDate` +
   `salePrice` + property `address`/`city` (take the most recent closed deal per person).
3. If `includeComms`: for each person, `max(created)` across `GET /calls`, `/textMessages`,
   `/emails`, `/notes`, `/appointments` (or a single `/events` query) → `lastContactDate`.
   Batch/throttle to respect FUB rate limits (the X-System "VNRE-Claude" headers already
   give you the higher tier).
4. Emit the §1 array. Return a summary: counts per segment, how many had a closed deal,
   how many had comms, plus the `stageMap` (like the lead-attention tool) so Claude can
   re-call if a segment name didn't resolve.

This is the durable answer and a clean **aiDrVN Stage 08 product component**.

---

## 4. Confirm against your live FUB (3 unknowns I won't guess)

1. **Segment names.** What are the exact FUB **stage** and/or **tag** strings for past
   clients and for sphere/COI? (The engine's `tier_of()` looks for "past client"/"closed"
   and "coi"/"sphere" — tell me your real labels and I'll match them precisely.)
2. **Close date + sale price location.** Are these on **Deals** (FUB Deals API) or on
   **person custom fields** (e.g., "Closing Date", "Sale Price")? Give me the exact custom
   field names if the latter.
3. **Sold-history JSON.** Does `04 Tools/plp-presentation-builder/vnre_sold_history.json`
   carry **salePrice** per deal, or only family/address/city/year? Equity moments need a
   price from somewhere — FUB or this file.

Answer those three and I'll: (a) hardcode your real segment labels into the engine,
(b) finalize the thin-path field mapping, and (c) hand Joey a ready `fub_retention_pull`
spec to build the durable version.
