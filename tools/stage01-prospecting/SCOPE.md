# Stage 01 — Prospecting & Appointment-Booking (SCOPE)

Goal: a **full listing calendar**. The plan needs **120 listing appointments → 100 taken →
75 sold**. Stage 01 is the funnel that feeds everything else. This scopes how AI plugs in,
what's buildable **now** with no new vendor, and what needs a voice platform + a compliance
sign-off.

## The keystone insight

Everything *downstream* of a booked appointment is already automated:

```
booked appt  ──▶  Google Calendar "LA: {Name}" event
                      │  (plp-folder-build, daily 7 AM)
                      ▼
                  PLP folder built  ──▶  comps + pre-qual  ──▶  plp-presentation
                                                                  (16-page packet)
```

So Stage 01's job reduces to one reliable output: **a well-formed `LA:` calendar event** (title
`LA: {Name}`, location = property address, description = the pre-qual template). Hit that and
the rest of the machine runs. That's the spine of this scope.

## The funnel & where AI plugs in

| Step | What happens | Build status |
|---|---|---|
| 1. Target | Rank who to work today: FSBO, expired, aged internet leads, circle/COI, geo-farm | **Buildable now** |
| 2. Reach | Dial / text / email the target with the right script | Voice = **vendor**; text/email = now |
| 3. Qualify | Run the segment script, capture answers | Voice = vendor; manual = now |
| 4. Book | Turn a "yes" into an `LA:` event + FUB log | **Buildable now (keystone)** |
| 5. Hand off | `LA:` event → PLP pipeline | **Already built** |
| 6. Nurture | Multi-touch follow-up for no-answers | **Buildable now** |

## A. Buildable NOW — no new vendor

1. **Active-Hunter targeting** (`build_call_list.py`) — same scoring pattern as
   `daily-lead-attention`: pull FUB by segment (FSBO / Expired / Aged Lead / COI / Past Client),
   score by signal × stage × recency × tier, output a ranked daily call list with the right
   **script per segment** attached. Filters DNC / opt-out up front (see Compliance).
2. **Script library** — FSBO, Expired, Aged-Lead, Circle/COI, and Just-Listed/Just-Sold
   neighbor scripts in DVN voice, living in `02 Reference/Scripts/`. (The plan's Key Initiative
   "standardize presentation and training materials.")
3. **Booking → handoff bridge** (`book_appointment.py`) — the keystone. Given a booked
   appointment from *any* channel (DVN, ISA, Upfirst, or a voice agent), create the Google
   Calendar `LA:` event in the exact format `plp-folder-build` consumes, pre-fill the pre-qual
   template from the call, and log the appointment to FUB. Calendar MCP is already connected.
4. **No-answer nurture** — for non-connects, generate the multi-touch text/email follow-up
   sequence as drafts (FUB + Gmail), so no lead goes cold from a missed dial.

## B. Needs a voice platform (scope only) — Vapi / Twilio + Upfirst

5. **Outbound voice agent** — Vapi (LLM voice) over Twilio numbers, running the segment
   scripts from A2, booking straight into the A3 bridge. This is the autonomous-dialing piece.
6. **Inbound triage** — you already run **Upfirst (Alex inbound, Jordan routing)**. Integrate
   so Upfirst-booked appointments also flow through the A3 bridge → same PLP pipeline.

These are the only vendor-dependent parts. They are an **overlay** on A, not a prerequisite —
A makes every human call more productive today and is what the voice agent plugs into later.

## C. Compliance — non-negotiable design gate (before any autonomous dialing)

Automating outbound calls raises real legal exposure. Build these in from the start; the
voice overlay does **not** ship until they're signed off:

- **DNC scrubbing** — National DNC + state lists + your internal DNC, scrubbed before every
  campaign. Targeting (A1) filters these out.
- **TCPA consent** — track consent basis per contact; autodialer/voice rules differ for cold
  vs. prior-relationship (past clients/COI are lower risk than cold FSBO/expired).
- **Two-party recording consent** — KS is one-party, **MO is all-party**; if calls are
  recorded, lead with the disclosure. You operate in both.
- **Calling-hours windows** + an **opt-out tag** in FUB honored everywhere (ties to the
  retention engine's opt-out guard).
- **AI disclosure** — emerging rules may require disclosing an AI caller; script for it.

> This is automation of prospecting you already do (Mojo, 150 calls/day) — the gate is about
> doing it at machine scale safely, not about whether it's allowed.

## D. Data model

- **FUB:** segment stage/tags (FSBO, Expired, Aged Lead, COI, Past Client), `DNC`/`Opt-Out`
  tag, consent basis, source. Lists sourced via Mojo / expired-FSBO data into FUB.
- **Calendar:** the `LA:` event contract (already defined by `plp-folder-build`).
- **Pre-qual template:** the `LA: Template` description format the PLP build parses.

## E. Phased plan

1. **Booking → handoff bridge (A3)** — *start here.* Immediately useful even at 100% human
   dialing; it's the keystone every other path books into, and it lights up the whole PLP
   pipeline from any "yes."
2. **Active-Hunter targeting + scripts (A1, A2)** — make the call hours productive.
3. **No-answer nurture (A4)** — stop leaking non-connects.
4. **Compliance checklist (C)** — sign off before any voice automation.
5. **Voice overlay (B5/B6)** — Vapi/Twilio outbound + Upfirst inbound into the A3 bridge.

## Recommendation

Build **A3 (the booking bridge) first.** It's small, buildable now with the connected Calendar
MCP, useful on day one regardless of who's dialing, and it's the socket the voice agent plugs
into later — so nothing here is wasted or blocked on a vendor decision.
