# Retention Engine — Workflow Audit, Data to Add, & Connector Map

Everything here is about one thing: turning your existing data + connectors into the
**50% repeat-and-referral business** the VNRE plan names as a key thrust, plus the
**Vendor MSA income** line ($25k) — without you hand-combing the CRM. This is the
Stage 08 module of aiDrVN; prove it inside VNRE, then it's sellable.

---

## 1. Workflow audit — end to end

| Step | State | Tighten |
|---|---|---|
| **Pull** | ✅ `fub_pull.py` (people + won deals + bulk comms + property-view events + custom fields) | Confirm your segment labels + custom-field names (PULL_SPEC §3). |
| **Enrich** | ⚠️ partial | Equity uses a flat 5% appreciation — upgrade to per-ZIP / real AVM (§4). CLV is a custom field — auto-fill it from QuickBooks (§3). |
| **Score** | ✅ deterministic, tunable, CLV-weighted, 30-day suppression | Add a hard "do-not-contact / opt-out" guard sourced from FUB tags (§2). |
| **Review** | ✅ Claude spot-checks drafts | Pull the last 1–2 comms per top contact so drafts reference the real prior conversation. |
| **Deliver** | ⚠️ brief only today | Auto-create Gmail drafts + (for equity) a Canva one-pager, and log a planned-touch note to FUB (§3). |
| **Close the loop** | ❌ missing | Write the touch back to FUB (note + "Last Touch" field) and track responses → referral attribution. This is what makes "50% repeat/referral" *measurable*, not just aspirational. |

**Biggest gap:** loop-closure. Right now the engine surfaces and drafts; it doesn't yet
record what was sent or whether it converted. Add the write-back (§3, FUB) and you get a
real repeat/referral funnel you can report on at the weekly leadership meeting.

---

## 2. Data points to ADD in Follow Up Boss (custom fields / tags)

Each row: the field, the moment it powers, and the VNRE goal it serves. Most are one-time
admin to add, then maintained at closing.

| Add in FUB | Powers | Serves goal |
|---|---|---|
| **Closing Date** (if not on the deal) | anniversary, tenure, move-window | repeat business |
| **Sale Price** (if not on the deal) | equity update | listing leads |
| **Loan Balance + Loan Type + Rate + Lender** | *true* equity (not estimated), refi touch, lender MSA | MSA income, listings |
| **Original Mortgage Rate** | refi touch | MSA income |
| **Birthday / Anniversary (personal)** | birthday + life-event touches | referral, retention |
| **Preferred Channel** (call/text/email) | every draft → right medium | conversion |
| **Lifetime Value** (auto from QBO) | CLV scoring → whales first | profit / 50% margin |
| **Referral Source** + **Referrals Given (count/date)** | who refers; when to re-ask | 50% referral thrust |
| **NPS Score** (you already run NPS, target 9.2) | only ask referrals from promoters | referral quality |
| **Do-Not-Contact / Opt-Out tag** | hard suppression guard | compliance, trust |
| **Property Type / Subdivision / ZIP** | per-ZIP appreciation, sharper comps | equity accuracy |
| **Home Anniversary Year-Bought** | milestone weighting | retention |

> Quick win: **NPS + Referrals-Given** are the two highest-leverage adds — they turn the
> Referral Ask from a blind blast into "ask my 9–10 promoters who haven't referred in 12 mo."

---

## 3. Your other connectors — how each plugs into this workflow

You're paying for these already; here's where they earn their keep in retention.

- **QuickBooks (connected):** sum each past client's commission across closings → write
  **Lifetime Value** back to FUB. Whales rise to the top of every brief automatically. Also
  feeds the Stage 07 CEO dashboard.
- **Gmail (connected):** (a) actual last-email date as a `lastContactDate` source; (b)
  auto-create the approved touches as **drafts** to each contact — one-tap send, nothing
  auto-fires.
- **Google Calendar (connected):** drop approved call-touches onto your calendar as 5-min
  tasks; read upcoming closings to pre-stage the anniversary list 12 months out.
- **Canva (connected):** for every **Equity Update**, auto-generate a branded "Your Home
  Equity Update — {address}" one-pager / postcard with the estimated value + gain. Equity
  touches convert far better with a visual than a bare text.
- **Granola (connected):** mine past listing/closing call transcripts for life events
  (baby, job change, "might downsize in a couple years") → schedule the right future touch
  and personalize the draft.
- **Google Drive (connected):** the brief + state live in the `Follow Up Boss Pipeline`
  folder; the sold-history JSON feeds equity/tenure.

**Highest-ROI connector add:** the **QuickBooks → FUB Lifetime Value** sync. It makes every
retention decision profit-weighted and directly serves the 50% margin target. I can build
that as its own small skill next.

---

## 4. Signals to add later (sharper, more work)

- **Real AVM instead of flat 5%:** pull an automated valuation (or your Cloud CMA / Realist
  feed) per address so equity numbers are defensible to the dollar.
- **Per-ZIP appreciation table:** cheap middle ground — replace the single `APPRECIATION_RATE`
  with a ZIP→rate lookup from Heartland MLS YoY data (you already pull this for market updates).
- **Rate-watch automation:** when the market 30-yr drops below a client's locked rate by your
  delta, auto-fire the refi list — turns Vendor MSA income into a standing engine.
- **Listing-inventory cross-ref:** when a move-window or active-move client's neighborhood
  gets a new comparable sale, trigger a "your neighbor just sold for $X" touch.
- **Equity-to-listing scoring:** combine tenure + equity + property-view into a single
  "likely to list in 12 mo" score and feed the hottest into the PLP pipeline automatically.

---

## 5. How this ladders to your numbers

- **75 listings / 120 listing appts:** active-move + equity + move-window touches feed
  warm seller conversations straight into the PLP pipeline.
- **50% repeat & referral thrust:** referral asks (NPS-gated) + birthdays + re-engage keep
  the 3,000 database in constant light rotation, with loop-closure making it measurable.
- **$25k Vendor MSA income:** the refi touch routes past clients to your lender partner.
- **50% net margin:** CLV-weighting spends your attention on the most profitable relationships.
