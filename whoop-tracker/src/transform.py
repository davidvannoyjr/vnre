"""Transform raw resource rows into the joined daily view.

Cycle -> calendar-day rule (see config.CYCLE_DAY_RULE): each physiological
cycle is assigned to the LOCAL date of its start timestamp. Recovery, sleep
and cycle are joined on the WHOOP id linkage (recovery.cycle_id -> cycle.id,
recovery.sleep_id -> sleep.id), never on date proximity. Workouts are attached
to the local date of their own start.
"""

from __future__ import annotations

import csv
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional

import config

MS_PER_HOUR = 3_600_000.0


# --------------------------------------------------------------------------
# Unit conversions
# --------------------------------------------------------------------------
def ms_to_hours(ms: Optional[float]) -> Optional[float]:
    return None if ms is None else round(ms / MS_PER_HOUR, 3)


def kj_to_cal(kj: Optional[float]) -> Optional[float]:
    return None if kj is None else round(kj * config.KJ_TO_CAL, 1)


def c_to_f(c: Optional[float]) -> Optional[float]:
    return None if c is None else round(c * 9.0 / 5.0 + 32.0, 2)


# --------------------------------------------------------------------------
# Local-time helpers
# --------------------------------------------------------------------------
def _parse_offset(tz_offset: Optional[str]) -> timedelta:
    """Parse a '+HH:MM' / '-HH:MM' WHOOP timezone_offset into a timedelta."""
    if not tz_offset:
        return timedelta(0)
    sign = 1
    s = tz_offset.strip()
    if s[0] in "+-":
        sign = -1 if s[0] == "-" else 1
        s = s[1:]
    try:
        hh, mm = s.split(":")
        return sign * timedelta(hours=int(hh), minutes=int(mm))
    except ValueError:
        return timedelta(0)


