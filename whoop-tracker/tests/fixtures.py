"""Synthetic WHOOP v2-shaped records for tests only.

These mimic the nested `score` structure the live API returns so the store
upserts and transforms exercise the same code paths as production. Never used
by the shipped workbook.
"""

from __future__ import annotations

import math
from datetime import date, timedelta


def _cycle(day: date, cid: int, strain: float) -> dict:
    return {
        "id": cid,
        "user_id": 1,
        "start": f"{day.isoformat()}T12:00:00.000Z",  # local 07:00 at -05:00
        "end": f"{(day + timedelta(days=1)).isoformat()}T11:59:00.000Z",
        "timezone_offset": "-05:00",
        "score_state": "SCORED",
        "score": {
            "strain": strain,
            "kilojoule": 8000.0 + strain * 100,
            "average_heart_rate": 70,
            "max_heart_rate": 150,
        },
    }


def _recovery(cid: int, sleep_id: str, recovery: float, hrv: float, rhr: float,
              calibrating: bool = False) -> dict:
    return {
        "cycle_id": cid,
        "sleep_id": sleep_id,
        "user_id": 1,
        "created_at": "2026-01-01T12:00:00.000Z",
        "score_state": "SCORED",
        "score": {
            "user_calibrating": calibrating,
            "recovery_score": recovery,
            "resting_heart_rate": rhr,
            "hrv_rmssd_milli": hrv,
            "spo2_percentage": 97.0,
            "skin_temp_celsius": 33.5,
        },
    }


def _sleep(day: date, sid: str, asleep_h: float, need_h: float, perf: float) -> dict:
    asleep_ms = asleep_h * 3_600_000
    return {
        "id": sid,
        "user_id": 1,
        "start": f"{day.isoformat()}T04:00:00.000Z",
        "end": f"{day.isoformat()}T12:00:00.000Z",
        "timezone_offset": "-05:00",
        "nap": False,
        "score_state": "SCORED",
        "score": {
            "stage_summary": {
                "total_in_bed_time_milli": asleep_ms * 1.1,
                "total_awake_time_milli": asleep_ms * 0.1,
                "total_light_sleep_time_milli": asleep_ms * 0.5,
                "total_slow_wave_sleep_time_milli": asleep_ms * 0.25,
                "total_rem_sleep_time_milli": asleep_ms * 0.25,
                "sleep_cycle_count": 5,
                "disturbance_count": 3,
            },
            "sleep_needed": {
                "baseline_milli": need_h * 3_600_000,
                "need_from_sleep_debt_milli": 0,
                "need_from_recent_strain_milli": 0,
                "need_from_recent_nap_milli": 0,
            },
            "respiratory_rate": 15.0,
            "sleep_performance_percentage": perf,
            "sleep_consistency_percentage": 80.0,
            "sleep_efficiency_percentage": 90.0,
        },
    }


def _workout(day: date, wid: str, strain: float) -> dict:
    return {
        "id": wid,
        "user_id": 1,
        "start": f"{day.isoformat()}T18:00:00.000Z",
        "end": f"{day.isoformat()}T19:00:00.000Z",
        "timezone_offset": "-05:00",
        "sport_name": "running",
        "score_state": "SCORED",
        "score": {
            "strain": strain,
            "average_heart_rate": 140,
            "max_heart_rate": 175,
            "kilojoule": 2000.0,
            "distance_meter": 8000.0,
            "altitude_gain_meter": 50.0,
            "zone_durations": {"zone_two_milli": 1_800_000},
        },
    }


def seed(conn, n_days: int = 40, calibrating_first: int = 0):
    """Populate `conn` with n_days of synthetic, correlated data.

    Recovery is made (negatively) correlated with the prior day's strain so the
    correlation/quartile tabs have signal to compute.
    """
    from src import store

    start = date(2026, 5, 1)
    sleep_ids = []
    for i in range(n_days):
        day = start + timedelta(days=i)
        cid = 1000 + i
        sid = f"sleep-{i:04d}-uuid"
        wid = f"wk-{i:04d}-uuid"

        strain = 8.0 + 6.0 * (0.5 + 0.5 * math.sin(i / 3.0))
        # next-day recovery lower after high strain; vary smoothly.
        recovery = 70.0 - (strain - 11.0) * 2.0 + 5.0 * math.cos(i / 4.0)
        hrv = 60.0 + 10.0 * math.sin(i / 5.0)
        rhr = 50.0 + 3.0 * math.cos(i / 6.0)
        asleep = 7.0 + 0.8 * math.sin(i / 2.0)
        need = 8.0
        perf = 80.0 + 10.0 * math.sin(i / 3.5)
        calibrating = i < calibrating_first

        store.upsert_cycle(conn, _cycle(day, cid, strain))
        store.upsert_sleep(conn, _sleep(day, sid, asleep, need, perf))
        store.upsert_recovery(conn, _recovery(cid, sid, recovery, hrv, rhr, calibrating))
        store.upsert_workout(conn, _workout(day, wid, strain - 2.0))
        sleep_ids.append(sid)
    conn.commit()
    return sleep_ids
