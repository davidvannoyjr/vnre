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
| 3 | 301-redirect kchomelistings.com → vannoyre.com | Dev | ⛔ HOLD | | ⚠️ DEPENDENCY: PPC vendor's LIVE ads (acct RE-DavidVanNoy-KC-3k) point here ("KCHL"). Do NOT redirect until vendor repoints landing pages — would break paid ads. Coordinate via vendor brief first. |
| 4 | 301-redirect thevannoygroup.com → vannoyre.com | Dev | ⛔ HOLD | | ⚠️ May be a vendor ad landing domain too. Confirm with vendor before redirecting. |
| 4b | Send canonical brief to PPC vendor | DVN | ☐ | | Vendor runs RE-DavidVanNoy-KC-3k ($34/day, listing-lead gen). Ask: rebrand VNG→Van Noy Real Estate, fix 34/34 disapprovals, plan repoint to vannoyre.com, confirm which legacy domains they need live. See `Vendor Brief - PPC Account.md`. |
| 5 | Kill/redirect vannoy-homes.kw.com | DVN/KW | ☐ | | Off-brand KW page |
| 5b | Google Local Services Ads (LSA) — consolidate to ≤1, pause + fix | DVN | ◐ | | 2026-06-13 FOUND **TWO** LSA accounts under one login: (1) "Unknown Business Name" 723-297-1201 — incomplete/abandoned signup → ABANDON (don't complete); (2) "Van Noy Real Estate" Leawood 947-603-4678 = the legacy "Van Noy Real Estate Group" profile w/ wrong NAP (5000 W 135th St/66224, thevannoygroup.com) → PAUSE + fix to canonical + leave off. Phone numbers shown are Google LSA proxy/tracking numbers, not real NAP. Don't create new accounts. End state: ≤1 LSA, paused & correct. |
| 5c | Google Ads account (1357676347) — settle balance, secure, leave dormant | DVN | ◐ | | 0 campaigns/$0 day (not spending). ✅ 2026-06-13 $88.40 balance PAID (checking …638, acct 9476034678 = the VNRE LSA; processing 3–5 days). REMAINING: review 1 security alert + verify 2 payment methods. Leave dormant — do NOT close. |
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
| 2026-06-13 | Google Local Services Ads | CONFIRMED "Unknown Business Name" = an incomplete/abandoned NEW signup (blank business-details form, never launched → can't bill). Action: abandon it, do NOT complete. Real work is on the "Van Noy Real Estate" (947-603-4678) account. | DVN/Claude | ◐ |
| 2026-06-13 | Google Ads account | Parent Google Ads acct "David Van Noy LSA" (ID 1357676347): 0 campaigns, $0/day — NOT actively spending. $88.40 balance owed (auto-pays Jul 1 / at $500, checking ending 638). 1 security alert + 2 payment methods to verify. 1 conversion tag recording (fine). Action: settle balance, check security alert, verify payment methods, leave dormant (don't close). | DVN/Claude | ◐ |
| 2026-06-13 | Google Ads account | ✅ $88.40 balance PAID (checking …638, acct 9476034678; processing 3–5 days). Balance cleared. | DVN | ✅ |
| 2026-06-13 | Google identity | MAJOR: a SECOND Google login exists — **david@thevannoygroup.com** (legacy domain) — holding 2 MORE Google Ads accounts: "RE-DavidVanNoy-KC-3k" (591-648-8315, likely vendor-managed PPC, "3k"=possible $3k/mo budget) + "Google Ads account" (643-233-9415). PRIORITY: check RE-…-3k for ACTIVE SPEND + linked agency/manager access. ALSO: this login is likely the GBP owner → add david@vannoyre.com as Owner from here (skip the Jun-16 transfer). Endgame: consolidate keepers to vannoyre.com login, retire thevannoygroup.com identity. | DVN/Claude | ◐ |
| 2026-06-13 | Google Ads "RE-DavidVanNoy-KC-3k" | RESOLVED: account is LIVE (~$962/28 days, $34/day, 85 campaigns, listing-lead gen: Home Value/Seller/Get Highest Offer). DVN confirms **vendor-managed & intentional — leave it running**. Branded to legacy VNG/KCHL/kchomelistings.com. 34/34 ads disapproved on "Video\|Seller\|Retargeting". CONSEQUENCE: kchomelistings.com + thevannoygroup.com redirects now BLOCKED until vendor repoints. Action → send vendor canonical brief (task 4b). | DVN | ✅ decision |
| 2026-06-13 | Google Ads "Google Ads account" (706968402 / 643-233-9415) | 2nd account under thevannoygroup.com login: EMPTY — 0 campaigns, "none of your ads are running." Dormant, not spending. Leave dormant, don't close. | DVN/Claude | ✅ |
| 2026-06-13 | — | Wrote `Vendor Brief - PPC Account.md` for DVN to send the PPC vendor (rebrand, canonical NAP, repoint plan, fix disapprovals, add vannoyre.com as admin) | Claude | ✅ |
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

## 5b. Google entity cleanup map (one identity must not become five)

| Entity | State (2026-06-13) | Action |
|--------|--------------------|--------|
| Business Profile (GBP) | Correct NAP, 4.8★/65, owned by another Google account | Regain ownership (claim request pending Jun 16) |
| LSA "Van Noy Real Estate" (947-603-4678) | Legacy profile, wrong NAP (5000 W 135th St, thevannoygroup.com), not live | Pause + fix 4 fields to canonical + leave off |
| LSA "Unknown Business Name" (723-297-1201) | Blank, incomplete signup, never launched | Abandon — do NOT complete |
| Google Ads acct "David Van Noy LSA" (1357676347) | Dormant, 0 campaigns, $88.40 owed | Settle balance, check security alert + payment methods, leave dormant |

> All legacy Google data traces to the same old cluster: **The Van Noy (Real Estate) Group · 5000 W 135th St / 66224 · (913) 393-9469 · thevannoygroup.com**. Every place it lives feeds AI a conflicting identity. Same cluster also lives on Yelp.

### Two Google logins (root cause of the sprawl)
| Login | Holds | Plan |
|-------|-------|------|
| **david@vannoyre.com** (current/canonical) | LSA accts (Van Noy RE + blank), Google Ads acct 1357676347 (dormant, balance paid) | Keep as the home for everything |
| **david@thevannoygroup.com** (legacy) | Google Ads "RE-DavidVanNoy-KC-3k" (591-648-8315) + "Google Ads account" (643-233-9415); likely GBP owner | CHECK RE-…-3k for active spend/agency; use to grant GBP ownership to vannoyre.com; then retire |

> Action order: (1) check RE-DavidVanNoy-KC-3k for live spend — pause if bleeding; (2) from this login, add david@vannoyre.com as GBP Owner; (3) consolidate keepers, retire the thevannoygroup.com identity.

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
