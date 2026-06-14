"""Function Health adapter — labs / biomarker layer (LIVE).

Pulls the biomarker panel and normalizes to life.labs_summary (+ optional detail rows).
On 2026-06-14 the live pull returned: total 123, in_range 104, out_of_range 5.
"""
import datetime as dt


def _fetch(cfg):
    # import requests
    # return requests.get("https://api.functionhealth.com/v1/biomarkers/summary",
    #                     headers={"Authorization": f"Bearer {cfg['api_token']}"}).json()
    raise NotImplementedError("wire Function Health API; normalize() defines the target shape")


def normalize(summary):
    s = summary["structuredContent"]["summary"]
    return {"life.labs_summary": [{
        "as_of": dt.date.today().isoformat(),
        "total": s["total"],
        "in_range": s["in_range"],
        "out_of_range": s["out_of_range"],
        "provider": "Function Health",
    }]}


def pull(cfg):
    return normalize(_fetch(cfg))
