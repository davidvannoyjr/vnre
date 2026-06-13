---
name: vnre-content-engine
description: Chop one listing into a full multichannel launch package — reusable building blocks, a status-aware beat schedule, per-channel captions (IG feed/Stories, FB page/groups, LinkedIn), a Follow Up Boss email/SMS blast, and a graphics spec — in DVN voice. Use whenever DVN says "build the social plan for {address}", "launch content for this listing", "coming soon / just listed posts", "content package for {listing}", or wants the marketing for a property. aiDrVN Stage 02 (Attraction).
---

# VNRE Content Engine — Stage 02 (Attraction)

One listing in → the whole launch package out, in the exact structure of DVN's hand-built
social plans. Turns a single property (or status change) into weeks of multichannel content so
the marketing thrust runs without writing each post from scratch.

## Architecture
`listing.json` → `build_content_package.py` → Claude voice-polish → graphics + scheduling:

1. **Generate the package:** `python3 scripts/build_content_package.py --listing listing.json
   --out-md "<listing folder>/Social Plan.md" --out-json _data/content.json`. Produces building
   blocks (stat line, spec block, contact lockup, hooks), a **status-aware beat schedule**, the
   per-channel captions, the FUB email/SMS blast, and the graphics spec.
2. **Polish to DVN voice.** The captions are strong drafts; tighten any that feel generic, weave
   in the standout hooks, keep it declarative and concrete (no "stunning"/"must-see" filler).
3. **Graphics:** hand the graphics spec to the existing
   `premarket-social-automation/vnre_social_graphic.py` (or the Canva "Coming Soon / Just Listed"
   brand template) to render the banner per beat at 1080×1080 / 1080×1350 / 1080×1920. FB uses the
   native photo gallery, not the banner.
4. **Schedule:** route the schedule table to Publer (via Claude-in-Chrome) and the FUB blast to a
   saved template or Gmail draft — same flow as the premarket automation plan.

## Status-aware
`status` drives the beat sequence and the CTA:
- `coming_soon` → teaser / sneak peek / live-this-week; CTA = "get on the first-look list".
- `active` → Just Listed → feature spotlight → yard+value → still available → open house.
- `price_improvement` → New Price → still the best value.
- `just_sold` → social proof for sphere/farm ("thinking of selling?").
- `open_house` → announce + day-of.

## Inputs (listing.json)
Required: `address`. Strongly recommended: `city, state, neighborhood, status, price, beds, baths,
sqft, lot, hooks[], agent{name,company,phone,email}, launchDate`. Optional: `mls, schools, taxes,
year, openHouseDay/Time`. Missing fields degrade gracefully.

## Approval gate (one)
Nothing schedules or sends automatically. DVN approves the schedule + captions, confirms photo
selection and the Canva template, and confirms the FUB smart list — then it queues. (See the
`needsDvn` list the script emits.)

## Verify offline
`python3 scripts/build_content_package.py --selftest`
