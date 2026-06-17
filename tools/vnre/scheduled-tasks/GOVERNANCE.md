# Scheduled-Task Governance — the agent-ops standard

The rules that keep every standing task cheap, safe, and auditable. This is the
canonical checklist applied to the VNRE suite. **Every task file in this folder
carries a filled-in `## Governance` block; this file is the spec those blocks
implement.** New task = copy the checklist below, fill every box, set autonomy to
1, ship.

These tasks are **single-pass scheduled jobs**, not open-ended agent loops:
MCP pull → deterministic Python → Claude review → staged drafts. So the
"iteration ceiling" and "STATE-as-loop-memory" items apply lightly — they're
circuit breakers and run ledgers, not a swarm controller. Read that lens into
every rule below.

---

## The checklist (canonical — copy into every task)

```
[ ] Trigger defined (cron / hook / manual) and documented
[ ] STATE path set; agent reads first, writes last
[ ] Writer and checker separate; checker has a hard gate (named)
[ ] Stop condition machine-checkable, not "agent says done"
[ ] Max iteration ceiling set (default 20)
[ ] Autonomy level set (start 1–2) and written in the file
[ ] Found-something → inbox; found-nothing → silent archive
[ ] Ran 3–5 iterations manually; tokens/iteration recorded
[ ] Worst-case daily cost calculated
[ ] Shell allowlist set (or no shell access)
[ ] Parallel agents (if any) isolated in worktrees
```

---

## 1. Autonomy ladder (set per task — start low, earn up)

| Level | Name | What it may do | Gate to move up |
|---|---|---|---|
| **L0** | Off / manual | Runs only when DVN triggers it by hand | — |
| **L1** | Propose | Read-only. Produces a brief/draft; DVN runs every downstream action | Output trusted 3–5 runs |
| **L2** | Stage | Creates drafts / dry-runs (Gmail drafts, Canva, dry-run plans). **Nothing sends or writes.** DVN approves each send/commit | 3–5 clean staged runs, 0 bad drafts |
| **L3** | Auto-commit (low-risk) | Writes **idempotent, reversible, low-blast-radius** changes automatically (e.g. one FUB number field). Still logs + inboxes | Validated match/quality threshold + DVN sign-off |
| **L4** | Autonomous send | Sends outbound to clients/leads without a human | **Not used.** Client-facing send is always human-gated (CLAUDE.md §3) |

**Current assignments:** `ceo-dashboard` = **L1** (read-only) · `active-hunter`,
`database-coi`, `clv-sync` = **L2** · `clv-sync` Lifetime-Value writeback = **L3-eligible**
once a few dry-runs are clean. Autonomy is written in each task file and never raised silently.

---

## 2. STATE — read first, write last

Each task keeps a run ledger so it has memory across fires (suppression windows,
carried-forward unmatched items, last output, cost). Two files, same folder as the
deliverables:

- **`<home>/_state/<task>.STATE.md`** — human-readable ledger (scaffold:
  [`STATE.template.md`](STATE.template.md)).
- **`<home>/_state/<task>.state.json`** — machine state for dedupe/suppression.
  (`database-coi` already uses `_data/coi-state.json` for this — keep it; the STATE.md
  is the human wrapper around it.)

**Protocol, every run:**
1. **Read first.** Load the STATE files before pulling anything. Get: last-run
   timestamp, suppression window, carried-forward items, autonomy level, run counter.
2. Do the work.
3. **Write last.** Append this run's line: timestamp, trigger, output path, counts
   (surfaced / suppressed / carried), tokens in/out, est. cost, anomalies, next-run note.

`_state/` and `_data/` stay **gitignored** — real CRM/financial data never enters git.

---

## 3. Writer ≠ Checker, with a named hard gate

The thing that drafts is never the thing that clears it. The checker is a
**deterministic step the writer can't talk its way past.**

