# Scheduled Task — meta-review

- **Name:** `meta-review`
- **Schedule:** Weekly — **Sunday 6:00 PM** (after the week's runs, before the new week)
- **Skill:** none — Claude reads the STATE ledgers directly and renders the rollup
- **Output:** `Follow Up Boss Pipeline/_state/Weekly Ops Review YYYY-MM-DD.md`
- **Prereqs:** the other tasks have run at least once (so `_state/*.STATE.md` exist)

The self-monitor. It reads every task's run ledger and answers the three questions a
fleet owner actually has: **did everything fire, what did it cost, and what's broken.**
It closes the governance boxes that can't be pre-filled — tokens/iteration and worst-case
cost stop being estimates once this rolls up the real ledgers.

## Trigger prompt (paste verbatim)

```
Run the weekly ops review.

1. Read every ledger in "Follow Up Boss Pipeline/_state/*.STATE.md" (active-hunter,
   database-coi, ceo-dashboard, clv-sync, plus daily-lead-attention / plp-folder-build
   if present). Each is a run log with timestamp, output, counts, tokens in/out, cost,
   and anomalies.
2. Render "Follow Up Boss Pipeline/_state/Weekly Ops Review <today>.md" with:
   - FIRED vs MISSED: every task that should have run this week, and whether it did
     (gap = a ledger with no run this week → flag it RED).
   - COST: tokens in/out and est. cost per task and the weekly total; compare to the
     GOVERNANCE §9 worst-case ceiling; call out the median tokens/iteration per task
     (this replaces the estimates — update GOVERNANCE §9 when it drifts >20%).
   - AUTONOMY: each task's level; flag any L3-eligible task still hand-approving cleanly
     (candidate to promote) and any level raised without a sign-off note.
   - ANOMALIES: every non-empty anomaly line, the retry/ceiling hits, empty-pull silent
     archives, and anyone high-value held back.
   - OPEN BOXES: which tasks still owe their 3–5 tokens/iteration logs.
3. Post a SHORT chat summary ONLY IF something needs DVN: a missed run, cost over the
   ceiling, an anomaly, or a promotion candidate. A clean week → write the file, say one
   green line, stop. Don't narrate a healthy week.
```

## On failure
- No `_state/` ledgers yet → say so, point to STATE.template.md; nothing to review.
- A ledger unparseable → note which one and keep going; don't fail the whole review.

## Governance (agent-ops — see [GOVERNANCE.md](GOVERNANCE.md))
- **Trigger:** cron — weekly Sunday 6:00 PM. Manual: "run the ops review".
- **STATE:** reads all `_state/*.STATE.md` (this is the read-first task); writes its own
  `_state/meta-review.STATE.md` line last (review date, weekly cost, anomaly count).
- **Writer ≠ checker — hard gate: `Read-Only Audit Gate`.** It reports on the other tasks;
  it never edits their ledgers, drafts, or commits. Purely observational.
- **Stop condition (machine-checkable):** review `.md` written **AND ≥1 ledger parsed**.
- **Iteration ceiling:** 1 pass/fire · retry ≤3 · 20 tool-calls hard cap.
- **Autonomy: L1 (Propose).** Read-only rollup.
- **Found-something → inbox** (missed run / over-cost / anomaly / promotion candidate posts
  to chat). **Found-nothing → silent** (write the file, one green line, no narration).
- **Shell allowlist:** none required (markdown read + render). No network.
- **Parallel:** N/A — runs alone, after the week.
