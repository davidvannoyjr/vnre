# Van Noy Profile & AI Discoverability Audit

**Subject:** David Van Noy Jr. / Van Noy Real Estate (VNRE) / DVN Coaching
**Date:** 2026-06-13
**Goal:** One identity, repeated everywhere, machine-readable — so any AI (ChatGPT, Gemini, Perplexity, Google AI Overviews, Copilot) returns the same correct answer about who you are, what you do, and how to reach you.

---

## 1. The verdict

Your footprint is wide but **fragmented and stale**. You show up in a lot of places — that's the good news. The bad news: those places disagree with each other on your name, your phone, your address, your years of experience, and your homes-sold count. When an AI assembles an answer about "David Van Noy real estate Kansas City," it averages the conflict and hedges. You read as *three different businesses* (Van Noy Real Estate, The Van Noy Group, and a stale ReeceNichols-era agent) instead of one authority.

**This is fixable in ~2 weeks of focused work, and most of it is free.** The fix is not "more profiles." It's **collapsing duplicates, locking one canonical record, and adding the structured data AI engines actually read.**

Three numbers tell the story:
- **4+** live websites pointing at you, at least two of which are stale or off-brand.
- **2** duplicate Zillow profiles splitting your reviews and authority.
- **5** different "facts" about your experience in the wild (18, 20, 22, 23+ years; "1,000+" vs "1,450+" homes).

---

## 2. Where you currently show up (profile inventory)

| # | Platform | URL | Status | Problem |
|---|----------|-----|--------|---------|
| 1 | **Brokerage site (primary)** | vannoyre.com | ✅ Canonical | Make this the hub everything links to. |
| 2 | Legacy IDX site | kchomelistings.com | 🔴 Retire/redirect | Still calls you "featured agent at ReeceNichols." Factually wrong now. |
| 3 | Secondary site | thevannoygroup.com | 🟠 Consolidate | Old team brand. Redirect to vannoyre.com. |
| 4 | **KW subdomain site** | vannoy-homes.kw.com | 🔴 Kill | A Keller Williams-hosted page in your name. Off-brand, confuses AI about your brokerage. |
| 5 | Guarantee landing page | vannoyre.com/yourhomesold | ✅ Keep | Good asset — link it from profiles. |
| 6 | Personal bio page | vannoyre.com/david-van-noy/ | ✅ Keep | Needs schema markup (see §4). |
| 7 | **Zillow (A)** | zillow.com/profile/VanNoyRE | 🟠 Pick ONE | Duplicate — splits reviews & ranking. |
| 8 | **Zillow (B)** | zillow.com/profile/VanNoyGroup | 🔴 Merge/retire | Old "Van Noy Group" brand. Consolidate into one. |
| 9 | LinkedIn (personal) | linkedin.com/in/davidvannoyjr | 🟠 Update | Headline still leads with a raw cell number, not positioning. |
| 10 | LinkedIn (company) | linkedin.com/company/vannoyre | ✅ Keep | Verify NAP + add description. |
| 11 | Homes.com | homes.com/real-estate-agents/david-van-noy-jr/m52eksj/ | 🟠 Claim/update | Stale experience figure. |
| 12 | FastExpert (agent + company) | fastexpert.com/agents/david-van-noy-23523/ | ✅ Keep | 82 reviews — asset. Sync bio. |
| 13 | Agent Pronto | agentpronto.com/agents/david-van-noy-83176 | 🔴 Fix brand | Listed as "The Van Noy Group." |
| 14 | realty.com | realty.com/office/317348/van_noy_real_estate | 🟠 Verify | Confirm NAP. |
| 15 | **Yelp** | yelp.com/biz/the-van-noy-group-leawood | 🔴 Fix | Wrong name ("The Van Noy Group") AND wrong address (5000 W 135th St). |
| 16 | Facebook | facebook.com/vannoyrealestate/ | ✅ Keep | Sync NAP + link tree. |
| 17 | Instagram | instagram.com/vannoyre/ | ✅ Keep | 617 posts, good. Bio needs link + keywords. |
| 18 | YouTube (handle) | youtube.com/@vannoyre | ✅ Keep | Underused for AI — see §5. |
| 19 | YouTube (legacy channel ID) | UC0jQiHoFvBy9iSVda39f4Gg | 🟠 Confirm | Same channel? Verify one canonical handle. |
| 20 | RealTrends (earned) | realtrends.com — "launches brokerage" | ✅ Authority | Cite/link it. |
| 21 | KC Real Producers (earned) | realproducersmag.com | ✅ Authority | Cite/link it. |
| 22 | Real Estate Radio Show | (host credit, multiple mentions) | 🟠 Underexploited | Strong authority signal — needs a home page + schema. |

