"""Pure-Python statistics over the daily view.

No numpy/pandas dependency at runtime — these are small daily series. The
workbook recomputes most of this live with Excel formulas (=AVERAGE, =STDEV,
=CORREL, etc.); the functions here back the tests and any Python-side summary.

All functions accept the daily list (newest-first, as produced by transform)
and internally sort chronologically where order matters.
"""

from __future__ import annotations

import math
from typing import Optional, Sequence

import config

# Metrics tracked for rolling/baseline/z-score analysis.
METRICS = [
    "recovery_score",
    "hrv_rmssd_ms",
    "resting_hr",
    "day_strain",
    "hours_of_sleep",
    "sleep_perf_pct",
]

NAN = float("nan")


def _clean(values: Sequence[Optional[float]]) -> list[float]:
    return [float(v) for v in values if isinstance(v, (int, float))]


def mean(values: Sequence[Optional[float]]) -> float:
    xs = _clean(values)
    return sum(xs) / len(xs) if xs else NAN


def stdev(values: Sequence[Optional[float]]) -> float:
    """Sample standard deviation (n-1). NaN if fewer than 2 points."""
    xs = _clean(values)
    if len(xs) < 2:
        return NAN
    m = sum(xs) / len(xs)
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return math.sqrt(var)


def pearson(xs: Sequence[Optional[float]], ys: Sequence[Optional[float]], min_n: int = 5):
    """Pearson r over paired, non-null samples. Returns (r, n).

    Guards n<min_n (returns (NaN, n)) and zero-variance (returns (NaN, n)).
    """
    pairs = [
        (float(x), float(y))
        for x, y in zip(xs, ys)
        if isinstance(x, (int, float)) and isinstance(y, (int, float))
    ]
    n = len(pairs)
    if n < min_n:
        return NAN, n
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    sxy = sum((x - mx) * (y - my) for x, y in pairs)
    sxx = sum((x - mx) ** 2 for x, _ in pairs)
    syy = sum((y - my) ** 2 for _, y in pairs)
    if sxx == 0 or syy == 0:
        return NAN, n
    return sxy / math.sqrt(sxx * syy), n


def linear_slope(values: Sequence[Optional[float]]) -> float:
    """OLS slope of values vs index 0..n-1 (per-day trend). NaN if n<2."""
    ys = _clean(values)
    n = len(ys)
    if n < 2:
        return NAN
    xs = list(range(n))
    mx = sum(xs) / n
    my = sum(ys) / n
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return NAN
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom


def _chrono(daily: list[dict]) -> list[dict]:
    return sorted(daily, key=lambda r: r["date"])


def baseline(daily: list[dict], metric: str, window: int = 30) -> float:
    """30-day rolling mean of the latest day, excluding calibrating days."""
    chrono = _chrono(daily)
    recent = chrono[-window:]
    vals = [r.get(metric) for r in recent if not r.get("user_calibrating")]
    return mean(vals)


def rolling_table(daily: list[dict]) -> list[dict]:
    """Per-day 7d/30d mean & SD, baseline, and z-score for each metric.

    Returned newest-first to match the Daily tab ordering.
    """
    chrono = _chrono(daily)
    out = []
    for i, row in enumerate(chrono):
        window7 = chrono[max(0, i - 6): i + 1]
        window30 = chrono[max(0, i - 29): i + 1]
        entry = {"date": row["date"]}
        for m in METRICS:
            v7 = [r.get(m) for r in window7]
            v30 = [r.get(m) for r in window30]
            base_vals = [r.get(m) for r in window30 if not r.get("user_calibrating")]
            base = mean(base_vals)
            sd30 = stdev(v30)
            val = row.get(m)
            z = NAN
            if isinstance(val, (int, float)) and not math.isnan(base) and not math.isnan(sd30) and sd30 != 0:
                z = (val - base) / sd30
            entry[m] = {
                "mean7": mean(v7),
                "sd7": stdev(v7),
                "mean30": mean(v30),
                "sd30": sd30,
                "baseline": base,
                "z": z,
            }
        out.append(entry)
    out.reverse()
    return out


