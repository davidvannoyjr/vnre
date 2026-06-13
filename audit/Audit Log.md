# Van Noy Profile Audit — Master Log

**Subject:** David Van Noy Jr. / Van Noy Real Estate / DVN Coaching
**Opened:** 2026-06-13 · **Owner:** DVN · **Status:** 🟡 In progress
**Goal:** One consistent, machine-readable identity across every platform so AI engines (ChatGPT, Gemini, Perplexity, Google AI Overviews, Copilot) return the same correct answer.

**How to use this doc:** This is the living record. When you change a profile, log it in §4 (Change Log) and check it in §3 (Task Ledger). Run the §6 verification monthly. Companion files: `2026-06 Van Noy Profile & AI Discoverability Audit.md` (full audit), `Canonical Identity Block.md` (paste-everywhere identity), `Schema-JSON-LD-Block.md` (developer), `Profile Tracker.md` (per-platform checklist).

---

## 1. Status dashboard

| Phase | Scope | Done | Total | % |
|-------|-------|------|-------|---|
| P0 — Stop the bleeding | Kill duplicates/stale, claim GBP, lock NAP | 0 | 8 | 0% |
| P1 — Sync profiles | Canonical NAP+bio everywhere | 0 | 11 | 0% |
| P2 — New AI assets | Schema, Wikidata, FAQ, llms.txt, coaching | 0 | 7 | 0% |
| **Overall** | | **0** | **26** | **0%** |

> Update the counts as tasks close in §3. The audit itself (research + canonical lock + asset drafts) is complete — the work below is execution.

---

## 2. Locked decisions (do not relitigate)

| Date | Decision | Value |
|------|----------|-------|
| 2026-06-13 | Personal name | David Van Noy Jr. |
| 2026-06-13 | Business name | Van Noy Real Estate (retire "Van Noy Group") |
| 2026-06-13 | Title | Broker/Owner |
| 2026-06-13 | Coaching brand | DVN Coaching (retire "Van Noy Coaching Method") |
| 2026-06-13 | Experience | 23+ years (since 2003) |
| 2026-06-13 | Career volume | $500M+ closed |
| 2026-06-13 | Homes sold | 1,450+ |
| 2026-06-13 | Market | KC metro — Johnson County KS & Jackson County MO |
| 2026-06-13 | **Office phone** | **(913) 349-7580** — confirmed by DVN |
| 2026-06-13 | **Office address** | **8700 State Line Rd, Suite 180, Leawood, KS 66206** — confirmed by DVN |
| 2026-06-13 | **Public email** | **david@vannoyre.com** — confirmed by DVN (info@ = general inbox only) |
| ⏳ OPEN | Cell phone (816) on LinkedIn | Keep public or strip? — awaiting DVN |

---

## 3. Task ledger (every action, tracked)

Legend: ☐ not started · ◐ in progress · ☑ done · ⏭ skipped

### P0 — Stop the bleeding
| # | Task | Owner | Status | Date done | Notes |
|---|------|-------|--------|-----------|-------|
| 1 | Claim/verify Google Business Profile, complete all fields | DVN | ◐ | | 2026-06-13: GBP EXISTS & verified, owned by another Google account. Sent claim request (deadline Jun 16). Address already correct (8700 State Line Rd Ste 180). Shows 4.8★/65 reviews. NEXT: check other Google accounts / ask team before waiting on transfer. |
| 2 | Merge duplicate Zillow profiles (VanNoyGroup → VanNoyRE) | DVN | ☐ | | Open Zillow support ticket |
| 3 | 301-redirect kchomelistings.com → vannoyre.com | Dev | ☐ | | Remove ReeceNichols language |
| 4 | 301-redirect thevannoygroup.com → vannoyre.com | Dev | ☐ | | |
| 5 | Kill/redirect vannoy-homes.kw.com | DVN/KW | ☐ | | Off-brand KW page |
| 5b | Google Local Services Ads (LSA) — consolidate to ≤1, pause + fix | DVN | ◐ | | 2026-06-13 FOUND **TWO** LSA accounts under one login: (1) "Unknown Business Name" 723-297-1201 — likely junk/incomplete → CLOSE; (2) "Van Noy Real Estate" Leawood 947-603-4678 = the legacy "Van Noy Real Estate Group" profile w/ wrong NAP (5000 W 135th St/66224, thevannoygroup.com, $500/wk) → PAUSE + fix to canonical + leave off. Phone numbers shown are Google LSA proxy/tracking numbers, not real NAP. Don't create new accounts. End state: ≤1 LSA, paused & correct. |
| 6 | Fix Yelp — name + address | DVN | ☐ | | → Van Noy Real Estate, 8700 State Line Rd |
| 7 | Rename "Van Noy Group" on Agent Pronto | DVN | ☐ | | |
| 8 | Add Schema.org JSON-LD to vannoyre.com | Dev | ☐ | | Block ready in Schema file |

### P1 — Sync every live profile to canonical record
| # | Task | Owner | Status | Date done | Notes |
|---|------|-------|--------|-----------|-------|
| 9 | vannoyre.com/david-van-noy/ — long bio + numbers + headshot | Dev | ☐ | | |
| 10 | LinkedIn personal — headline + medium bio | DVN | ☐ | | Drop raw-cell headline |
| 11 | LinkedIn company — description + NAP + logo | DVN | ☐ | | |
| 12 | Zillow (kept profile) — bio + numbers + headshot | DVN | ☐ | | |
| 13 | Homes.com — experience + bio + headshot | DVN | ☐ | | |
| 14 | FastExpert (agent + company) — sync bio | DVN | ☐ | | Keep 82 reviews |
| 15 | realty.com — verify/correct NAP | DVN | ☐ | | |
| 16 | Facebook — NAP + bio + headshot + link | DVN | ☐ | | |
| 17 | Instagram — bio + keywords + link | DVN | ☐ | | |
| 18 | YouTube — confirm single handle + About | DVN | ☐ | | @vannoyre canonical |
| 19 | Realtor.com — claim agent profile if missing | DVN | ☐ | | |