**Likely MISSING / unclaimed (high-value gaps):**
- 🔴 **Google Business Profile** — not confirmed claimed. This is the #1 source for local AI answers and Maps. If unclaimed, claim today.
- 🔴 **Realtor.com agent profile** — no profile surfaced. Realtor.com is heavily scraped by AI engines.
- 🔴 **Wikidata entity** — no structured knowledge-graph node. This is how you become a "known entity" to AI.
- 🔴 **DVN Coaching** — essentially invisible. Externally mislabeled "Van Noy Coaching Method." No dedicated, discoverable presence.

---

## 3. The consistency audit — what conflicts, and the fix

### Canonical record (lock this — confirm the 3 flagged fields and everything cascades)

| Field | CANONICAL VALUE | Notes |
|-------|-----------------|-------|
| Name (personal) | **David Van Noy Jr.** | Always "Jr." Always "Van Noy" (two words). |
| Business name | **Van Noy Real Estate** | Retire "The Van Noy Group" / "Van Noy Group" everywhere. |
| Title | **Broker/Owner, Van Noy Real Estate** | |
| Coaching brand | **DVN Coaching** | Stop "Van Noy Coaching Method" externally. Pick one name and use it. |
| Experience | **23+ years (since 2003)** | Kills the 18/20/22 conflict. 2026 − 2003 = 23. |
| Career volume | **$500M+ closed** | Consistent — keep. |
| Homes sold | **1,450+ homes** | Upgrade from "1,000+." It's your real number and it's stronger. |
| Market | **Kansas City metro — Johnson County KS & Jackson County MO** | |
| Email (public) | **info@vannoyre.com** (general) / **david@vannoyre.com** (direct) | Pick which is public-facing and use it consistently. |
| Office phone | **⚠️ CONFIRM** — (913) 349-7580 or (913) 393-9469? | Two are live. Tell me the right one. |
| Office address | **⚠️ CONFIRM** — 8700 State Line Rd, Ste 180, Leawood, KS 66206 (Yelp shows 5000 W 135th St). | Which is current? |
| Cell | **⚠️ CONFIRM** — 816 number on LinkedIn. | Keep public or not? |

### Conflicts found in the wild

| Conflict | Where | Correct it to |
|----------|-------|---------------|
| Years of experience: 18 / 20 / 22 / 23+ | Zillow, Homes.com, FastExpert, vannoyre.com | **23+ (since 2003)** |
| Homes sold: "1,000+" vs internal "1,450+" | All public profiles | **1,450+** |
| Business name: "Van Noy Group" vs "Van Noy Real Estate" | Yelp, Agent Pronto, Zillow-B | **Van Noy Real Estate** |
| "Featured agent at ReeceNichols" (present tense) | kchomelistings.com | Remove — you own VNRE now |
| Address: State Line Rd vs 5000 W 135th St | Yelp vs others | **One confirmed address** |
| Phone: 3 different numbers | LinkedIn, kchomelistings, others | **One office + one cell, fixed** |
| Email: info@ vs david@ | various | **One public email** |
| Coaching: "Van Noy Coaching Method" vs "DVN Coaching" | RealTrends, internal | **One coaching brand name** |

**Rule going forward:** the canonical record above is copy-pasted *identically* into every profile. Same bio, same NAP, same numbers, same headshot. AI rewards repetition of identical facts across independent sources — that's how it gains confidence to state them.

---

## 4. AI discoverability (GEO/AEO) audit — the new frontier

This is the part most agents have never thought about. Traditional SEO gets you ranked in blue links. **Generative Engine Optimization (GEO)** / **Answer Engine Optimization (AEO)** gets you *cited inside the AI's answer.* Different game, different tactics.