| Task | Writer | Checker — **hard gate (named)** |
|---|---|---|
| `active-hunter` | `build_call_list.py` ranking + Claude script attach | **Suppression Gate** — DNC/opt-out + dialed-<2d + attempt-cap + KS/MO calling-hours. Enforced in Python, independent of drafting. No contact surfaces that fails it |
| `database-coi` | `build_coi_brief.py` scoring + Claude personalization | **Defensible-Claim Gate** — 30-day suppression + every equity number must be defensible. No draft leaves staging with an undefendable figure or a suppressed contact |
| `ceo-dashboard` | `build_dashboard.py` renderer | **No-Fabrication Gate** — every number traces to a QBO MCP report saved in `_data/`. Missing/auth-lapsed pull → stop, never infer a number |
| `clv-sync` | `build_clv.py` plan | **Dry-Run/Commit Gate** — `fub_push.py` writes nothing without `--commit`; commit only on DVN approval (L2) or match-confidence ≥ threshold with 0 over-threshold unmatched (L3) |

---

## 4. Stop condition — machine-checkable, never "agent says done"

Single-pass tasks "stop" by producing a valid artifact or exiting silent. The
check is a file/count assertion, not a vibe.

| Task | Done = | Empty/error → |
|---|---|---|
| `active-hunter` | call-list `.md` written **AND** `rows > 0` | Don't overwrite prior list. Silent archive |
| `database-coi` | brief `.md` written **AND** `surfacedCount > 0`, state dedupe applied | Keep prior brief. Silent archive |
| `ceo-dashboard` | dashboard `.md` written **AND** both `pl.json` + `ar.json` parsed (top-level keys present) | Stop, report auth/pull failure. No fabricated numbers |
| `clv-sync` | `clv-plan.json` written **AND** `writeback ≥ 1` | Stop, report. Commit stays gated |

## 5. Max iteration ceiling (circuit breakers)

No unbounded loops. Each fire is **one agent pass**.
- **Retry ceiling = 3** on transient failure (matches the push/fetch backoff: 2s/4s/8s), then stop and report.
- **Tool-call ceiling = 20 per run** as a hard circuit breaker (the checklist default). A run that hits 20 stops and writes an anomaly line to STATE.
- A task never re-triggers itself. The schedule is the only trigger.

## 6. Found-something → inbox · found-nothing → silent archive

- **Found something (≥1 surfaced/actionable):** post the chat summary, land the
  deliverable in the Pipeline folder, stage drafts. This is the "inbox."
- **Found nothing (0 surfaced) or empty pull:** write **only** the STATE ledger
  line and exit. No chat ping, no empty file over a good one, no Gmail noise.
  Silence is the signal that nothing needed DVN.

## 7. Shell allowlist (network is the real lockdown)

The Cowork sandbox has **no outbound network** — `api.followupboss.com` and QBO are
unreachable from shell by design. All live data enters through MCP tools, not curl.
Shell is for the deterministic renderers only.

**Allowlist:**
```
python3 scripts/build_call_list.py …
python3 scripts/build_coi_brief.py …
python3 scripts/build_delivery.py …
python3 scripts/build_dashboard.py …
python3 scripts/build_clv.py …
python3 scripts/fub_push.py …          # dry-run default; --commit is the gated write
python3 scripts/partner_value.py …
python3 scripts/fub_field_setup.py …   # one-time setup
python3 scripts/*.py --selftest        # offline verification (build_coi_brief.py verifies via sample/ fixtures, no --selftest)
mkdir / mv / rm within <home>/_data and <home>/_state only
```
**Denied:** `curl`/`wget`/any network call to FUB or QBO from the sandbox (blocked
anyway — use `fub_pull.py` on a networked Mac or the MCP tools). No `rm` outside
`_data`/`_state`. No writes to `02 Reference/` or repo source from a scheduled run.

## 8. Parallel agents → worktrees

**Currently N/A** — the cadence is collision-checked and sequential (5:00 → 5:15 →
5:45 → 6:00 → 6:30 → 7:00), one task at a time, so they never race on shared
`_data`/`_state`. **If that changes** (e.g. a multi-segment backfill fans out, or
two tasks ever run concurrently), isolate each agent in its own git worktree and a
private `_data/<run-id>/` namespace so they can't clobber each other's pull/state
files. Don't parallelize onto the same `_state` file.

