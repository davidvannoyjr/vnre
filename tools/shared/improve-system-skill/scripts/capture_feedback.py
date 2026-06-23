#!/usr/bin/env python3
"""/improve-system — capture a task learning and draft the edit.

Appends a structured, dated entry to LEARNINGS.md and prints a proposed-edit block
for DVN to approve. Approval-gated by design: it writes ONLY to the log. The edit
to the target Knowledge/Skill file is applied separately, after DVN says yes —
nothing here self-modifies the brain.

Usage:
  python3 capture_feedback.py --task "..." --worked "..." --change "..." \
      --target {knowledge,skill,new-skill,project} --file path/to/target \
      [--log LEARNINGS.md]
  python3 capture_feedback.py --selftest

Design rules (suite-wide): deterministic, offline --selftest, tunable constants at
the top, approval-gated (writes the log, applies no brain edit, sends nothing).
"""

import argparse
import os
import sys
from datetime import date

# ---- Tunable constants -----------------------------------------------------
VALID_TARGETS = ["knowledge", "skill", "new-skill", "project"]
DEFAULT_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "LEARNINGS.md")
LOG_HEADER = "# LEARNINGS — /improve-system changelog\n\n" \
             "Running log of task learnings and the edits they drove. Newest at the " \
             "bottom. Each entry names one target file; the edit is applied only " \
             "after DVN approves it.\n"
# ---------------------------------------------------------------------------


def format_entry(today, task, worked, change, target, file_, status="proposed"):
    return (
        f"\n## {today} — {task}\n"
        f"- **Worked:** {worked or '—'}\n"
        f"- **Change:** {change}\n"
        f"- **Target:** {target} → `{file_ or 'TBD'}`\n"
        f"- **Status:** {status}\n"
    )


def proposed_edit_block(task, change, target, file_):
    return (
        "\n--- PROPOSED EDIT (approval-gated — not applied) ---\n"
        f"Target ({target}): {file_ or 'TBD'}\n"
        f"From learning: {task}\n"
        f"Make this change: {change}\n"
        "Apply only after DVN approves. If Knowledge: also overwrite the single "
        "Drive CLAUDE.md copy in place (master manual §11).\n"
        "----------------------------------------------------\n"
    )


def ensure_log(path):
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(LOG_HEADER)


def append_entry(path, entry):
    ensure_log(path)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(entry)


def run(args):
    if args.target not in VALID_TARGETS:
        print(f"[error] --target must be one of {VALID_TARGETS}", file=sys.stderr)
        return 1
    if not args.change:
        print("[error] --change is required: state the one specific improvement.",
              file=sys.stderr)
        return 1
    today = args.today or date.today().isoformat()
    entry = format_entry(today, args.task or "(untitled task)", args.worked,
                         args.change, args.target, args.file)
    log_path = args.log or DEFAULT_LOG
    append_entry(log_path, entry)
    print(f"Logged learning -> {os.path.normpath(log_path)}")
    print(proposed_edit_block(args.task or "(untitled task)", args.change,
                              args.target, args.file))
    return 0


def selftest():
    import tempfile
    today = "2026-06-23"
    entry = format_entry(today, "Test task", "X worked", "Do Y next time",
                         "skill", "tools/foo/SKILL.md")
    for needle in ["2026-06-23 — Test task", "Do Y next time", "skill",
                   "tools/foo/SKILL.md", "**Status:** proposed"]:
        assert needle in entry, f"entry missing: {needle}"
    block = proposed_edit_block("Test task", "Do Y next time", "skill", "tools/foo/SKILL.md")
    assert "approval-gated" in block and "not applied" in block, "edit block not gated"
    with tempfile.TemporaryDirectory() as d:
        log = os.path.join(d, "L.md")
        append_entry(log, entry)
        append_entry(log, format_entry(today, "Second", "", "Another change", "knowledge", "claude/CLAUDE.md"))
        with open(log, encoding="utf-8") as fh:
            body = fh.read()
        assert body.startswith("# LEARNINGS"), "log header missing"
        assert body.count("\n## ") == 2, "expected two entries in log"
        assert "knowledge" in body, "second target not recorded"
    # invalid target rejected
    bad = argparse.Namespace(target="oops", change="x", task="t", worked="",
                             file="f", today=today, log=None)
    assert run(bad) == 1, "invalid target should fail"
    # missing change rejected
    bad2 = argparse.Namespace(target="skill", change="", task="t", worked="",
                              file="f", today=today, log=None)
    assert run(bad2) == 1, "missing change should fail"
    print("selftest passed: entries format + append correctly, edits stay gated, "
          "bad input rejected.")
    return 0


def main():
    p = argparse.ArgumentParser(description="/improve-system feedback capture")
    p.add_argument("--task", help="what the task was")
    p.add_argument("--worked", help="what worked")
    p.add_argument("--change", help="the one specific improvement (required)")
    p.add_argument("--target", choices=VALID_TARGETS, help="where the edit lands")
    p.add_argument("--file", help="path to the target file")
    p.add_argument("--log", help=f"log path (default {DEFAULT_LOG})")
    p.add_argument("--today", help="override date (YYYY-MM-DD)")
    p.add_argument("--selftest", action="store_true", help="run offline self-test")
    args = p.parse_args()
    if args.selftest:
        return selftest()
    if not args.target:
        p.error("--target is required (or use --selftest)")
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