def _parse_utc(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def local_datetime(start_ts: Optional[str], tz_offset: Optional[str]) -> Optional[datetime]:
    dt = _parse_utc(start_ts)
    if dt is None:
        return None
    return dt + _parse_offset(tz_offset)


def local_date(start_ts: Optional[str], tz_offset: Optional[str]) -> Optional[date]:
    ldt = local_datetime(start_ts, tz_offset)
    return ldt.date() if ldt else None


def local_hour(start_ts: Optional[str], tz_offset: Optional[str]) -> Optional[float]:
    """Fractional local hour-of-day (e.g. 23.5 = 11:30pm), useful as bedtime."""
    ldt = local_datetime(start_ts, tz_offset)
    if ldt is None:
        return None
    return round(ldt.hour + ldt.minute / 60.0, 3)


# --------------------------------------------------------------------------
# Interventions
# --------------------------------------------------------------------------
def load_interventions(path: Path = config.INTERVENTIONS_CSV) -> dict[str, list[dict]]:
    """Return {iso_date: [ {category,item,dose,notes}, ... ]}."""
    out: dict[str, list[dict]] = {}
    if not path.exists():
        return out
    with path.open(newline="") as fh:
        for row in csv.DictReader(fh):
            d = (row.get("date") or "").strip()
            if not d:
                continue
            out.setdefault(d, []).append(
                {
                    "category": (row.get("category") or "").strip(),
                    "item": (row.get("item") or "").strip(),
                    "dose": (row.get("dose") or "").strip(),
                    "notes": (row.get("notes") or "").strip(),
                }
            )
    return out


# --------------------------------------------------------------------------
# Daily view
# --------------------------------------------------------------------------
def build_daily(
    cycles: Iterable[dict],
    recovery: Iterable[dict],
    sleep: Iterable[dict],
    workouts: Iterable[dict],
    interventions: Optional[dict[str, list[dict]]] = None,
) -> list[dict]:
    """Join resources into one row per calendar day, newest first."""
    recovery_by_cycle = {r["cycle_id"]: r for r in recovery}
    sleep_by_id = {s["id"]: s for s in sleep}

    # Aggregate workouts per local day.
    workouts_by_day: dict[date, list[dict]] = {}
    for w in workouts:
        d = local_date(w.get("start"), w.get("timezone_offset"))
        if d is not None:
            workouts_by_day.setdefault(d, []).append(w)

    interventions = interventions or {}
    rows: dict[date, dict] = {}

    for cyc in cycles:
        day = local_date(cyc.get("start"), cyc.get("timezone_offset"))
        if day is None:
            continue
        # If two cycles map to one local day (rare boundary case), keep the
        # later-starting one as the day's representative cycle.
        existing = rows.get(day)
        if existing and (cyc.get("start") or "") <= existing["_cycle_start"]:
            continue

        rec = recovery_by_cycle.get(cyc["id"], {})
        slp = sleep_by_id.get(rec.get("sleep_id"), {}) if rec else {}

        asleep_ms = sum(
            v for v in (
                slp.get("total_light_ms"),
                slp.get("total_sws_ms"),
                slp.get("total_rem_ms"),
            ) if isinstance(v, (int, float))
        ) if slp else None

        hours_sleep = ms_to_hours(asleep_ms) if asleep_ms is not None else None
        need_hours = ms_to_hours(slp.get("sleep_need_ms")) if slp else None
        debt_hours = None
        if need_hours is not None and hours_sleep is not None:
            debt_hours = round(max(0.0, need_hours - hours_sleep), 3)

        day_workouts = workouts_by_day.get(day, [])
        workout_strains = [
            w["strain"] for w in day_workouts if isinstance(w.get("strain"), (int, float))
        ]

        skin_c = rec.get("skin_temp_c")
        row = {
            "date": day.isoformat(),
            "recovery_score": rec.get("recovery_score"),
            "hrv_rmssd_ms": rec.get("hrv_rmssd_ms"),
            "resting_hr": rec.get("resting_hr"),
            "day_strain": cyc.get("strain"),
            "sleep_perf_pct": slp.get("sleep_perf_pct"),
            "sleep_consistency_pct": slp.get("sleep_consistency_pct"),
            "hours_of_sleep": hours_sleep,
            "sleep_need_hours": need_hours,
            "sleep_debt_hours": debt_hours,
            "respiratory_rate": slp.get("respiratory_rate"),
            "spo2": rec.get("spo2_pct"),
            "skin_temp_c": skin_c,
            "skin_temp_f": c_to_f(skin_c),
            "bedtime_hour": local_hour(slp.get("start"), slp.get("timezone_offset")) if slp else None,
            "primary_workout_strain": max(workout_strains) if workout_strains else None,
            "workout_count": len(day_workouts),
            "user_calibrating": int(bool(rec.get("user_calibrating"))),
            "interventions": interventions.get(day.isoformat(), []),
            "_cycle_start": cyc.get("start") or "",
        }
        rows[day] = row

    ordered = sorted(rows.values(), key=lambda r: r["date"], reverse=True)
    for r in ordered:
        r.pop("_cycle_start", None)
    return ordered


# Stable column order for the workbook Daily tab (intervention flags appended).
DAILY_COLUMNS = [
    ("date", "Date"),
    ("recovery_score", "Recovery %"),
    ("hrv_rmssd_ms", "HRV (ms)"),
    ("resting_hr", "RHR (bpm)"),
    ("day_strain", "Day Strain"),
    ("sleep_perf_pct", "Sleep Perf %"),
    ("sleep_consistency_pct", "Sleep Consistency %"),
    ("hours_of_sleep", "Hours Slept"),
    ("sleep_need_hours", "Sleep Need (h)"),
    ("sleep_debt_hours", "Sleep Debt (h)"),
    ("respiratory_rate", "Resp Rate"),
    ("spo2", "SpO2 %"),
    ("skin_temp_c", "Skin Temp °C"),
    ("skin_temp_f", "Skin Temp °F"),
    ("bedtime_hour", "Bedtime (h)"),
    ("primary_workout_strain", "Top Workout Strain"),
    ("workout_count", "Workouts"),
    ("user_calibrating", "Calibrating"),
]


def all_intervention_items(daily: list[dict]) -> list[str]:
    items: set[str] = set()
    for row in daily:
        for iv in row.get("interventions", []):
            if iv.get("item"):
                items.add(iv["item"])
    return sorted(items)
