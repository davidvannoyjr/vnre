---
name: vnre-active-hunter
description: Build DVN's daily Active-Hunter call list — ranked outbound prospecting targets across FSBO, Expired, Aged Lead, Geo-farm, COI, and Past Client, each with the right DVN-voice script attached, DNC/opt-out filtered out. Use whenever DVN says "build my call list", "who do I prospect today", "hunt list", "FSBO/expired calls", or when the active-hunter task fires. Connects to vnre-book-appointment on a yes, and the nurture sequences on a no-answer.
---

# VNRE Active Hunter — Stage 01 daily targeting

Feeds the funnel: ranks who to dial today across the prospecting segments, attaches the matching
script, and filters DNC/opt-out before anything surfaces. A connect routes to
`vnre-book-appointment`; a no-answer routes to the nurture sequence. The point is a productive
prospecting block aimed at the plan's **120 listing appointments**.

## Architecture
Same shape as the lead/Database & COI briefs: FUB pull → deterministic ranking → review → work it.

1. **Pull** prospecting contacts from FUB (FSBO, Expired, Aged Lead, Geo-farm, COI, Past Client)
   with `id, name, phone, address/city, tags, stage, segment?, lastAttemptDate, attempts, signal`,
   and any DNC/opt-out tag. (`fub_pull.py` patterns apply; or `fub_search_people` by stage/tag.)
2. **Rank:** `python3 scripts/build_call_list.py --pull pull.json --out "<home>/<today> Call List.md"`.
   Listing-intent segments (FSBO/Expired) rank highest; filters DNC/opt-out, contacts dialed within
   2 days, and anyone past the attempt cap.
3. **Work it:** for each contact, open the attached `call-scripts/<segment>.md`.
   - **Connect → appointment:** capture the pre-qual on the call, then run **`vnre-book-appointment`**
     (creates the `LA:` event → PLP pipeline).
   - **No connect:** log the attempt to FUB; draft the next touch from `call-scripts/_nurture-sequences.md`
     (Gmail/text drafts, approval-gated). Stop on reply or opt-out.

## Scripts
`call-scripts/` — FSBO, Expired, Aged-Lead, Circle-COI, Past-Client (DVN voice, real VNRE USPs +
objection handlers + close-to-appointment), and `_nurture-sequences.md`. These also belong in
Drive `02 Reference/Scripts/`.

## Compliance (non-negotiable)
DNC/opt-out are filtered by the script, but you still own: TCPA consent basis per segment (cold
FSBO/expired carry more risk than past-client/COI), KS/MO **calling-hours** windows, and recording
consent (KS one-party, **MO all-party**). See `stage01-prospecting/SCOPE.md §C`. This skill is
human-dial targeting; the autonomous voice overlay does not ship until that checklist is signed.

## Cadence
Daily, with the morning prospecting block (paired with `daily-lead-attention`). Tuning constants
(segment weights, suppression window, attempt cap, cap) at the top of `build_call_list.py`.

## Verify offline
`python3 scripts/build_call_list.py --selftest`