**How AI decides who you are:**
1. **Structured data (Schema.org)** on your site — `RealEstateAgent`, `Person`, `LocalBusiness`, `Organization`, `FAQPage`. This is machine-readable fact. Most agent sites have none.
2. **Knowledge-graph entities** — Wikidata, Google Knowledge Panel. These make you a "known entity" the AI trusts.
3. **Consistent NAP across many independent sources** — the consistency fix in §3 directly feeds this.
4. **Q&A-formatted content** that mirrors how people ask AI ("Who is the best listing agent in Leawood KS?" "How do I sell my house in Overland Park?").
5. **Citable third-party authority** — RealTrends, Real Producers, your radio show, reviews.

**Your current GEO/AEO scorecard:**

| Signal | Status | Priority |
|--------|--------|----------|
| Schema.org markup on vannoyre.com | ❌ None detected | 🔴 P0 |
| `RealEstateAgent` / `Person` schema on bio page | ❌ | 🔴 P0 |
| `FAQPage` schema on key pages | ❌ | 🔴 P0 |
| Google Business Profile claimed & complete | ⚠️ Unconfirmed | 🔴 P0 |
| Wikidata entity | ❌ | 🟠 P1 |
| Consistent NAP across sources | ❌ Conflicts everywhere | 🔴 P0 |
| Q&A / "answer-shaped" content | ❌ Marketing-voice pages only | 🟠 P1 |
| YouTube transcripts (AI reads these) | ⚠️ Not optimized | 🟠 P1 |
| llms.txt file on domain | ❌ | 🟢 P2 (emerging) |
| Author/expert bylines on content | ⚠️ Partial | 🟢 P2 |

**The single highest-leverage move:** add Schema.org `RealEstateAgent` + `Person` + `FAQPage` JSON-LD to vannoyre.com. It's invisible to humans, free, and it hands AI engines a clean, authoritative fact sheet about you. (Draft block is in `Schema-JSON-LD-Block.md`.)

---

## 5. The ambitious exposure plan

### Phase 0 — Stop the bleeding (this week, free)
1. **Claim/verify Google Business Profile.** Complete every field, set the canonical NAP, add categories (Real estate agency, Real estate consultant), post weekly.
2. **Kill the stale assets:** redirect `kchomelistings.com`, `thevannoygroup.com`, and `vannoy-homes.kw.com` → `vannoyre.com` (301 redirects). Remove "ReeceNichols" present-tense language.
3. **Merge the duplicate Zillow profiles** into one (Zillow support can merge — consolidates your reviews).
4. **Rename "Van Noy Group" → "Van Noy Real Estate"** on Yelp, Agent Pronto, Zillow. Fix the Yelp address.
5. **Standardize NAP + bio + headshot** across all 22 profiles using the canonical record.

### Phase 1 — Make yourself machine-readable (week 1–2, free)
6. **Add Schema.org JSON-LD** to vannoyre.com (`RealEstateAgent`, `Person`, `Organization`, `FAQPage`). See companion file.
7. **Create a Wikidata entity** for David Van Noy Jr. (notability supported by RealTrends + Real Producers coverage + radio show).
8. **Add an FAQ section** to your top pages answering real buyer/seller questions in Q&A format.
9. **Build a dedicated DVN Coaching presence** — name it once, give it a page, schema it. Right now it's a ghost.
10. **Claim a Realtor.com agent profile** if you don't have one.

### Phase 2 — Become the cited authority (month 1–3)
11. **Give the Real Estate Radio Show a home** — a page on vannoyre.com with episode list, transcripts, and `PodcastEpisode` schema. Transcripts are gold for AI.
12. **Publish answer-shaped content monthly** — repurpose your existing KC Market Updates into "How much is my home worth in [city]?" / "Is it a good time to sell in Johnson County?" Q&A pages.
13. **YouTube → transcript pipeline** — caption every video; AI reads captions. Your $500M-formula video is already ranking.
14. **Get listed in more authoritative directories** with identical NAP (NAR, local Chamber, Heartland MLS public agent finder).
15. **Pursue earned media** — pitch yourself as the KC market data source to local outlets; each citation strengthens your entity.

