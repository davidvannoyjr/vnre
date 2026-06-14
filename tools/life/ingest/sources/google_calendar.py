"""Google Calendar adapter — time-structure layer (LIVE).

Pulls events and tags each into a time category so the dashboard can show block adherence
and revenue-producing %. Keyword rules below are tuned to DVN's calendar conventions
(LA: = listing appointment, LIFT/DRIVE/Focus, etc.).
"""
import datetime as dt

CATEGORY_RULES = [
    ("appointment", ("la:", "appt", "listing appointment", "showing", "buyer")),
    ("prospecting", ("prospect", "calls", "dial", "circle", "expired", "fsbo")),
    ("workout",     ("lift", "gym", "run", "workout", "train")),
    ("coaching",    ("coach", "1:1", "client call")),
    ("personal",    ("drive", "check out", "out of office", "lunch", "family")),
    ("admin",       ("focus", "email", "admin", "plan")),
]


def categorize(summary, event_type):
    s = (summary or "").lower()
    for cat, kws in CATEGORY_RULES:
        if any(k in s for k in kws):
            return cat
    if event_type == "FOCUS_TIME":
        return "admin"
    if event_type == "OUT_OF_OFFICE":
        return "personal"
    return "admin"


def normalize(events):
    rows = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date"))
        end = e["end"].get("dateTime", e["end"].get("date"))
        rows.append({
            "id": e["id"],
            "starts_at": start,
            "ends_at": end,
            "summary": e.get("summary", ""),
            "event_type": e.get("eventType", "DEFAULT"),
            "category": categorize(e.get("summary"), e.get("eventType")),
        })
    return {"life.calendar_events": rows}


def pull(cfg):
    # from googleapiclient.discovery import build (service account creds)
    # today window → events.list(calendarId=cfg['calendar_id'], timeMin=, timeMax=)
    raise NotImplementedError("wire Google Calendar API; normalize() defines the target shape")
