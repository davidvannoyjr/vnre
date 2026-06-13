---
name: vnre-book-appointment
description: Turn a booked listing appointment into a well-formed Google Calendar `LA:` event (the exact format plp-folder-build parses) plus a FUB note, so the PLP folder + presentation pipeline runs automatically downstream. Use whenever DVN, an ISA, or Upfirst books a listing appointment — "book the LA for {name}", "add this listing appointment", "set the appointment", "got a listing appt" — or when a voice agent captures a booking. This is the Stage 01 booking → handoff bridge.
---

# VNRE Book Appointment — Stage 01 → PLP handoff bridge

The keystone of appointment-booking. A booked appointment becomes an `LA:` calendar event in
the precise shape `plp-folder-build` expects, so the rest of the machine runs on its own:

```
this skill ──▶ LA: {Name} event ──▶ plp-folder-build (7 AM) ──▶ PLP folder
                                                                  ──▶ plp-presentation packet
```

Works for any booking channel — you, an ISA, Upfirst (Alex/Jordan), or a future voice agent
all route through here, so there's one consistent on-ramp to the PLP pipeline.

## Steps

1. **Capture** the appointment into an appointment object: `name` and `datetime` are required;
   add whatever the call surfaced — property address, source, county, timeline, price
   expectation, beds/baths, condition, questions, notes, `plpInstructions`. (Missing fields are
   simply omitted — the more you capture on the call, the richer the auto-built pre-qual.)
2. **Build the payload:** `python3 scripts/build_la_event.py --appt appt.json`. Returns the
   `create_event` args (summary / start / end / location / description), the predicted PLP
   folder name, and the FUB note.
3. **Confirm with DVN.** Show the event summary, time, address, and the **predicted PLP folder**
   before creating — because creating the `LA:` event triggers `plp-folder-build` to make the
   folder and copy current contract forms. Don't double-book: `plp-folder-build` dedupes by last
   name, but check the calendar for an existing `LA:` for this client first.
4. **Create the event** via the Calendar MCP `create_event` using the payload's `create_event`
   block verbatim (summary, startTime, endTime, timeZone, location, description).
5. **Log to FUB:** add the payload's `fubNote` to the contact's record (`fub_add_note`), and set
   the stage to listing-appointment-booked.

## The LA: contract (don't break it)
- **Title:** `LA: {Name}` — the name after `LA:` becomes the PLP folder name. Never title it
  `LA: Template` (that's the recurring template event the builder skips).
- **Location:** street + city (+ state) — used for the folder address and the appointment city.
- **Description:** the pre-qual format this script emits — `plp-folder-build` parses it into the
  Pre-Qual Summary doc. Keep the section headings.

## Notes
- Time zone defaults to America/Chicago (KC metro). Duration defaults to 60 min.
- This is the buildable-now core of Stage 01 (see `SCOPE.md`). The Active-Hunter targeting,
  script library, no-answer nurture, and the Vapi/Twilio voice overlay all book *through* this
  bridge — none of them change the contract above.

## Verify offline
`python3 scripts/build_la_event.py --selftest`
