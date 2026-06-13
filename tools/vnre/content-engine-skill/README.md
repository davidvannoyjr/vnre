# vnre-content-engine — Stage 02 (Attraction)

Chops one listing into a full multichannel launch package — building blocks, a status-aware
beat schedule, per-channel captions (IG feed/Stories, FB page/groups, LinkedIn), a FUB
email/SMS blast, and a graphics spec — matching DVN's hand-built social plans.

Pairs with the existing `premarket-social-automation` (graphic generator + Canva template +
Publer/Claude-in-Chrome scheduling): this engine writes the **copy + schedule + plan**, that
handles the **visuals + posting**.

## Files
```
content-engine-skill/
├── SKILL.md, README.md
├── scripts/build_content_package.py
└── sample/sample_listing.json
```

## Try it (no network)
```bash
python3 scripts/build_content_package.py --selftest
python3 scripts/build_content_package.py --listing sample/sample_listing.json \
  --out-md /tmp/plan.md --out-json /tmp/plan.json && sed -n '1,40p' /tmp/plan.md
```

## Status sets the play
`coming_soon` (first-look capture) · `active` (Just Listed → spotlights → still available → open
house) · `price_improvement` · `just_sold` (social proof) · `open_house`.

## Output
- `--out-md`: the human social plan (building blocks, schedule table, captions, FUB blast,
  graphics spec, approval checklist) — drop it in the listing's folder.
- `--out-json`: structured plan (beats, schedule, captions, Canva spec) for the graphic generator
  and Publer scheduling.

> Captions are strong drafts in DVN voice — polish the standouts before scheduling. Graphics go
> to `vnre_social_graphic.py` / the Canva brand template. Nothing posts without DVN's approval.
