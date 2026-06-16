"""Analytics tests: z-score, correlation, n<5 guard, baseline exclusion."""

import math

from src import analytics


def _daily(values, key="recovery_score", calibrating=None):
    """Build minimal daily rows (chronological dates ascending)."""
    rows = []
    for i, v in enumerate(values):
        rows.append({
            "date": f"2026-05-{i+1:02d}",
            key: v,
            "user_calibrating": (calibrating[i] if calibrating else 0),
        })
    return rows


def test_zscore_on_known_series():
    # Series with mean 50, sample SD computed; latest value 70.
    values = [40, 50, 60, 50, 70]
    daily = _daily(values)
    table = analytics.rolling_table(daily)
    latest = table[0]["recovery_score"]
    # baseline = mean of all (no calibrating) = 54; sd = sample sd.
    expected_mean = sum(values) / len(values)
    assert math.isclose(latest["baseline"], expected_mean, rel_tol=1e-9)
    sd = analytics.stdev(values)
    expected_z = (70 - expected_mean) / sd
    assert math.isclose(latest["z"], expected_z, rel_tol=1e-9)


def test_baseline_excludes_calibrating_days():
    values = [10, 10, 10, 100]      # last day huge but calibrating
    calib = [0, 0, 0, 1]
    daily = _daily(values, calibrating=calib)
    base = analytics.baseline(daily, "recovery_score", window=30)
    assert math.isclose(base, 10.0)  # 100 excluded


def test_pearson_perfect_correlation():
    xs = [1, 2, 3, 4, 5, 6]
    ys = [2, 4, 6, 8, 10, 12]       # y = 2x
    r, n = analytics.pearson(xs, ys)
    assert n == 6
    assert math.isclose(r, 1.0, rel_tol=1e-9)


def test_pearson_n_guard_returns_nan_not_crash():
    xs = [1, 2, 3]
    ys = [2, 4, 6]
    r, n = analytics.pearson(xs, ys)  # n=3 < 5
    assert n == 3
    assert math.isnan(r)


def test_linear_slope_positive():
    assert math.isclose(analytics.linear_slope([1, 2, 3, 4]), 1.0, rel_tol=1e-9)
    assert math.isnan(analytics.linear_slope([5]))


def test_strain_recovery_balance_buckets():
    rows = []
    for i in range(20):
        rows.append({
            "date": f"2026-05-{i+1:02d}",
            "day_strain": float(i),
            "recovery_score": 100.0 - i,  # higher strain day -> lower next recovery
            "user_calibrating": 0,
        })
    out = analytics.strain_recovery_balance(rows)
    assert len(out) == 4
    # Q1 (low strain) should have higher mean next-day recovery than Q4.
    assert out[0]["mean_next_recovery"] > out[3]["mean_next_recovery"]


def test_correlation_matrix_shape():
    rows = []
    for i in range(15):
        rows.append({
            "date": f"2026-05-{i+1:02d}",
            "day_strain": float(i % 7),
            "hours_of_sleep": 7.0,
            "sleep_perf_pct": 80.0,
            "sleep_consistency_pct": 75.0,
            "bedtime_hour": 23.0,
            "respiratory_rate": 15.0,
            "recovery_score": 60.0 + (i % 5),
            "hrv_rmssd_ms": 55.0,
            "user_calibrating": 0,
            "interventions": [],
        })
    matrix = analytics.correlation_matrix(rows, items=[])
    assert "recovery_score" in matrix and "hrv_rmssd_ms" in matrix
    assert "day_strain" in matrix["recovery_score"]
