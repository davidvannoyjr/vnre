"""SQLite persistence layer.

Tables mirror the WHOOP v2 resources, keeping the raw JSON alongside typed
columns for auditing. All writes are idempotent upserts keyed on the WHOOP
record id, so re-running ingestion never duplicates rows. Timestamps are
stored as UTC ISO-8601 strings exactly as WHOOP returns them.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS cycles (
    id              INTEGER PRIMARY KEY,
    start           TEXT,
    end             TEXT,
    timezone_offset TEXT,
    score_state     TEXT,
    strain          REAL,
    kilojoule       REAL,
    avg_hr          INTEGER,
    max_hr          INTEGER,
    raw_json        TEXT,
    ingested_at     TEXT
);

CREATE TABLE IF NOT EXISTS recovery (
    cycle_id        INTEGER PRIMARY KEY,
    sleep_id        TEXT,
    score_state     TEXT,
    recovery_score  REAL,
    resting_hr      REAL,
    hrv_rmssd_ms    REAL,
    spo2_pct        REAL,
    skin_temp_c     REAL,
    user_calibrating INTEGER,
    raw_json        TEXT,
    ingested_at     TEXT
);

CREATE TABLE IF NOT EXISTS sleep (
    id              TEXT PRIMARY KEY,
    start           TEXT,
    end             TEXT,
    timezone_offset TEXT,
    nap             INTEGER,
    score_state     TEXT,
    sleep_perf_pct          REAL,
    sleep_consistency_pct   REAL,
    sleep_efficiency_pct    REAL,
    total_in_bed_ms REAL,
    total_awake_ms  REAL,
    total_light_ms  REAL,
    total_sws_ms    REAL,
    total_rem_ms    REAL,
    respiratory_rate REAL,
    sleep_need_ms   REAL,
    raw_json        TEXT,
    ingested_at     TEXT
);

CREATE TABLE IF NOT EXISTS workouts (
    id              TEXT PRIMARY KEY,
    start           TEXT,
    end             TEXT,
    timezone_offset TEXT,
    sport_id        INTEGER,
    sport_name      TEXT,
    score_state     TEXT,
    strain          REAL,
    avg_hr          INTEGER,
    max_hr          INTEGER,
    kilojoule       REAL,
    distance_m      REAL,
    altitude_gain_m REAL,
    zone_durations_json TEXT,
    raw_json        TEXT,
    ingested_at     TEXT
);

CREATE TABLE IF NOT EXISTS body (
    recorded_at     TEXT PRIMARY KEY,
    height_m        REAL,
    weight_kg       REAL,
    max_hr          INTEGER
);

CREATE TABLE IF NOT EXISTS sync_state (
    resource        TEXT PRIMARY KEY,
    last_start      TEXT,
    last_run_at     TEXT
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def connect(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Open (and initialize) the SQLite database."""
    path = db_path or config.DB_PATH
    if path != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.executescript(SCHEMA)
    return conn


# --------------------------------------------------------------------------
# Helpers for safely reaching into nested score objects.
# --------------------------------------------------------------------------
def _score(record: dict) -> dict:
    return record.get("score") or {}


def _is_scored(record: dict) -> bool:
    return record.get("score_state") == "SCORED"


# --------------------------------------------------------------------------
# Upserts
# --------------------------------------------------------------------------
def upsert_cycle(conn: sqlite3.Connection, rec: dict) -> None:
    s = _score(rec)
    conn.execute(
        """
        INSERT INTO cycles (id, start, end, timezone_offset, score_state,
            strain, kilojoule, avg_hr, max_hr, raw_json, ingested_at)
        VALUES (:id, :start, :end, :tz, :state, :strain, :kj, :avg, :max, :raw, :ing)
        ON CONFLICT(id) DO UPDATE SET
            start=excluded.start, end=excluded.end,
            timezone_offset=excluded.timezone_offset, score_state=excluded.score_state,
            strain=excluded.strain, kilojoule=excluded.kilojoule,
            avg_hr=excluded.avg_hr, max_hr=excluded.max_hr,
            raw_json=excluded.raw_json, ingested_at=excluded.ingested_at
        """,
        {
            "id": rec["id"],
            "start": rec.get("start"),
            "end": rec.get("end"),
            "tz": rec.get("timezone_offset"),
            "state": rec.get("score_state"),
            "strain": s.get("strain"),
            "kj": s.get("kilojoule"),
            "avg": s.get("average_heart_rate"),
            "max": s.get("max_heart_rate"),
            "raw": json.dumps(rec),
            "ing": _now(),
        },
    )


