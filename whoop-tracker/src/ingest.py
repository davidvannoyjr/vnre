"""Ingestion: pull each resource, upsert, and advance watermarks.

``backfill`` does a full historical pull from ``--since``. ``sync`` does an
incremental delta pull using the stored per-resource watermark, with a small
overlap window so nothing falls through the cracks (upserts make the overlap
harmless).
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import config
from . import store
from .client import WhoopClient

log = logging.getLogger("whoop.ingest")

# Re-pull this much before the watermark on incremental sync, so edge records
# that were still being scored at the previous run get refreshed.
_OVERLAP = timedelta(days=2)

# How each collection maps to (client iterator, upsert fn, timestamp field used
# for the watermark). Recovery has no `start`; we watermark it on `created_at`.
_RESOURCES: dict[str, tuple[str, Callable, str]] = {
    "cycles": ("iter_cycles", store.upsert_cycle, "start"),
    "sleep": ("iter_sleep", store.upsert_sleep, "start"),
    "workout": ("iter_workouts", store.upsert_workout, "start"),
    "recovery": ("iter_recovery", store.upsert_recovery, "created_at"),
}


def _parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _ingest_resource(
    conn,
    client: WhoopClient,
    resource: str,
    start: Optional[str],
    end: Optional[str],
) -> int:
    iter_name, upsert_fn, ts_field = _RESOURCES[resource]
    iterator = getattr(client, iter_name)(start=start, end=end)

    count = 0
    max_ts = _parse_iso(start)
    for rec in iterator:
        upsert_fn(conn, rec)
        count += 1
        ts = _parse_iso(rec.get(ts_field))
        if ts and (max_ts is None or ts > max_ts):
            max_ts = ts
    conn.commit()

    if max_ts is not None:
        store.set_watermark(conn, resource, _iso(max_ts))
    log.info("Ingested %d %s records.", count, resource)
    return count


def _sync_singletons(conn, client: WhoopClient) -> None:
    """Profile is not persisted (no table); body is point-in-time."""
    try:
        client.get_profile()  # validates auth/scope; nothing to persist
        body = client.get_body()
        store.upsert_body(conn, body)
        conn.commit()
        log.info("Refreshed body measurement.")
    except Exception as exc:  # non-fatal for the daily pipeline
        log.warning("Could not refresh profile/body: %s", exc)


def backfill(conn, since: Optional[str] = None, client: Optional[WhoopClient] = None) -> dict:
    """Full historical pull from `since` (default: account start = no bound)."""
    client = client or WhoopClient()
    start = None
    if since:
        # Accept YYYY-MM-DD or full ISO.
        dt = _parse_iso(since) or datetime.strptime(since, "%Y-%m-%d").replace(
            tzinfo=timezone.utc
        )
        start = _iso(dt)

    _sync_singletons(conn, client)
    results = {}
    for resource in config.COLLECTION_RESOURCES:
        results[resource] = _ingest_resource(conn, client, resource, start, None)
    return results


def sync(conn, client: Optional[WhoopClient] = None) -> dict:
    """Incremental delta pull using the per-resource watermark."""
    client = client or WhoopClient()
    _sync_singletons(conn, client)

    results = {}
    for resource in config.COLLECTION_RESOURCES:
        watermark = store.get_watermark(conn, resource)
        start = None
        if watermark:
            dt = _parse_iso(watermark)
            if dt:
                start = _iso(dt - _OVERLAP)
        if start is None:
            log.info("No watermark for %s; doing a full pull.", resource)
        results[resource] = _ingest_resource(conn, client, resource, start, None)
    return results
