"""Whoop adapter — body / recovery / sleep (PENDING DEVICE).

Whoop v2 API (OAuth2): /v1/recovery, /v1/activity/sleep, /v1/cycle, /v1/user/measurement/body.
The official API is the reason Whoop is the body spine. Writes life.body_daily.
"""
import datetime as dt


def normalize(recovery, sleep):
    r = recovery["score"]; s = sleep["score"]
    return {"life.body_daily": [{
        "day": dt.date.today().isoformat(),
        "recovery": round(r["recovery_score"]),
        "hrv": r["hrv_rmssd_milli"], "resting_hr": r["resting_heart_rate"],
        "strain": recovery.get("strain"),
        "sleep_hours": round(s["stage_summary"]["total_in_bed_time_milli"] / 3.6e6, 2),
        "sleep_perf": round(s["sleep_performance_percentage"]),
        "sleep_consistency": round(s.get("sleep_consistency_percentage", 0)),
    }]}


def pull(cfg):
    raise NotImplementedError("buy Whoop, authorize OAuth, map endpoints → normalize()")