def upsert_recovery(conn: sqlite3.Connection, rec: dict) -> None:
    s = _score(rec)
    conn.execute(
        """
        INSERT INTO recovery (cycle_id, sleep_id, score_state, recovery_score,
            resting_hr, hrv_rmssd_ms, spo2_pct, skin_temp_c, user_calibrating,
            raw_json, ingested_at)
        VALUES (:cid, :sid, :state, :rec, :rhr, :hrv, :spo2, :skin, :cal, :raw, :ing)
        ON CONFLICT(cycle_id) DO UPDATE SET
            sleep_id=excluded.sleep_id, score_state=excluded.score_state,
            recovery_score=excluded.recovery_score, resting_hr=excluded.resting_hr,
            hrv_rmssd_ms=excluded.hrv_rmssd_ms, spo2_pct=excluded.spo2_pct,
            skin_temp_c=excluded.skin_temp_c, user_calibrating=excluded.user_calibrating,
            raw_json=excluded.raw_json, ingested_at=excluded.ingested_at
        """,
        {
            "cid": rec["cycle_id"],
            "sid": rec.get("sleep_id"),
            "state": rec.get("score_state"),
            "rec": s.get("recovery_score"),
            "rhr": s.get("resting_heart_rate"),
            "hrv": s.get("hrv_rmssd_milli"),
            "spo2": s.get("spo2_percentage"),
            "skin": s.get("skin_temp_celsius"),
            "cal": 1 if s.get("user_calibrating") else 0,
            "raw": json.dumps(rec),
            "ing": _now(),
        },
    )


def upsert_sleep(conn: sqlite3.Connection, rec: dict) -> None:
    s = _score(rec)
    stages = s.get("stage_summary") or {}
    need = s.get("sleep_needed") or {}
    sleep_need_ms = None
    if need:
        sleep_need_ms = sum(
            v for v in (
                need.get("baseline_milli"),
                need.get("need_from_sleep_debt_milli"),
                need.get("need_from_recent_strain_milli"),
                need.get("need_from_recent_nap_milli"),
            ) if isinstance(v, (int, float))
        )
    conn.execute(
        """
        INSERT INTO sleep (id, start, end, timezone_offset, nap, score_state,
            sleep_perf_pct, sleep_consistency_pct, sleep_efficiency_pct,
            total_in_bed_ms, total_awake_ms, total_light_ms, total_sws_ms,
            total_rem_ms, respiratory_rate, sleep_need_ms, raw_json, ingested_at)
        VALUES (:id, :start, :end, :tz, :nap, :state, :perf, :cons, :eff,
            :bed, :awake, :light, :sws, :rem, :rr, :need, :raw, :ing)
        ON CONFLICT(id) DO UPDATE SET
            start=excluded.start, end=excluded.end,
            timezone_offset=excluded.timezone_offset, nap=excluded.nap,
            score_state=excluded.score_state, sleep_perf_pct=excluded.sleep_perf_pct,
            sleep_consistency_pct=excluded.sleep_consistency_pct,
            sleep_efficiency_pct=excluded.sleep_efficiency_pct,
            total_in_bed_ms=excluded.total_in_bed_ms, total_awake_ms=excluded.total_awake_ms,
            total_light_ms=excluded.total_light_ms, total_sws_ms=excluded.total_sws_ms,
            total_rem_ms=excluded.total_rem_ms, respiratory_rate=excluded.respiratory_rate,
            sleep_need_ms=excluded.sleep_need_ms, raw_json=excluded.raw_json,
            ingested_at=excluded.ingested_at
        """,
        {
            "id": rec["id"],
            "start": rec.get("start"),
            "end": rec.get("end"),
            "tz": rec.get("timezone_offset"),
            "nap": 1 if rec.get("nap") else 0,
            "state": rec.get("score_state"),
            "perf": s.get("sleep_performance_percentage"),
            "cons": s.get("sleep_consistency_percentage"),
            "eff": s.get("sleep_efficiency_percentage"),
            "bed": stages.get("total_in_bed_time_milli"),
            "awake": stages.get("total_awake_time_milli"),
            "light": stages.get("total_light_sleep_time_milli"),
            "sws": stages.get("total_slow_wave_sleep_time_milli"),
            "rem": stages.get("total_rem_sleep_time_milli"),
            "rr": s.get("respiratory_rate"),
            "need": sleep_need_ms,
            "raw": json.dumps(rec),
            "ing": _now(),
        },
    )


