# Execution Checklist — do this when you're back at a desk

> Sequenced for impact and speed. Each step says how long, which file to use, and where to
> log it. Everything content-side is already written — this is paste-and-send.
> Log each completion in `Audit Log.md` §3 (check the task) and §4 (change log).
> **NOTE:** The Google audit (2026-06-13) found heavy account sprawl across TWO logins
> (david@vannoyre.com + david@thevannoygroup.com). Do that cleanup FIRST — section below.

---

## DAY 0 — GOOGLE ACCOUNT CLEANUP (found 2026-06-13, do first)

Full map + IDs in `Audit Log.md` §5b. Rules: never click "New account," never complete a signup, don't close accounts with billing history (leave dormant).

**G1. Reclaim the Business Profile — task #1** ⭐ highest value
- Log in as **david@thevannoygroup.com** → go to business.google.com.
- If it owns the "Van Noy Real Estate" profile (4.8★/65), add **david@vannoyre.com as Owner**, then cancel the slow Jun-16 transfer request. If not, let the transfer request ride to Jun 16.
- Once you control it: paste GBP fields from `Profile Copy Pack.md`, set categories, post.

**G2. Send the PPC vendor brief — task #4b**
- Vendor runs Google Ads "RE-DavidVanNoy-KC-3k" (~$1k+/mo, ~$8.6k YTD). Send `Vendor Brief - PPC Account.md`.
- Demands: cost-per-listing ROI, rebrand VNG→Van Noy Real Estate, canonical NAP, a date to repoint landing pages off kchomelistings.com, fix the 34/34 disapproved ads, add david@vannoyre.com as admin.

**G3. Local Services Ads cleanup — task #5b**
- Account picker (david@vannoyre.com login): "Unknown Business Name" = blank signup → **abandon, don't complete**.
- "Van Noy Real Estate" LSA → **pause the ad**, fix name/address/website/bio to canonical, **leave off** (buyer-lead product, off-strategy). Steps in `Outreach & Fix Scripts.md` §6.

**G4. Google Ads housekeeping — task #5c**
- Acct 1357676347: $88.40 ✅ paid 2026-06-13. Leave dormant.
- Acct 706968402: empty since 2022. Leave dormant.
- Review the "Protect your account from unauthorized activity" security alerts; verify payment methods on file are yours.

**⛔ DO NOT redirect kchomelistings.com or thevannoygroup.com yet** — the vendor's live ads land there (tasks #3/#4 are on HOLD until the vendor confirms a repoint date via G2).

---

## DAY 1 — ~90 minutes, biggest impact

**1. Google Business Profile — see G1 above (task #1)**
- It already EXISTS (4.8★/65, correct address) but is owned by another account — this is a *reclaim*, not a new claim. Do G1.

**2. Open the Zillow merge ticket (10 min) — task #2**
- Send the message in `Outreach & Fix Scripts.md` §1 to Zillow Agent Support.
- *Why: consolidates your split reviews onto one profile.*

**3. Fix Yelp (15 min) — task #6**
- Claim at biz.yelp.com, then apply `Outreach & Fix Scripts.md` §2 (name + address).

**4. Forward the developer brief (10 min) — tasks #5, #8**
- Send `Outreach & Fix Scripts.md` §5 to whoever runs vannoyre.com.
- Attach `Schema-JSON-LD-Block.md` (schema + llms.txt) and `FAQ Content.md`.
- Fill the schema placeholders for them: headshot URL, logo URL. Review rating/count already set to Google 4.8★/65.
- ⚠️ **Tell the dev to HOLD the kchomelistings.com / thevannoygroup.com redirects** (tasks #3/#4) until the PPC vendor repoints (see G2). The rest (kw.com redirect, ReeceNichols cleanup, schema, llms.txt, FAQ) is good to go.

**5. Update LinkedIn personal headline (10 min) — task #10**
- Replace headline + About with `Profile Copy Pack.md` → LinkedIn section.
- Remove the raw cell number from the headline.

---

## WEEK 1 — sync every profile (~2 hours total, batchable)

Use `Profile Copy Pack.md` for each. Same bio, NAP, numbers, headshot everywhere.

- [ ] LinkedIn company (#11)
- [ ] Zillow kept profile (#12)
- [ ] Homes.com — claim + correct (#13) — `Outreach & Fix Scripts.md` §4
- [ ] FastExpert agent + company (#14)
- [ ] Agent Pronto rename (#7) — `Outreach & Fix Scripts.md` §3
- [ ] realty.com verify (#15)
- [ ] Facebook (#16)
- [ ] Instagram bio + link (#17)
- [ ] YouTube About + confirm single handle (#18, #19)
- [ ] Realtor.com — claim/create (#19/Realtor) — `Profile Copy Pack.md` Realtor section
- [ ] Pick & upload ONE canonical headshot across all of the above

---

## WEEK 2 — build the AI assets

- [ ] **Schema + llms.txt live** on vannoyre.com (dev) — validate at validator.schema.org + Google Rich Results test (#8, #24)
- [ ] **FAQ sections published** on About/Sellers/Buyers/Coaching pages (#21) — `FAQ Content.md`
- [ ] **DVN Coaching page** published (#22) — `DVN Coaching Page.md` (decide: /coaching vs dvncoaching.com)
- [ ] **Create Wikidata entity** (#20) — `Wikidata Entity Draft.md`; add the resulting URL to schema sameAs
- [ ] **Radio Show page** stub (#23) — `Radio Show Page.md`; send me the episode source to populate

---

## MONTH 1+ — authority & maintenance

- [ ] Caption/transcribe all YouTube videos (#25)
- [ ] Reviews → AggregateRating schema once review counts confirmed (#26)
- [ ] Reviews engine: ask every closing for a Google + Zillow review (feeds ratings AI shows)
- [ ] Repurpose each monthly KC Market Update into a Q&A FAQ page ("Is it a good time to sell in [city]?")
- [ ] **Run the verification test** (`Audit Log.md` §6): ask ChatGPT/Perplexity/Gemini/Google "Who is David Van Noy real estate Kansas City?" — log results, fix any drift.

---

## What's blocking nothing (decide when convenient)
- **Cell (816):** keep public anywhere, or office-only? (default: office-only)
- **Coaching home:** vannoyre.com/coaching vs dvncoaching.com? (default: /coaching)
- **Headshot:** confirm the one file to standardize on.
- **Radio episode source:** where the archive/feed lives, so I can build the episode entries.
- **PPC vendor (after they reply):** is the ~$1k+/mo producing listings? If cost-per-listing is bad, cut or rework — decide once they send numbers.

Answer these in chat and I'll finalize the affected files.

---

## Session log — Google sprawl found 2026-06-13 (status)
- ✅ $88.40 LSA balance paid · ✅ confirmed empty/dormant accounts (706968402, 1357676347) · ✅ vendor PPC decision (leave running, get ROI)
- ◐ Open: reclaim GBP (G1) · send vendor brief (G2) · pause+fix LSA (G3) · security-alert checks (G4) · HOLD legacy-domain redirects
- Full detail: `Audit Log.md` §3 (tasks 1, 4b, 5b, 5c), §5b (Google entity map), §4 (change log).
