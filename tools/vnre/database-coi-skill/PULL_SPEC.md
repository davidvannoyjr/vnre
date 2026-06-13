# FUB Pull Spec — vnre-database-coi (Stage 08)

The pull is implemented and self-owned: **`scripts/fub_pull.py`** talks directly to the
Follow Up Boss v1 REST API and emits exactly the schema below. This doc is the contract +
the FUB field map, so you can verify it against your live account.

---

## 1. Output contract (what the engine consumes)

`fub_pull.py` writes `{"pulledAt", "count", "contacts": [...]}` where each contact is:

```jsonc
{
  "id": "12345",                    // FUB person id (REQUIRED — dedupe key)
  "firstName": "Andrew",
  "lastName": "Edwards",
  "address": "16408 Riggs Rd",      // property owned (won-deal address, else person address)
  "city": "Stilwell",
  "tags": ["Past Client"],
  "stage": "Past Client",
  "email": "andrew@…",              // for Gmail drafts
  "closeDate": "2021-06-10",        // most-recent won deal (anniversary, tenure, equity)
  "salePrice": 400000,              // most-recent won deal (equity math)
  "lastContactDate": "2026-01-01",  // max across calls/texts/emails/notes (referral/suppress)
  "recentPropertyViewDate": "2026-06-01",  // latest property-view event (ACTIVE-MOVE signal)
  "mortgageRate": 7.5,              // custom field -> refi touch
  "birthday": "06-15",              // custom field -> birthday touch
  "preferredChannel": "text",       // custom field -> shown on each line
  "lifetimeValue": 18500            // custom field / QBO -> CLV score boost
}
```

Everything except `id` degrades gracefully — the engine fires whatever moments the present
fields support, and backfills `closeDate`/`salePrice`/`address` from `vnre_sold_history.json`.

## 2. FUB sources `fub_pull.py` reads

| Output | FUB endpoint | Notes |
|---|---|---|
| base person fields, tags, stage, addresses, custom fields | `GET /people?fields=allFields` filtered by each segment | paginated |
| `closeDate`, `salePrice`, property `address`/`city` | `GET /deals` (status Won) joined by `people[].id` | most-recent won deal wins |
| `lastContactDate` | bulk `GET /calls /textMessages /emails /notes` (newest-first, stop past lookback) | scalable — no per-person calls |
| `recentPropertyViewDate` | `GET /events` filtered to property/view types | the move-intent signal |
| `mortgageRate`, `birthday`, `preferredChannel`, `lifetimeValue` | person custom fields (read by display name, several aliases) | optional, sharpen moments |

The client handles HTTP Basic auth (API key as username), the `X-System` / `X-System-Key`
headers (your "VNRE-Claude" higher-rate tier), 429 back-off, and pagination. Run
`python3 fub_pull.py --selftest` to verify the join logic offline (no network).

## 3. Confirmed with DVN (2026-06-13) ✅

1. **Segment labels** — **Past Client, COI, DVN COI, Agent COI**. Set in `config.example.json →
   segments`. Per the operating manual, Past Client + DVN COI + Agent COI are **Tier 1** (the
   engine's `tier_of` now ranks them top); plain COI is Tier 2.
2. **Close date + sale price** — on **FUB Deals** ✅. `fub_pull.py` already reads the most-recent
   won deal for `closeDate` + `salePrice`, so equity/anniversary/tenure work for any client whose
   purchase is in FUB. (Clients who bought before FUB won't have a deal → no equity touch, but
   anniversary/move-window/referral still fire from the sold history.)
3. **Sold-history JSON** — **no sale price** ❌. So CLV (`clv-sync`) can't price historical
   closings; it uses **closings-count × avgGci.default** (a loyalty/transaction-count value) and
   should be enriched with FUB deal prices for FUB-era buyers. See `clv-sync config.example.json`.

See [`ENRICHMENTS.md`](ENRICHMENTS.md) for the custom fields worth adding and how the rest of
your connectors plug in.