def anomalies_today(daily: list[dict]) -> list[dict]:
    """Metrics whose latest |z| >= threshold (config.Z_ANOMALY)."""
    table = rolling_table(daily)
    if not table:
        return []
    latest = table[0]
    flags = []
    for m in METRICS:
        z = latest[m]["z"]
        if isinstance(z, float) and not math.isnan(z) and abs(z) >= config.Z_ANOMALY:
            flags.append({"metric": m, "z": round(z, 2)})
    return flags


def hrv_trend_slope(daily: list[dict], window: int = 7) -> float:
    """7-day slope of HRV (chronological)."""
    chrono = _chrono(daily)[-window:]
    return linear_slope([r.get("hrv_rmssd_ms") for r in chrono])


def strain_recovery_balance(daily: list[dict]) -> list[dict]:
    """Bucket today's day_strain into quartiles; report mean NEXT-day recovery.

    Pairs day d strain with day d+1 recovery.
    """
    chrono = _chrono(daily)
    pairs = []
    for i in range(len(chrono) - 1):
        strain = chrono[i].get("day_strain")
        next_rec = chrono[i + 1].get("recovery_score")
        if isinstance(strain, (int, float)) and isinstance(next_rec, (int, float)):
            pairs.append((float(strain), float(next_rec)))
    if len(pairs) < 4:
        return []

    strains = sorted(p[0] for p in pairs)

    def q(frac: float) -> float:
        idx = frac * (len(strains) - 1)
        lo = int(math.floor(idx))
        hi = int(math.ceil(idx))
        if lo == hi:
            return strains[lo]
        return strains[lo] + (strains[hi] - strains[lo]) * (idx - lo)

    edges = [q(0.0), q(0.25), q(0.5), q(0.75), q(1.0)]
    buckets = [[], [], [], []]
    for strain, next_rec in pairs:
        for b in range(4):
            lo, hi = edges[b], edges[b + 1]
            if (strain >= lo and strain < hi) or (b == 3 and strain <= hi):
                buckets[b].append(next_rec)
                break
    labels = ["Q1 (low strain)", "Q2", "Q3", "Q4 (high strain)"]
    out = []
    for b in range(4):
        out.append(
            {
                "bucket": labels[b],
                "strain_range": (round(edges[b], 1), round(edges[b + 1], 1)),
                "mean_next_recovery": round(mean(buckets[b]), 1) if buckets[b] else NAN,
                "n": len(buckets[b]),
            }
        )
    return out


def correlation_matrix(daily: list[dict], items: Optional[list[str]] = None) -> dict:
    """Pearson r (and n) of prior-day predictors vs next-morning recovery & HRV.

    Predictors are taken from day d; outcomes from day d+1. Intervention items
    become 0/1 daily flags. Guards n<5 (returns NaN).
    """
    chrono = _chrono(daily)
    items = items or []

    predictors = [
        "day_strain",
        "hours_of_sleep",
        "sleep_perf_pct",
        "sleep_consistency_pct",
        "bedtime_hour",
        "respiratory_rate",
    ] + [f"flag::{it}" for it in items]

    def value(row: dict, key: str):
        if key.startswith("flag::"):
            item = key[len("flag::"):]
            present = any(iv.get("item") == item for iv in row.get("interventions", []))
            return 1.0 if present else 0.0
        return row.get(key)

    out: dict[str, dict] = {}
    for outcome in ("recovery_score", "hrv_rmssd_ms"):
        col = {}
        for pred in predictors:
            xs = [value(chrono[i], pred) for i in range(len(chrono) - 1)]
            ys = [chrono[i + 1].get(outcome) for i in range(len(chrono) - 1)]
            r, n = pearson(xs, ys)
            col[pred] = {"r": r, "n": n}
        out[outcome] = col
    return out


def training_load(daily: list[dict]) -> dict:
    """7-day training monotony (mean strain / SD strain) and weekly load (sum)."""
    chrono = _chrono(daily)[-7:]
    strains = [r.get("day_strain") for r in chrono]
    m = mean(strains)
    sd = stdev(strains)
    monotony = m / sd if (not math.isnan(m) and not math.isnan(sd) and sd != 0) else NAN
    load = sum(_clean(strains))
    return {"monotony": monotony, "weekly_load": load, "mean_strain": m, "sd_strain": sd}
