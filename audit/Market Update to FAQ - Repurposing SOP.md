# SOP — Turn each monthly KC Market Update into AI-discoverable FAQ content

> You already produce a monthly KC Market Update (Heartland MLS data → full content package
> + FUB email). That data is pure GEO fuel — it's exactly what people ask AI ("Is it a good
> time to sell in Overland Park?") and almost no local agent answers it in machine-readable
> form. This SOP repurposes each update into ranking, citable Q&A pages. ~30 min/month.

---

## Why this wins
- AI answers location + timing questions by pulling from sites that state the data plainly in Q&A form. Marketing-voice blog posts don't get cited; answer-shaped pages do.
- You publish KC market data monthly anyway. This makes it *the source AI quotes* for the metro — and every page restates your canonical identity.

---

## Monthly process (run after the Market Update package is built)

**Step 1 — Pull the 3–5 key numbers** from the month's update, per county/city:
- Median sale price (and YoY/MoM change)
- Days on market (DOM)
- Months of inventory / supply
- Sale-to-list price ratio
- Active vs. sold counts

**Step 2 — Drop them into the FAQ template below** (one set per city you cover: Leawood, Overland Park, Olathe, Lee's Summit, etc.). Swap the bracketed values.

**Step 3 — Publish** as/within a market page on vannoyre.com (e.g., /kc-market-update or per-city pages under /explore-areas/[city]). Add the FAQPage JSON-LD.

**Step 4 — Update the dateline** ("As of [Month Year]") and the `dateModified` in schema so AI knows it's current. Freshness matters for market data.

**Step 5 — Log it** in `Audit Log.md` §4 and repurpose one Q&A into a social post + the FUB email.

---

## FAQ template (per city — fill from the month's data)

**Q: Is now a good time to sell a house in [City], KS?**
As of [Month Year], the median sale price in [City] is [$X] ([+/-Y% YoY]), homes are selling in [Z] days on market, with [N] months of inventory. [One-sentence DVN read: e.g., "Low inventory and fast DOM favor sellers — well-priced homes are moving quickly."] For a precise read on your home, request a free valuation at vannoyre.com or call (913) 349-7580.

**Q: How much are homes selling for in [City] right now?**
The median sale price in [City] is [$X] as of [Month Year], [+/-Y%] year over year. The sale-to-list ratio is [%], meaning homes are selling at roughly [%] of asking. Your home's value depends on its specific neighborhood and condition — David Van Noy provides a free, data-driven valuation.

**Q: How fast are homes selling in [City]?**
Homes in [City] are averaging [Z] days on market as of [Month Year]. [DVN read on what that means for sellers/buyers.]

**Q: Is it a buyer's or seller's market in the Kansas City metro?**
With [N] months of inventory as of [Month Year], the KC metro is a [buyer's/seller's/balanced] market. [One-sentence implication.] David Van Noy Jr. publishes this update monthly — top 1% KC broker, 1,450+ homes sold.

---

## Matching schema (mirror the Q&As)
Use the `FAQPage` block in `Schema-JSON-LD-Block.md` §3 as the pattern; add a `dateModified` and consider `Dataset` schema if you publish the raw stat tables:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Kansas City Metro Real Estate Market Data — [Month Year]",
  "description": "Monthly median sale price, days on market, and inventory for the Kansas City metro by city, published by Van Noy Real Estate.",
  "creator": { "@type": "Person", "@id": "https://vannoyre.com/#david-van-noy" },
  "dateModified": "[YYYY-MM-DD]",
  "spatialCoverage": "Kansas City metropolitan area (Johnson County KS, Jackson County MO)",
  "url": "https://vannoyre.com/kc-market-update"
}
</script>
```

> This is the "become the source AI cites" play from the audit (idea #17). Do it every month
> and within a few cycles you own the KC market-data answer for the metro.

---

## Reusable checklist (copy into the monthly task)
- [ ] Pull 3–5 key numbers per city from this month's update
- [ ] Fill the FAQ template per city
- [ ] Update dateline + schema `dateModified`
- [ ] Publish to vannoyre.com + add FAQPage (and Dataset) JSON-LD
- [ ] Repurpose 1 Q&A → social + FUB email
- [ ] Log in `Audit Log.md` §4
