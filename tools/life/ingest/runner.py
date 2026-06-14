#!/usr/bin/env python3
"""DVN Life Design — ingestion runner.

Orchestrates every source adapter, normalizes to the `life.*` warehouse schema, and records
an audit row per source in life.source_runs. Each adapter exposes `pull(cfg) -> dict` returning
warehouse-shaped rows; the runner writes them and never lets one source failure abort the rest.

Usage:
    python ingest/runner.py --once          # one full pass (backfill / manual)
    python ingest/runner.py --source quickbooks
"""
import argparse, importlib, json, sys, datetime as dt
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = [
    "quickbooks", "function_health", "credit_karma", "google_calendar", "granola",
    "follow_up_boss", "whoop", "withings", "macro_log",
]


def load_config():
    p = ROOT.parent / "config.json"
    if not p.exists():
        print("config.json not found — copy config.example.json and fill it in.", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text())


def write(warehouse, table, rows):
    """Upsert rows into the warehouse. Implemented against Supabase REST in production;
    here it is the single integration point so adapters stay storage-agnostic."""
    # from supabase import create_client; client.table(table).upsert(rows).execute()
    print(f"  → {table}: {len(rows)} row(s)")


def run_source(name, cfg, warehouse):
    src = cfg["sources"].get(name, {})
    if not src.get("enabled"):
        print(f"[skip] {name} (disabled: {src.get('reason') or src.get('note') or 'not enabled'})")
        return
    started = dt.datetime.utcnow().isoformat()
    try:
        mod = importlib.import_module(f"sources.{name}")
        tables = mod.pull(src)
        total = 0
        for table, rows in tables.items():
            write(warehouse, table, rows)
            total += len(rows)
        print(f"[ok]   {name}: {total} row(s)")
        write(warehouse, "life.source_runs",
              [{"source": name, "started_at": started, "status": "ok", "rows_written": total}])
    except Exception as e:  # one bad source must not sink the pass
        print(f"[err]  {name}: {e}")
        write(warehouse, "life.source_runs",
              [{"source": name, "started_at": started, "status": "error", "note": str(e)}])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--source")
    args = ap.parse_args()
    cfg = load_config()
    warehouse = cfg["warehouse"]
    sys.path.insert(0, str(ROOT))
    targets = [args.source] if args.source else SOURCES
    for name in targets:
        run_source(name, cfg, warehouse)


if __name__ == "__main__":
    main()
