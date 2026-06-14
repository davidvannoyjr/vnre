"""macro-log adapter — diet (PENDING SKILL).

No external API. The `macro-log` Claude skill writes life.diet_entries directly when DVN
texts/photos a meal ("had 6oz salmon + rice" → Claude estimates → upsert). This adapter only
rolls today's entries into life.metrics_daily for the dashboard.
"""
import datetime as dt


def rollup(entries):
    day = dt.date.today().isoformat()
    cal = sum(e["calories"] for e in entries)
    pro = sum(e["protein_g"] for e in entries)
    return {"life.metrics_daily": [
        {"day": day, "domain": "body", "metric": "calories", "value": cal, "target": 2200},
        {"day": day, "domain": "body", "metric": "protein_g", "value": pro, "target": 180},
    ]}


def pull(cfg):
    raise NotImplementedError("build the macro-log skill; it writes life.diet_entries, this rolls it up")
