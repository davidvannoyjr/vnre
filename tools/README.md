# VNRE Tool Suite — the aiDrVN operating modules

Code modules that automate Van Noy Real Estate, mapped to DVN's own **aiDrVN 9-stage model**.
Every module is built to run on the existing stack (Follow Up Boss, QuickBooks, Google
Workspace, Canva, Granola — all connected) with **no third-party dependency**. VNRE is the lab;
proven modules become sellable aiDrVN product components.

Design rules across all modules: deterministic Python (no network in the scoring layer),
offline `--selftest`, tunable constants at the top, **approval-gated** outputs (nothing sends or
writes automatically), and secrets/financials kept out of git.

## Module index

| Module | Stage | What it does | Status | To go live |
|---|---|---|---|---|
| `active-hunter-skill` | 01 Prospect | Daily ranked call list (FSBO/Expired/Aged/COI/Past) + DVN-voice scripts + nurture; DNC/opt-out filtered | ✅ built | FUB segment labels |
| `stage01-prospecting` (book-appointment) | 01 Prospect | Booking → `LA:` calendar event → PLP pipeline (the keystone) | ✅ built | confirm-gate live |
| `stage01-prospecting/SCOPE.md` | 01 Prospect | Voice overlay (Vapi/Twilio) + Upfirst inbound + compliance | 📋 scoped | vendor + compliance sign-off |
| `content-engine-skill` | 02 Attraction | Listing → multichannel launch package (captions, schedule, FUB blast, graphics spec) | ✅ built | photo selection per listing |
| `ceo-dashboard-skill` | 07 Finance | Weekly QuickBooks actuals vs 2026 plan + 50% margin guard + A/R flag | ✅ built | nothing (QBO connected) |
| `retention-referral-skill` | 08 Retention | 8-moment retention/referral brief (equity, anniversary, move, refi, birthday, referral…) | ✅ built | 3 FUB facts |
| `clv-sync-skill` | (cross) | Client Lifetime Value from closings → FUB; QBO partner-value brief | ✅ built | `Lifetime Value` field |
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
06 Compliance  ⬜ file auditor — not yet built
07 Finance     ✅ ceo-dashboard
08 Retention   ✅ retention-referral  (+ clv-sync profit-weighting)
09 Scale       ⬜ AI call-coach — not yet built
```

## How it connects

```
active-hunter ─(connect)─▶ book-appointment ─▶ LA: event ─▶ plp-build ─▶ plp-presentation ─▶ ERS send
      │(no answer)                                                                                │
      ▼                                                                                           ▼
   nurture seq                                                                              closed deal
                                                                                                  │
clv-sync ──(Lifetime Value)──▶ retention-referral ◀──(past clients + sold history)───────────────┘
ceo-dashboard ◀── QuickBooks ── watches revenue pace, 50% margin, A/R
```

A booked appointment lights the whole downstream pipeline; closings feed CLV; CLV profit-weights
retention; retention + active-hunter refill the funnel; the CEO dashboard watches the money.

## Per-device setup (live)
- `followupboss` MCP connected (active-hunter, retention, clv-sync, lead brief).
- QuickBooks MCP connected (ceo-dashboard, clv-sync partner view).
- Skills saved in Claude desktop; each tool's `config.json` filled from its `config.example.json`.
- Schedules created from `scheduled-tasks/`.

## Open items before full live operation
1. **3 FUB facts** (retention + CLV): segment labels, where close-date/price live, whether the
   sold JSON carries price/commission.
2. **`Lifetime Value` custom field** — run `clv-sync-skill/scripts/fub_field_setup.py --create`
   to create/verify it (and the other suite fields); falls back to admin-UI steps if the API
   doesn't permit field creation.
3. **Compliance checklist** (Stage 01 voice): DNC/TCPA/two-party consent (KS one-party, MO all-party).
4. **Voice vendor** decision (Vapi/Twilio) for autonomous dialing + Upfirst inbound integration.

## Not yet built (next candidates)
- **Stage 06 Compliance** — file auditor (missing-signature/PDF checks).
- **Stage 09 Scale** — AI call-coach (Granola transcripts → script feedback).

Recently added: **retention delivery layer** (`build_delivery.py` → Gmail drafts + Canva equity
one-pagers + manual queue) and **FUB field setup** (`fub_field_setup.py`) — both built.
