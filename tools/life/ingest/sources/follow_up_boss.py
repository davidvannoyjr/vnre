"""Follow Up Boss adapter — prospecting + production layer (PENDING CONNECTION).

THE #1 Phase-1.5 task. Not connected in the web session, so the dashboard's manual Daily Log
feeds life.prospecting_daily until this is wired. FUB API: https://api.followupboss.com/v1
  /events            → calls, texts, appointments (set/kept)
  /people, /deals    → database coverage, pipeline
Auth: HTTP Basic with the FUB API key (lives in Drive: fub-api-key.local.md — never committed).

When enabled, this REPLACES the 'manual' source for a day; the dashboard already blends
manual + FUB and prefers FUB when present.
"""
import datetime as dt


def normalize(events, day=None):
    day = day or dt.date.today().isoformat()
    calls = sum(1 for e in events if e.get("type") == "Calls")
    contacts = sum(1 for e in events if e.get("type") == "Calls" and e.get("outcome") == "Connected")
    appts_set = sum(1 for e in events if e.get("type") == "Appointments")
    appts_kept = sum(1 for e in events if e.get("type") == "Appointments" and e.get("outcome") == "Met")
    return {"life.prospecting_daily": [{
        "day": day, "calls": calls, "contacts": contacts,
        "appts_set": appts_set, "appts_kept": appts_kept, "source": "fub",
    }]}


def pull(cfg):
    raise NotImplementedError("connect FUB MCP / API key, then map /events → normalize()")
