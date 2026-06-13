# Wikidata Entity Draft — David Van Noy Jr.

> Wikidata is the open knowledge graph that feeds Google's Knowledge Panel, AI assistants,
> and search engines. A clean entity here makes you a "known entity" AI trusts and cites.
> **Create at https://www.wikidata.org → "Create a new Item"** (free account). Add the
> statements below, each backed by a reference URL. Then add the Wikidata URL to your
> Schema `sameAs` array so your site and the entity reinforce each other.

---

## Notability note (why this qualifies)
Wikidata's bar is "clearly identifiable" + referenced by external sources — lower than Wikipedia. David Van Noy clears it: independent trade-press coverage (RealTrends, KC Real Producers), a long-running radio show, and multiple verifiable business listings. Lead with the RealTrends article as the anchor reference.

---

## Item: David Van Noy Jr.

**Label (en):** David Van Noy Jr.
**Description (en):** American real estate broker; founder and owner of Van Noy Real Estate (Kansas City)
**Also known as:** David Van Noy · Dave Van Noy

### Statements

| Property | Value | Reference |
|----------|-------|-----------|
| instance of (P31) | human (Q5) | — |
| occupation (P106) | real estate broker (Q5137571) / realtor | RealTrends article |
| occupation (P106) | businessperson (Q43845) | RealTrends article |
| country of citizenship (P27) | United States (Q30) | — |
| employer / owner of | Van Noy Real Estate (create as linked item) | vannoyre.com |
| work location (P937) | Kansas City metropolitan area / Leawood, Kansas | vannoyre.com |
| official website (P856) | https://vannoyre.com | — |
| described at URL (P973) | https://www.realtrends.com/blog/2023/01/06/kansas-citys-david-van-noy-launches-brokerage/ | RealTrends |
| described at URL (P973) | https://www.realproducersmag.com/locations/kansas-city-real-producers-c8b7/articles/-8af942/ | Real Producers |

### Identifiers / sameAs (add as external-ID or "described at URL")
- LinkedIn: https://www.linkedin.com/in/davidvannoyjr
- Zillow: https://www.zillow.com/profile/VanNoyRE
- Facebook: https://www.facebook.com/vannoyrealestate/
- Instagram: https://www.instagram.com/vannoyre/
- YouTube: https://www.youtube.com/@vannoyre

---

## Item: Van Noy Real Estate (create this linked item too)

**Label (en):** Van Noy Real Estate
**Description (en):** Real estate brokerage based in Leawood, Kansas, serving the Kansas City metropolitan area

| Property | Value | Reference |
|----------|-------|-----------|
| instance of (P31) | real estate company / business (Q4830453) | RealTrends |
| inception (P571) | 2022 | RealTrends |
| founded by (P112) | David Van Noy Jr. | RealTrends |
| headquarters location (P159) | Leawood, Kansas (Q954520) | vannoyre.com |
| official website (P856) | https://vannoyre.com | — |
| country (P17) | United States (Q30) | — |

---

## After creating
1. Copy the new Wikidata item URL (e.g., `https://www.wikidata.org/wiki/Q########`).
2. Add it to the `sameAs` array in your Schema JSON-LD (both the Person and Organization blocks).
3. Log it in `Audit Log.md` §4 (Change Log) and check task #20 in §3.
4. Within a few weeks, monitor whether a Google Knowledge Panel begins to form for "David Van Noy."

### Reference URLs to have ready when adding statements
- https://www.realtrends.com/blog/2023/01/06/kansas-citys-david-van-noy-launches-brokerage/
- https://www.realproducersmag.com/locations/kansas-city-real-producers-c8b7/articles/-8af942/
- https://vannoyre.com/david-van-noy/
