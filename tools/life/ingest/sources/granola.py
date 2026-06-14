"""Granola adapter — call/meeting quality (LIVE).

Counts meetings and (when paired with the vnre-call-coach skill) feeds script-adherence
scores. Live pull 2026-06-14: 0 meetings this week.
"""
import datetime as dt


def normalize(meetings):
    return {"life.metrics_daily": [{
        "day": dt.date.today().isoformat(), "domain": "biz",
        "metric": "calls_scored_week", "value": len(meetings), "target": None,
    }]}


def pull(cfg):
    raise NotImplementedError("wire Granola API; normalize() defines the target shape")
