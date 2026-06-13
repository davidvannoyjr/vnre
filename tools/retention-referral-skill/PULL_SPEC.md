# FUB Pull Spec — vnre-retention-referral (Stage 08)

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

## 3. Confirm against your live FUB (so I can hardcode the right labels)

1. **Segment labels** — exact **stage** and/or **tag** strings for past clients and for
   sphere/COI. Put them in `config.json → segments` (and they also drive the engine's tiering).
2. **Close date + sale price** — on FUB **Deals**, or on **person custom fields**? `fub_pull.py`
   checks deals first, then custom fields named "Closing Date"/"Sale Price" (and aliases) —
   tell me your real field names if they differ.
3. **Sold-history JSON** — does `vnre_sold_history.json` carry **salePrice**, or only
   family/address/city/year? Equity needs a price from a deal, a custom field, or this file.

See [`ENRICHMENTS.md`](ENRICHMENTS.md) for the custom fields worth adding and how the rest of
your connectors plug in.