### P2 — Build new discoverability assets
| # | Task | Owner | Status | Date done | Notes |
|---|------|-------|--------|-----------|-------|
| 20 | Create Wikidata entity | Claude/DVN | ◐ | | Draft ready (`Wikidata Entity Draft.md`); DVN to submit |
| 21 | Add FAQPage content to top 5 pages | Claude/Dev | ◐ | | Copy drafted (`FAQ Content.md`); Dev to publish + schema |
| 22 | DVN Coaching dedicated page + schema | Claude/Dev | ◐ | | Page copy + schema drafted (`DVN Coaching Page.md`); Dev to publish |
| 23 | Radio Show page + transcripts + schema | Claude/Dev | ◐ | | Page copy + schema drafted (`Radio Show Page.md`); needs episode source |
| 24 | Publish llms.txt at vannoyre.com/llms.txt | Dev | ☐ | | Block ready |
| 25 | Caption all YouTube videos | DVN | ☐ | | AI reads transcripts |
| 26 | Reviews → AggregateRating/Review schema | Dev | ◐ | | Real data confirmed: Google 4.8★/65. Plugged into Schema file. (FastExpert ~82 separate.) |

---

## 4. Change log (append-only — one line per change)

| Date | Platform | What changed | By | Verified |
|------|----------|--------------|----|----------|
| 2026-06-13 | — | Audit opened; full footprint researched; 22 profiles inventoried | Claude | ✅ |
| 2026-06-13 | — | Canonical record locked (phone/address/email confirmed by DVN) | Claude/DVN | ✅ |
| 2026-06-13 | — | Assets drafted: canonical block, JSON-LD schema, llms.txt, profile tracker | Claude | ✅ |
| 2026-06-13 | — | Drafted FAQ content, Wikidata entity, and outreach/fix scripts (Zillow, Yelp, Agent Pronto, Homes.com, dev brief) | Claude | ✅ |
| 2026-06-13 | — | Built Profile Copy Pack (per-platform paste-ready copy), DVN Coaching page, Radio Show page, Execution Checklist, folder README | Claude | ✅ |
| 2026-06-13 | — | Added Review Request Templates and the Market Update → FAQ repurposing SOP | Claude | ✅ |
| 2026-06-13 | Google Business Profile | DVN began claim — GBP already exists/verified under another account; sent ownership request (deadline Jun 16). Address correct. Captured real rating 4.8★/65 → into schema | DVN/Claude | ✅ |
| 2026-06-13 | Google Local Services Ads | FOUND a third Google entity — legacy LSA "The Van Noy Real Estate Group" with all wrong NAP + thevannoygroup.com + $500/wk budget, pending verification. Corrective action: pause, fix to canonical, leave off (buyer-lead product, off-strategy) | DVN/Claude | ◐ |
| 2026-06-13 | Google Local Services Ads | Account picker shows TWO LSA accounts: "Unknown Business Name" (723-297-1201, likely junk → close) + "Van Noy Real Estate" Leawood (947-603-4678, the legacy one → pause/fix/off). Consolidate to ≤1. | DVN/Claude | ◐ |
| | | _next change here…_ | | |

---

## 5. Findings snapshot (baseline — what was wrong on day 1)

- **4+ websites:** vannoyre.com (keep), kchomelistings.com (stale ReeceNichols), thevannoygroup.com (old brand), vannoy-homes.kw.com (off-brand KW).
- **2 duplicate Zillow profiles:** VanNoyRE + VanNoyGroup — splits reviews/authority.
- **"Van Noy Group" legacy brand** live on Yelp, Agent Pronto, Zillow-B.
- **Experience conflict:** 18 / 20 / 22 / 23+ years across sources.
- **Homes sold:** "1,000+" public vs 1,450+ actual.
- **3 phone numbers, 2 addresses, 2 email formats** in circulation.
- **No Schema.org markup** on the site. No Wikidata entity. No FAQ/answer content. No llms.txt.
- **DVN Coaching invisible** and mislabeled.
- **GBP & Realtor.com** unconfirmed/likely unclaimed.

---

## 6. AI-answer verification log (run monthly)

Test each engine with: **"Who is David Van Noy real estate Kansas City?"**
Pass = answer matches canonical record (Van Noy Real Estate, 23+ yrs, $500M+, 1,450+ homes, (913) 349-7580, 8700 State Line Rd, david@vannoyre.com). Log drift.

| Date | ChatGPT | Perplexity | Gemini | Google AI Overview | Notes / drift found |
|------|---------|------------|--------|--------------------|--------------------|
| 2026-06-13 (baseline) | ❌ mixes 18/22 yrs, "1,000+" | ❌ "Van Noy Group" surfaces | ❌ stale ReeceNichols | ❌ conflicting NAP | Pre-fix baseline |
| | | | | | _next check…_ |

---

## 7. Open items / waiting on DVN
- [ ] **Cell phone decision** — keep the 816 number public, or strip from LinkedIn?
- [ ] Headshot file — confirm the one canonical image to use everywhere.
- [ ] Review count/rating for schema AggregateRating (currently ~82 on FastExpert — confirm number to publish).
- [x] ~~Approve Claude to draft: FAQ content, Wikidata entity, Zillow-merge + Yelp-fix outreach copy.~~ Done 2026-06-13 — see `FAQ Content.md`, `Wikidata Entity Draft.md`, `Outreach & Fix Scripts.md`.