---

## 9. Cost model — tokens/iteration + worst-case day

Single-pass run shape (conservative ceiling per fire):

| | Input tokens | Output tokens |
|---|---|---|
| System + skill + instructions | ~15k | — |
| MCP tool results (pull summaries; raw JSON goes to file, not context) | ~40k | — |
| Renderer output + brief review | ~10k | ~12k |
| **Per-run ceiling** | **~65k in** | **~12k out** |

**Daily fleet (worst case = first Monday of the month, all six fire):**

| Task | Days/wk | In (k) | Out (k) |
|---|---|---|---|
| daily-lead-attention | 7 | 65 | 12 |
| active-hunter | 7 | 65 | 12 |
| plp-folder-build | 7 | 40 | 6 |
| database-coi | 1 (Mon) | 65 | 12 |
| ceo-dashboard | 1 (Mon) | 65 | 12 |
| clv-sync | 1 (1st Mon) | 65 | 12 |

- **Typical weekday:** 3 tasks ≈ **170k in / 30k out**.
- **Worst-case day (1st Monday):** 6 tasks ≈ **365k in / 66k out**.
- **Worst-case month:** ~22 weekdays × ~200k + the Monday spikes ≈ **~5–6M in / ~1M out**.

> **Cost in dollars:** multiply by the current Opus input/output per-token rate
> (confirm the live rate before quoting — do not assume). At the ballpark Opus rate
> the worst-case day lands in the low **single-digit dollars**; the dominant lever is
> **keeping raw FUB/QBO JSON out of context** (write to file, pass by path — already
> the design). Prompt-cache the static skill/system prefix and per-run input drops
> further. **Action:** record real tokens/run in each STATE ledger for 3–5 runs and
> replace these estimates with measured numbers.

---

## 10. Per-task status — every box, every task

| Box | active-hunter | database-coi | ceo-dashboard | clv-sync |
|---|---|---|---|---|
| Trigger documented | ✅ daily 5:15 | ✅ Mon 6:00 | ✅ Mon 6:30 | ✅ 1st Mon 5:45 |
| STATE read-first/write-last | ✅ set | ✅ (+coi-state.json) | ✅ set | ✅ set |
| Writer≠checker + named gate | ✅ Suppression | ✅ Defensible-Claim | ✅ No-Fabrication | ✅ Dry-Run/Commit |
| Stop machine-checkable | ✅ rows>0 | ✅ surfaced>0 | ✅ pulls parsed | ✅ writeback≥1 |
| Iteration ceiling | ✅ 1 pass/3 retry/20 cap | ✅ | ✅ | ✅ |
| Autonomy written | ✅ L2 | ✅ L2 | ✅ L1 | ✅ L2→L3 |
| Found→inbox / none→silent | ✅ | ✅ | ✅ | ✅ |
| 3–5 manual runs + tokens | ⬜ **DVN to log** | ⬜ **DVN to log** | ⬜ **DVN to log** | ⬜ **DVN to log** |
| Worst-case cost | ✅ §9 | ✅ §9 | ✅ §9 | ✅ §9 |
| Shell allowlist | ✅ §7 | ✅ §7 | ✅ §7 | ✅ §7 |
| Parallel→worktrees | ✅ N/A (sequential) | ✅ N/A | ✅ N/A | ✅ N/A |

**The only open box is the same one for all four: run each 3–5 times and record
tokens/iteration in its STATE ledger.** Everything else is satisfied by the suite's
existing design (deterministic Python, dry-run/draft gating, no-network sandbox) plus
the governance blocks now in each task file.

> `daily-lead-attention` and `plp-folder-build` are pre-existing tasks whose
> definitions live in Drive, not this repo. Apply the same `## Governance` block to
> them when you next touch their files — they inherit this standard.
