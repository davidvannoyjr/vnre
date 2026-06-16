"""Transform tests: cycle→day mapping, sleep-debt floor, ms→hours, calibrating."""

from datetime import date

from src import transform


def test_cycle_day_mapping_across_timezone_boundary():
    # 02:00 UTC at offset -05:00 is 21:00 the PREVIOUS local day.
    d = transform.local_date("2026-01-02T02:00:00.000Z", "-05:00")
    assert d == date(2026, 1, 1)

    # 23:00 UTC at offset +02:00 is 01:00 the NEXT local day.
    d2 = transform.local_date("2026-01-01T23:00:00.000Z", "+02:00")
    assert d2 == date(2026, 1, 2)


def test_ms_to_hours_and_units():
    assert transform.ms_to_hours(3_600_000) == 1.0
    assert transform.ms_to_hours(None) is None
    assert transform.kj_to_cal(1000) == 239.0
    assert transform.c_to_f(0) == 32.0
    assert transform.c_to_f(37) == 98.6


def test_sleep_debt_floor_at_zero():
    # Slept MORE than needed -> debt floored at 0, not negative.
    cycles = [{
        "id": 1, "start": "2026-05-01T12:00:00.000Z",
        "timezone_offset": "-05:00", "strain": 10.0,
    }]
    recovery = [{"cycle_id": 1, "sleep_id": "s1", "recovery_score": 60,
                 "hrv_rmssd_ms": 55, "resting_hr": 50, "user_calibrating": 0}]
    # 9h asleep (3h each light/sws/rem) vs 8h need.
    three = 3 * 3_600_000
    sleep = [{
        "id": "s1", "start": "2026-05-01T04:00:00.000Z", "timezone_offset": "-05:00",
        "total_light_ms": three, "total_sws_ms": three, "total_rem_ms": three,
        "sleep_need_ms": 8 * 3_600_000, "sleep_perf_pct": 95,
        "sleep_consistency_pct": 80,
    }]
    daily = transform.build_daily(cycles, recovery, sleep, [])
    assert len(daily) == 1
    row = daily[0]
    assert row["hours_of_sleep"] == 9.0
    assert row["sleep_debt_hours"] == 0.0  # floored, never negative


def test_join_uses_id_linkage_and_workout_aggregation():
    cycles = [{"id": 7, "start": "2026-05-02T12:00:00.000Z",
               "timezone_offset": "-05:00", "strain": 14.0}]
    recovery = [{"cycle_id": 7, "sleep_id": "sX", "recovery_score": 42,
                 "hrv_rmssd_ms": 48, "resting_hr": 52, "user_calibrating": 0}]
    sleep = [{"id": "sX", "start": "2026-05-02T05:00:00.000Z",
              "timezone_offset": "-05:00", "total_light_ms": 3_600_000,
              "total_sws_ms": 3_600_000, "total_rem_ms": 3_600_000,
              "sleep_need_ms": 8 * 3_600_000, "sleep_perf_pct": 70}]
    workouts = [
        {"id": "w1", "start": "2026-05-02T18:00:00.000Z",
         "timezone_offset": "-05:00", "strain": 9.0},
        {"id": "w2", "start": "2026-05-02T20:00:00.000Z",
         "timezone_offset": "-05:00", "strain": 12.5},
    ]
    daily = transform.build_daily(cycles, recovery, sleep, workouts)
    row = daily[0]
    assert row["recovery_score"] == 42          # joined by cycle_id
    assert row["primary_workout_strain"] == 12.5  # max of the day
    assert row["workout_count"] == 2


def test_calibrating_flag_propagates():
    cycles = [{"id": 1, "start": "2026-05-01T12:00:00.000Z",
               "timezone_offset": "-05:00", "strain": 10.0}]
    recovery = [{"cycle_id": 1, "sleep_id": None, "recovery_score": 50,
                 "hrv_rmssd_ms": 50, "resting_hr": 50, "user_calibrating": 1}]
    daily = transform.build_daily(cycles, recovery, [], [])
    assert daily[0]["user_calibrating"] == 1
