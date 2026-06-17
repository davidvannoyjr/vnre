# Scheduled Task — active-hunter

- **Name:** `active-hunter`
- **Schedule:** Daily — **5:15 AM** (ready before the 7:30 AM prospecting block; pairs with the 5:00 lead brief)
- **Skill:** `vnre-active-hunter`
- **Output:** `Follow Up Boss Pipeline/YYYY-MM-DD Call List.md`
- **Prereqs:** `followupboss` MCP connected; `04 Tools/active-hunter-skill/` installed.

## Trigger prompt (paste verbatim)

```
Build today's Active-Hunter call list.

1. Get the prospecting contacts — FSBO, Expired, Aged Lead, Geo-farm, COI, Past
   Client — with id, name, phone, address/city, tags/stage, lastAttemptDate,
   attempts, and any signal, including the DNC/Opt-Out tag so it can be filtered.
   FIRST check for the shared pull "_data/fub-morning-pull-<today>.json" (pulledAt =
   today): if present and fresh, filter the prospecting segments out of it — do not
   re-pull. If absent/stale, self-pull from FUB and save to _data/hunter-pull-<today>.json.
2. Run build_call_list.py --pull that file --out "Follow Up Boss Pipeline/<today>
   Call List.md" --today <today>.
3. Present the list grouped by segment with the script reference per group. Note the
   suppressed counts (DNC/opt-out, dialed <2d, maxed).
4. As I work it: connect -> run vnre-book-appointment; no-answer -> log the attempt
   and draft the next nurture touch (Gmail/text draft, approval-gated). Nothing sends
   automatically. Respect KS/MO calling hours and any opt-out.
```

## On failure
- `fub_*` tools missing → restart Claude / run fix-claude-config.sh (Claude quit).
- Empty pull → report and stop; don't overwrite the prior list with an empty one.

## Governance (agent-ops — see [GOVERNANCE.md](GOVERNANCE.md))
- **Trigger:** cron — daily 5:15 AM (documented above). Manual: "build my call list".
- **STATE:** `<home>/_state/active-hunter.STATE.md` (+ `.state.json`). Read first
  (suppression window, attempts/cap, carried items); write last (counts, tokens, cost).
- **Writer ≠ checker — hard gate: `Suppression Gate`.** `build_call_list.py` enforces
  DNC/opt-out + dialed-<2d + attempt-cap + KS/MO calling-hours in Python, independent of
  the drafting step. No contact surfaces that fails it.
- **Stop condition (machine-checkable):** call-list `.md` written **AND `rows > 0`**.
- **Iteration ceiling:** 1 pass/fire · retry ≤3 (2s/4s/8s) · 20 tool-calls hard cap.
- **Autonomy: L2 (Stage).** Drafts nurture touches; **nothing sends**. DVN approves each.
- **Found-something → inbox** (list + scripts + suppressed counts in chat). **Found-nothing
  → silent archive** (write STATE line only; never overwrite the prior list).
- **Shell allowlist:** `python3 scripts/build_call_list.py …` (+ `--selftest`) only; no
  network from sandbox.
- **Parallel:** N/A — sequential in the cadence. Worktree-isolate only if ever parallelized.
- **Open box:** log tokens/iteration for 3–5 runs into STATE.
