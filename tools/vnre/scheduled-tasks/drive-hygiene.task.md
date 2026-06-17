# Scheduled Task — drive-hygiene

- **Name:** `drive-hygiene`
- **Schedule:** Monthly — **first Sunday 5:00 PM** (pairs with the weekly `meta-review`; off the AM critical path)
- **Skill:** none — uses the Google Drive connector (`search_files` / `get_file_metadata`)
- **Output:** `Follow Up Boss Pipeline/_state/Drive Hygiene Report YYYY-MM-DD.md`
- **Prereqs:** Google Drive connector connected

Catches the exact failure mode the multi-device sync keeps producing: **duplicate
`CLAUDE.md`**, sync **conflict files**, husk folders, and **zip-vs-unpacked tool drift**.
It reports a cleanup list — it does not delete (the connector can't, and deletion is
DVN's call). Read-only by design.

## What it scans for
1. **Duplicate `CLAUDE.md`** — anything titled `CLAUDE.md` outside the one canonical
   `Claude md/CLAUDE.md`. Invariant: exactly one in Drive (CLAUDE.md §11).
2. **Sync conflict files** — titles containing `(1)`, `(2)`, `conflicted copy`, or a
   second copy of a same-named file in the same parent. Newest content wins; merge + delete.
3. **Tool drift** — `04 Tools/` holding both unpacked skill folders **and** a
   `vnreaidrvntools*.zip`. The unpacked folders are the runtime home; any **undated** zip
   is stale (keep only dated backup snapshots).
4. **Husk folders** — near-empty `Claude`/`Claude md`/`Artifacts`/`Projects` folders from
   sync drift (the §12 husk-chain pattern).
5. **Oversized/binary in the brain** — large binaries that should live outside the synced
   markdown tree.

## Trigger prompt (paste verbatim)

```
Run the monthly Drive hygiene scan.

1. Via the Google Drive connector:
   - search title = 'CLAUDE.md' → list every copy with parent + size + modifiedTime.
     Flag all but the canonical "Claude md/CLAUDE.md" (the largest, most-recent one).
   - search title contains '(1)' OR title contains 'conflicted copy' → conflict files.
   - list children of "04 Tools/" → flag if both unpacked skill folders AND any
     vnreaidrvntools*.zip exist; flag any UNDATED vnreaidrvntools.zip as stale.
   - flag near-empty husk folders named Claude / Claude md / Artifacts / Projects.
2. Write "Follow Up Boss Pipeline/_state/Drive Hygiene Report <today>.md": a table per
   category with the file/folder, its Drive link, size, and the recommended action
   (KEEP / DELETE / MERGE / UNPACK). Never auto-delete — this is a report.
3. Post a SHORT chat summary ONLY IF the scan finds anything actionable: duplicate
   CLAUDE.md count, conflict-file count, tool drift. A clean Drive → write the file,
   one green line, stop.
```

## On failure
- Drive connector not connected → say so; nothing to scan.
- Connector has no delete tool → expected; this task only reports. DVN deletes from Drive.

## Governance (agent-ops — see [GOVERNANCE.md](GOVERNANCE.md))
- **Trigger:** cron — monthly, first Sunday 5:00 PM. Manual: "run the Drive hygiene scan".
- **STATE:** `<home>/_state/drive-hygiene.STATE.md`. Read first (last scan's duplicate/conflict
  counts for a delta); write last (counts, tokens, cost).
- **Writer ≠ checker — hard gate: `Report-Only Gate`.** It surfaces a cleanup list; it never
  deletes, moves, or overwrites a Drive file. Deletion is DVN's manual action.
- **Stop condition (machine-checkable):** report `.md` written **AND ≥1 Drive query returned**.
- **Iteration ceiling:** 1 pass/fire · retry ≤3 · 20 tool-calls hard cap.
- **Autonomy: L1 (Propose).** Read-only scan + report.
- **Found-something → inbox** (cleanup list + short chat flag). **Found-nothing → silent**
  (write the file, one green line, stop).
- **Shell allowlist:** none — Drive connector tools only. No network shell.
- **Parallel:** N/A — runs alone, monthly.
