# Project — Niched Command Center

**Purpose (VNRE):** One screen that answers the only question that matters at
5 AM — *what do I do today to hit the plan.* Not a metrics wall. A decision
surface for the single workflow DVN runs daily: the prospecting-to-listing engine.

**Status:** Framework built 2026-06-23. Branded single-pane shell with labeled
data slots in `command-center/`. Goes live by wiring the slots to the skills that
already produce the data.

---

## The niche (one problem, on purpose)
The source says: *solve a specific workflow problem you face daily — no external
audience needed.* DVN's daily problem is **the morning go/no-go**: who to call,
what's hot, am I on pace, what's stalling. He has the data scattered across five
skill outputs. The command center puts it on one screen so the morning block
starts with zero assembly.

**Explicitly out of scope:** company financials (that's `vnre-ceo-dashboard`),
asset tracking (that's `vannoy_dashboard.html`), transactions, coaching. One
screen, one job. Niche it or it becomes another dashboard nobody opens.

## What's on the screen (four panels)
1. **Today's Hunt** — the ranked call list (`vnre-active-hunter`): top targets,
   segment, the one line of why-now.
2. **Needs Attention** — leads scored High/Med/Low with stalls/regressions
   (`daily-lead-attention`).
3. **Pace vs Plan** — appointments and listings this week/month against the
   75-sides/yr math (50 contacts → 1 appt → ~70% → listing).
4. **Pipeline** — live `LA:` appointments feeding PLP (`vnre-book-appointment`).

## Inputs
- JSON outputs from the skills above (the command center reads, never computes —
  the scoring stays in the deterministic Python where it belongs).

## Outputs
- A rendered screen (open `command-center/index.html`), refreshed each morning.

## Process
1. Morning tasks run (active-hunter 5:15, lead brief 5:00) and drop their JSON.
2. Command center loads the JSON into the four panels.
3. DVN reads one screen, starts the prospecting block. No assembly.

## Decisions (do not relitigate)
- **Read-only.** The center displays; it never scores or sends. All logic stays in
  the skills.
- **Four panels, hard cap.** A fifth panel means a second screen and a new niche —
  don't add, fork.
- **VNRE brand.** Red `#C8102E` accent only; charcoal/gray base; Roboto Condensed
  headers. Matches the offer-summary/HTML-branding palette.
- **Built for the 5 AM read**, not a client. No polish that doesn't speed the
  decision.

## Connects to
- Upstream: `vnre-active-hunter`, `daily-lead-attention`, `vnre-book-appointment`,
  the numbers math.
- Downstream: the prospecting block itself — this is the on-ramp to it.
