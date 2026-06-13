# Outreach & Fix Scripts — copy, paste, send

> Ready-to-send messages to collapse the duplicate profiles and correct the wrong listings.
> Professional and direct. Replace [brackets] before sending.

---

## 1. Zillow — merge the duplicate profiles

**Problem:** Two profiles split your reviews and ranking — `zillow.com/profile/VanNoyRE` and `zillow.com/profile/VanNoyGroup`.
**Channel:** Zillow Agent Support — agentsupport@zillow.com, or in your Zillow account → Help → "Contact us." Phone: 1-866-688-6911.

**Subject:** Merge duplicate agent profiles — David Van Noy

> I have two Zillow profiles under my name and brokerage, and I need them merged into one so my reviews and sales history are consolidated.
>
> - Keep: https://www.zillow.com/profile/VanNoyRE
> - Merge in / retire: https://www.zillow.com/profile/VanNoyGroup
>
> Correct identity for the surviving profile:
> David Van Noy Jr., Broker/Owner, Van Noy Real Estate
> 8700 State Line Rd, Suite 180, Leawood, KS 66206
> (913) 349-7580 · david@vannoyre.com · vannoyre.com
>
> Please move all reviews and past sales from the VanNoyGroup profile onto the VanNoyRE profile, then deactivate the duplicate. I'm the account owner for both — let me know what verification you need.
>
> Thank you,
> David Van Noy Jr.

---

## 2. Yelp — fix business name and address

**Problem:** Listed as "The Van Noy Group" at 5000 W 135th St (wrong name + wrong address).
**Channel:** Claim the business at biz.yelp.com (verify ownership), then edit Business Information. If you can't edit a field, use "Suggest an edit" on the public listing or contact Yelp support.

**If contacting support / suggesting edit:**

> This listing is mine and the business name and address are both incorrect. Please update:
>
> - Business name: "The Van Noy Group" → **Van Noy Real Estate**
> - Address: 5000 W 135th St → **8700 State Line Rd, Suite 180, Leawood, KS 66206**
> - Phone: **(913) 349-7580**
> - Website: **https://vannoyre.com**
>
> I'm the owner — David Van Noy Jr., Broker/Owner. Let me know what's needed to verify.

---

## 3. Agent Pronto — rename brand

**Problem:** Listed as "David Van Noy & The Van Noy Group."
**Channel:** Agent Pronto agent support / profile contact, or reply to any Agent Pronto referral email.

> Please update my profile. My brokerage is **Van Noy Real Estate** — the "Van Noy Group" name is retired. Correct details:
>
> David Van Noy Jr., Broker/Owner, Van Noy Real Estate
> 8700 State Line Rd, Suite 180, Leawood, KS 66206
> (913) 349-7580 · david@vannoyre.com · vannoyre.com
> Experience: 23+ years · $500M+ closed · 1,450+ homes sold.

---

## 4. Homes.com — claim & correct experience

**Channel:** homes.com agent dashboard (claim profile) or support.

> Claiming my profile and correcting the details:
> David Van Noy Jr., Broker/Owner, Van Noy Real Estate — 23+ years experience, $500M+ closed, 1,450+ homes sold. NAP: 8700 State Line Rd, Suite 180, Leawood, KS 66206 · (913) 349-7580 · david@vannoyre.com.

---

## 5. Web developer — the consolidation + schema brief

**Channel:** email/Slack to whoever manages vannoyre.com.

> Three site tasks, priority order:
>
> 1. **301-redirect** these domains/pages to their best match on vannoyre.com (NOT just the homepage where a deeper match exists):
>    - kchomelistings.com → vannoyre.com
>    - thevannoygroup.com → vannoyre.com
>    - vannoy-homes.kw.com → vannoyre.com (and let's discuss taking it down entirely)
> 2. **Remove** any "ReeceNichols" present-tense language anywhere on our properties.
> 3. **Add Schema.org JSON-LD** to the site head — I'll send the exact blocks (RealEstateAgent, Organization, FAQPage) plus an llms.txt file. Validate at validator.schema.org and the Google Rich Results test before pushing.
>
> Canonical contact to use everywhere:
> David Van Noy Jr. — Broker/Owner, Van Noy Real Estate
> 8700 State Line Rd, Suite 180, Leawood, KS 66206 · (913) 349-7580 · david@vannoyre.com

---

## 6. Google Local Services Ads (LSA / "Google Screened") — pause + correct

**Problem:** A separate legacy LSA account, "The Van Noy Real Estate Group," with all-wrong data and a $500/wk budget, pending verification.
**Channel:** ads.google.com/localservices (the Local Services Ads dashboard) — NOT the same as Google Business Profile.

**Steps (in order):**
1. **Pause first:** top of the Profile & budget screen, toggle the ad **OFF** so budget can't spend.
2. **Decision:** LSA is a buyer-lead product (~$2k/mo at $500/wk). For a listing-focused business this is likely off-strategy — recommendation is to leave it **paused** unless you're deliberately building a buyer-lead channel.
3. **Fix every field to canonical** (even while paused — it feeds Google/AI):
   - Business name: "The Van Noy Real Estate Group" → **Van Noy Real Estate**
   - Address: 5000 W 135th St, 66224 → **8700 State Line Rd, Suite 180, Leawood, KS 66206**
   - Phone: (913) 393-9469 → **(913) 349-7580**
   - Website: thevannoygroup.com → **https://vannoyre.com**
   - Business bio: paste the short bio from `Canonical Identity Block.md`
4. **Do NOT complete Google Screened verification** (license + background check) until data is fixed and you've decided to run LSA.

---

### After each fix
Log it in `Audit Log.md` §4 (Change Log) and check the matching task in §3. Re-verify the listing a week later — some platforms revert.
