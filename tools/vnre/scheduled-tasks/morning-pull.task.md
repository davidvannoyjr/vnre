# Scheduled Task — morning-pull

- **Name:** `morning-pull`
- **Schedule:** Daily — **4:55 AM** (ahead of the 5:00 lead brief and 5:15 hunter list)
- **Skill:** none — a single shared FUB pull primitive (`fub_pull.py` / `fub_*` MCP tools)
- **Output:** `Follow Up Boss Pipeline/_data/fub-morning-pull-YYYY-MM-DD.json` (shared artifact)
- **Prereqs:** `followupboss` MCP connected (or `fub_pull.py` on a networked machine)

One pull, two consumers. Today the **5:00 lead brief** and **5:15 active-hunter** each hit
FUB independently 15 minutes apart — two pulls of overlapping people (COI / Past Client live
in both worlds), double the pull tokens, and a window where suppression state can drift
between them. This task pulls the **union once** at 4:55 and writes a shared artifact; both
downstream tasks **read it and filter**, instead of pulling again. Net: one FUB pull per
morning instead of two, and a single consistent suppression snapshot.

## What it pulls (the union — superset of both consumers)

| Lane | Segments | Used by |
|---|---|---|
| Pipeline leads | Hot, Watch, Nurture | daily-lead-attention |
| Prospecting | FSBO, Expired, Aged Lead, Geo-farm, COI, Past Client | active-hunter |

Fields per person: `id, name, phone, email, address/city, tags, stage, segment,
lastAttemptDate, attempts, lastContactDate, signal`, and the **DNC/opt-out** tag.

## Trigger prompt (paste verbatim)

```
Build today's shared FUB morning pull.

1. Pull the union of pipeline-lead segments (Hot, Watch, Nurture) and prospecting
   segments (FSBO, Expired, Aged Lead, Geo-farm, COI, Past Client) from Follow Up Boss
   in ONE pass — id, name, phone, email, address/city, tags, stage, segment,
   lastAttemptDate, attempts, lastContactDate, signal, and the DNC/opt-out tag.
2. Write it to "Follow Up Boss Pipeline/_data/fub-morning-pull-<today>.json" with a
   top-level {pulledAt, count, segments[], people[]}.
3. Exit silent — no chat summary, no deliverable. This is a data primitive. If the pull
   is empty or fails, do NOT overwrite a good prior file; log it and stop so the
   downstream tasks fall back to their own pull.
4. Housekeeping: delete fub-morning-pull-*.json older than 7 days.
```

## How the consumers use it
- **active-hunter** (5:15) and **daily-lead-attention** (5:00): step 1 becomes "**read
  `_data/fub-morning-pull-<today>.json` if present and fresh (pulledAt = today); filter to
  my segments. If absent/stale, self-pull as before.**" Non-breaking — the fallback means
  nothing breaks if this task isn't created yet or fails.

> **DVN action to finish the merge:** this repo updates `active-hunter` to consume the
> shared pull. `daily-lead-attention` is defined in Drive (not this repo) — make the same
> "read-if-present, else self-pull" edit there, and create this `morning-pull` task in
> Cowork at 4:55. Until both are wired, each task safely self-pulls.

## On failure
- `fub_*` tools missing → restart Claude / `fix-claude-config.sh` (Claude quit). Consumers self-pull.
- Empty pull → log and stop; never overwrite a good prior file. Consumers self-pull.

## Governance (agent-ops — see [GOVERNANCE.md](GOVERNANCE.md))
- **Trigger:** cron — daily 4:55 AM. Manual: "build the morning pull".
- **STATE:** `<home>/_state/morning-pull.STATE.md`. Read first (yesterday's count for a
  sanity delta); write last (count, pulledAt, tokens, cost).
- **Writer ≠ checker — hard gate: `Freshness Gate`.** A consumer uses the artifact only if
  `pulledAt = today`; a stale/missing file forces self-pull. The pull never overwrites a
  good prior file with an empty one.
- **Stop condition (machine-checkable):** artifact written **AND `count > 0`**.
- **Iteration ceiling:** 1 pass/fire · retry ≤3 · 20 tool-calls hard cap.
- **Autonomy: L1 (Propose).** Read-only data primitive — pulls and writes a local file; sends/drafts nothing.
- **Found-something → (no inbox; it's a primitive)** the artifact is the output. **Found-nothing
  → silent** (log, keep prior file, consumers self-pull).
- **Shell allowlist:** `python3 scripts/fub_pull.py …` (on a networked machine) or `fub_*`
  MCP tools in-session; `rm` within `_data/` only. No curl from the sandbox.
- **Parallel:** N/A — runs first, alone, before the consumers.