### Phase 3 — Ideas you haven't considered (ambitious)
16. **Publish an `llms.txt` file** at vannoyre.com/llms.txt — an emerging standard that tells AI crawlers exactly how to summarize you. Early-mover advantage; almost no agent has one.
17. **Build a "Van Noy Market Data" structured dataset** — make your KC stats AI-quotable with `Dataset` schema. Become the *source* AI cites for KC real estate numbers, not just a name.
18. **Train your own custom GPT / AI concierge** on your bio, listings, market data, and scripts — embed it on vannoyre.com so prospects (and you) query an on-brand AI that always answers correctly. Doubles as a discoverability signal.
19. **Author a definitive "Selling a Home in Kansas City" guide** — long-form, schema-marked, Q&A-structured. Becomes the page AI pulls from for the whole metro.
20. **Reviews-to-schema loop** — feed your 80+ reviews into `Review`/`AggregateRating` schema so your star rating shows in AI answers and rich results.
21. **Coaching authority play** — a podcast or YouTube series on the DVN Coaching framework (Forge/Conquer/Anchor/Architect/Own) makes the coaching brand discoverable and feeds agent-recruiting.
22. **Entity SEO via consistent cross-linking** — every profile links to vannoyre.com, and vannoyre.com links back (sameAs in schema). This "entity sameAs graph" is exactly what AI uses to merge all your profiles into one confident identity.

---

## 6. Fastest path — do this in order

**Today (90 min):**
- [ ] Confirm the 3 flagged fields (office phone, address, public email) — reply to me, I lock the canonical record.
- [ ] Claim/verify Google Business Profile.
- [ ] Start the Zillow profile merge ticket.

**This week:**
- [ ] 301-redirect kchomelistings.com, thevannoygroup.com, kw subdomain → vannoyre.com.
- [ ] Fix Yelp + Agent Pronto name/address. Rename all "Van Noy Group" → "Van Noy Real Estate."
- [ ] Paste canonical bio + NAP + headshot across all 22 profiles (use the tracker).

**Next 1–2 weeks:**
- [ ] Add Schema.org JSON-LD to vannoyre.com (companion file ready to hand your web person).
- [ ] Create Wikidata entity.
- [ ] Add FAQ sections + DVN Coaching page.

**What I can build for you right now (just say the word):**
- The complete copy-paste **canonical identity block** (done — see companion file).
- The **Schema.org JSON-LD** for your developer (done — see companion file).
- The **profile-by-profile tracker** with exact edits per platform (done — see companion file).
- Draft **FAQ content** in your voice for the top 5 pages.
- A draft **Wikidata entity** and `llms.txt`.
- Outreach copy to **merge the Zillow duplicates** and fix Yelp.

---

## Sources
- [RealTrends — Kansas City's David Van Noy launches brokerage](https://www.realtrends.com/blog/2023/01/06/kansas-citys-david-van-noy-launches-brokerage/)
- [KC Real Producers — David Van Noy](https://www.realproducersmag.com/locations/kansas-city-real-producers-c8b7/articles/-8af942/)
- [Van Noy Real Estate — bio](https://vannoyre.com/david-van-noy/) · [About](https://vannoyre.com/about/) · [Home](https://vannoyre.com/)
- [LinkedIn — personal](https://www.linkedin.com/in/davidvannoyjr) · [company](https://www.linkedin.com/company/vannoyre)
- [Zillow — VanNoyRE](https://www.zillow.com/profile/VanNoyRE) · [Zillow — VanNoyGroup (duplicate)](https://www.zillow.com/profile/VanNoyGroup)
- [Homes.com](https://www.homes.com/real-estate-agents/david-van-noy-jr/m52eksj/) · [FastExpert](https://www.fastexpert.com/agents/david-van-noy-23523/) · [Agent Pronto](https://agentpronto.com/agents/david-van-noy-83176) · [realty.com](https://www.realty.com/office/317348/van_noy_real_estate)
- [Yelp — "The Van Noy Group" (wrong name/address)](https://www.yelp.com/biz/the-van-noy-group-leawood)
- [Facebook](https://www.facebook.com/vannoyrealestate/) · [Instagram](https://www.instagram.com/vannoyre/) · [YouTube](https://www.youtube.com/@vannoyre)
- [kchomelistings.com (stale ReeceNichols-era site)](https://www.kchomelistings.com/about/) · [thevannoygroup.com](https://www.thevannoygroup.com/) · [vannoy-homes.kw.com](https://vannoy-homes.kw.com/)
- [YouTube — From $500M Sold: David Van Noy's Formula](https://www.youtube.com/watch?v=dwbje3tEPcI)
