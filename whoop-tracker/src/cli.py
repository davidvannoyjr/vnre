"""Command-line entry point: `whoop auth | backfill | sync | build | all`.

Run as a module from the project root:

    python -m src.cli all
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import config
from . import auth, ingest, store, workbook

_INTERVENTIONS_HEADER = "date,category,item,dose,notes\n"
_INTERVENTIONS_EXAMPLES = [
    "2026-06-10,supplement,magnesium glycinate,400mg,before bed",
    "2026-06-11,substance,alcohol,2 drinks,dinner out",
    "2026-06-12,sleep_protocol,no screens after 9pm,,wind-down routine",
    "2026-06-13,nutrition,late meal,,ate at 10pm",
    "2026-06-14,training,zone 2 ride,60min,easy aerobic",
]


def _configure_logging(quiet: bool) -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    handlers: list[logging.Handler] = [logging.FileHandler(config.LOG_PATH)]
    if not quiet:
        handlers.append(logging.StreamHandler(sys.stdout))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
        force=True,
    )


def _ensure_interventions() -> None:
    """Seed data/interventions.csv with a header + 5 editable example rows."""
    path = config.INTERVENTIONS_CSV
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_INTERVENTIONS_HEADER + "\n".join(_INTERVENTIONS_EXAMPLES) + "\n")
    logging.getLogger("whoop.cli").info("Seeded %s with example rows.", path)


def cmd_auth(_args) -> int:
    auth.run_oauth_flow()
    return 0


def cmd_backfill(args) -> int:
    _ensure_interventions()
    conn = store.connect()
    try:
        results = ingest.backfill(conn, since=args.since)
    finally:
        conn.close()
    print("Backfill complete:", results)
    return 0


def cmd_sync(_args) -> int:
    _ensure_interventions()
    conn = store.connect()
    try:
        results = ingest.sync(conn)
    finally:
        conn.close()
    print("Sync complete:", results)
    return 0


def cmd_build(_args) -> int:
    _ensure_interventions()
    conn = store.connect()
    try:
        path = workbook.build(conn)
    finally:
        conn.close()
    print(f"Workbook built: {path}")
    return 0


def cmd_all(args) -> int:
    rc = cmd_sync(args)
    if rc != 0:
        return rc
    return cmd_build(args)


def cmd_webhook(args) -> int:
    from . import webhooks
    webhooks.serve(host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="whoop", description="WHOOP tracker pipeline.")
    p.add_argument("--quiet", action="store_true", help="Log to file only.")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("auth", help="Run OAuth and store encrypted tokens.")

    pb = sub.add_parser("backfill", help="Full historical pull.")
    pb.add_argument("--since", default=None, help="YYYY-MM-DD (default: account start).")

    sub.add_parser("sync", help="Incremental delta pull using the watermark.")
    sub.add_parser("build", help="Regenerate whoop_dashboard.xlsx from the DB.")
    sub.add_parser("all", help="Sync then build (the daily command).")

    pw = sub.add_parser("webhook", help="Run the webhook receiver (push updates).")
    pw.add_argument("--host", default="0.0.0.0")
    pw.add_argument("--port", type=int, default=8099)
    return p


_DISPATCH = {
    "auth": cmd_auth,
    "backfill": cmd_backfill,
    "sync": cmd_sync,
    "build": cmd_build,
    "all": cmd_all,
    "webhook": cmd_webhook,
}


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    _configure_logging(args.quiet)
    try:
        return _DISPATCH[args.command](args)
    except Exception as exc:  # surface a clean message, full trace in the log
        logging.getLogger("whoop.cli").exception("Command failed.")
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