def upsert_workout(conn: sqlite3.Connection, rec: dict) -> None:
    s = _score(rec)
    zones = s.get("zone_durations") or s.get("zone_duration") or {}
    conn.execute(
        """
        INSERT INTO workouts (id, start, end, timezone_offset, sport_id, sport_name,
            score_state, strain, avg_hr, max_hr, kilojoule, distance_m,
            altitude_gain_m, zone_durations_json, raw_json, ingested_at)
        VALUES (:id, :start, :end, :tz, :sid, :sname, :state, :strain, :avg, :max,
            :kj, :dist, :alt, :zones, :raw, :ing)
        ON CONFLICT(id) DO UPDATE SET
            start=excluded.start, end=excluded.end,
            timezone_offset=excluded.timezone_offset, sport_id=excluded.sport_id,
            sport_name=excluded.sport_name, score_state=excluded.score_state,
            strain=excluded.strain, avg_hr=excluded.avg_hr, max_hr=excluded.max_hr,
            kilojoule=excluded.kilojoule, distance_m=excluded.distance_m,
            altitude_gain_m=excluded.altitude_gain_m,
            zone_durations_json=excluded.zone_durations_json,
            raw_json=excluded.raw_json, ingested_at=excluded.ingested_at
        """,
        {
            "id": rec["id"],
            "start": rec.get("start"),
            "end": rec.get("end"),
            "tz": rec.get("timezone_offset"),
            "sid": rec.get("sport_id"),
            "sname": rec.get("sport_name"),
            "state": rec.get("score_state"),
            "strain": s.get("strain"),
            "avg": s.get("average_heart_rate"),
            "max": s.get("max_heart_rate"),
            "kj": s.get("kilojoule"),
            "dist": s.get("distance_meter"),
            "alt": s.get("altitude_gain_meter"),
            "zones": json.dumps(zones),
            "raw": json.dumps(rec),
            "ing": _now(),
        },
    )


def upsert_body(conn: sqlite3.Connection, rec: dict, recorded_at: Optional[str] = None) -> None:
    conn.execute(
        """
        INSERT INTO body (recorded_at, height_m, weight_kg, max_hr)
        VALUES (:at, :h, :w, :hr)
        ON CONFLICT(recorded_at) DO UPDATE SET
            height_m=excluded.height_m, weight_kg=excluded.weight_kg,
            max_hr=excluded.max_hr
        """,
        {
            "at": recorded_at or _now(),
            "h": rec.get("height_meter"),
            "w": rec.get("weight_kilogram"),
            "hr": rec.get("max_heart_rate"),
        },
    )


# --------------------------------------------------------------------------
# Watermarks
# --------------------------------------------------------------------------
def get_watermark(conn: sqlite3.Connection, resource: str) -> Optional[str]:
    row = conn.execute(
        "SELECT last_start FROM sync_state WHERE resource = ?", (resource,)
    ).fetchone()
    return row["last_start"] if row else None


def set_watermark(conn: sqlite3.Connection, resource: str, last_start: Optional[str]) -> None:
    conn.execute(
        """
        INSERT INTO sync_state (resource, last_start, last_run_at)
        VALUES (?, ?, ?)
        ON CONFLICT(resource) DO UPDATE SET
            last_start=excluded.last_start, last_run_at=excluded.last_run_at
        """,
        (resource, last_start, _now()),
    )


# --------------------------------------------------------------------------
# Read helpers used by transform/analytics
# --------------------------------------------------------------------------
def fetch_all(conn: sqlite3.Connection, table: str) -> list[dict]:
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    return [dict(r) for r in rows]


def latest_body(conn: sqlite3.Connection) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM body ORDER BY recorded_at DESC LIMIT 1"
    ).fetchone()
    return dict(row) if row else None
