# VNRE Tool Suite — the aiDrVN operating modules

Code modules that automate Van Noy Real Estate, mapped to DVN's own **aiDrVN 9-stage model**.
Every module is built to run on the existing stack (Follow Up Boss, QuickBooks, Google
Workspace, Canva, Granola — all connected) with **no third-party dependency**. VNRE is the lab;
proven modules become sellable aiDrVN product components.

Design rules across all modules: deterministic Python (no network in the scoring layer),
offline `--selftest`, tunable constants at the top, **approval-gated** outputs (nothing sends or
writes automatically), and secrets/financials kept out of git.

## Layout & ownership

```
tools/vnre/    🏢 runs the brokerage (almost everything)
tools/shared/  🔁 dual-use VNRE + DVN Coaching (call-coach today)
```

**[`MANIFEST.md`](MANIFEST.md) is the authoritative per-module classification** (business,
maturity, keep) — read it before merging to see exactly what's VNRE vs. coaching-overlap.
(In Drive these live flat under `04 Tools/`; the vnre/shared split is repo-clarity only.)

## Module index

| Module | Stage | What it does | Status | To go live |
|---|---|---|---|---|
| `active-hunter-skill` | 01 Prospect | Daily ranked call list (FSBO/Expired/Aged/COI/Past) + DVN-voice scripts + nurture; DNC/opt-out filtered | ✅ built | FUB segment labels |
| `stage01-prospecting` (book-appointment) | 01 Prospect | Booking → `LA:` calendar event → PLP pipeline (the keystone) | ✅ built | confirm-gate live |
| `stage01-prospecting/SCOPE.md` | 01 Prospect | Voice overlay (Vapi/Twilio) + Upfirst inbound + compliance | 📋 scoped | vendor + compliance sign-off |
| `content-engine-skill` | 02 Attraction | Listing → multichannel launch package (captions, schedule, FUB blast, graphics spec) | ✅ built | photo selection per listing |
| `compliance-auditor-skill` | 06 Compliance | Transaction-file completeness vs per-stage checklist (missing / verify-sig / deadlines) | ✅ built | confirm form set w/ broker |
| `ceo-dashboard-skill` | 07 Finance | Weekly QuickBooks actuals vs 2026 plan + 50% margin guard + A/R flag | ✅ built | nothing (QBO connected) |
| `database-coi-skill` | 08 Database/COI | 2-lane brief: Customer Care + Opportunity & Database Mgmt (8 moments) | ✅ built | live `config.json` (key + segments confirmed) |
| `clv-sync-skill` | (cross) | Client Lifetime Value from closings → FUB; QBO partner-value brief | ✅ built | create `Lifetime Value` field |
| `call-coach-skill` | 09 Scale | Granola transcript → script-adherence self-coaching (phases, objections, talk ratio, drills) | ✅ built | Granola transcripts |
| `scheduled-tasks` | — | Standing Cowork task definitions for the above | ✅ defined | create in Cowork |

Pre-existing skills (in Drive `04 Tools/`, referenced by the master manual): `plp-build`,
`plp-presentation`, `send-ers-agreement`, `daily-lead-attention`, `vnre-html-branding`, `dvn-voice`.

## 9-stage coverage

```
01 Prospect    ✅ active-hunter + book-appointment   (voice overlay scoped)
02 Attraction  ✅ content-engine  (pairs with premarket-social graphic gen + Publer)
03 Prep        ✅ plp-build + plp-presentation (pre-existing)
04 Closing     ✅ offer-to-spreadsheet (pre-existing)
05 Operations  ✅ send-ers-agreement (pre-existing)   (full milestone automation = later)
06 Compliance  ✅ compliance-auditor  (checklist-driven; broker signs off)
07 Finance     ✅ ceo-dashboard
08 Database/COI   ✅ database-coi  (+ clv-sync profit-weighting)
09 Scale       ✅ call-coach  (self mode; client/agent modes ready)
```

**All 9 stages built or scoped.** (01 voice overlay is the one scoped-not-built piece, gated on
a vendor + compliance sign-off.)

## How it connects

```
active-hunter ─(connect)─▶ book-appointment ─▶ LA: event ─▶ plp-build ─▶ plp-presentation ─▶ ERS send
      │(no answer)                                                                                │
      ▼                                                                                           ▼
   nurture seq                                                                              closed deal
                                                                                                  │
clv-sync ──(Lifetime Value)──▶ database-coi ◀──(past clients + sold history)───────────────┘
ceo-dashboard ◀── QuickBooks ── watches revenue pace, 50% margin, A/R
```

A booked appointment lights the whole downstream pipeline; closings feed CLV; CLV profit-weights
database & COI + active-hunter refill the funnel; the CEO dashboard watches the money.

## Per-device setup (live)
- `followupboss` MCP connected (active-hunter, database & COI, clv-sync, lead brief).
- QuickBooks MCP connected (ceo-dashboard, clv-sync partner view).
- Skills saved in Claude desktop; each tool's `config.json` filled from its `config.example.json`.
- Schedules created from `scheduled-tasks/`.

## Open items before full live operation
> The "3 FUB facts" were **confirmed with DVN 2026-06-13** (see `database-coi-skill/PULL_SPEC.md §3`):
> segments = Past Client / COI / DVN COI / Agent COI; close-date + sale price live on FUB **Deals**;
> sold-history JSON carries **no** price (CLV falls back to closings-count × `avgGci.default`). Those
> are settled — they're baked into the `config.example.json` files. What remains is activation, below.

1. **Live `config.json` per skill** — copy each `config.example.json` → `config.json` (gitignored)
   and fill real `xSystemKey` + `avgGci.default`. Desktop-only: needs the FUB key in Drive
   (`fub-api-key.local.md`).
2. **`Lifetime Value` custom field** — run `clv-sync-skill/scripts/fub_field_setup.py --create`
   to create/verify it (and the other suite fields); falls back to admin-UI steps if the API
   doesn't permit field creation. Then set `clv-sync` `customFieldName` = "Lifetime Value".
3. **Compliance checklist** (Stage 01 voice): DNC/TCPA/two-party consent (KS one-party, MO all-party).
4. **Voice vendor** decision (Vapi/Twilio) for autonomous dialing + Upfirst inbound integration.

## Next candidates (enhancements, not gaps)
- **Stage 01 voice overlay** — Vapi/Twilio outbound + Upfirst inbound (gated on compliance sign-off).
- **Call-coach client/agent modes** — turn Stage 09 into a DVN Coaching / new-agent product.
- **Deeper compliance** — PDF AcroForm signature-field parsing.

Recently added: **database & COI delivery layer** (`build_delivery.py` → Gmail drafts + Canva equity
one-pagers + manual queue) and **FUB field setup** (`fub_field_setup.py`) — both built.
