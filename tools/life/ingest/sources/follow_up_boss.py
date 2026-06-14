"""Follow Up Boss adapter — prospecting + conversion layer.

THE Phase-1.5 source. Pulls calls + appointments from the FUB REST API and normalizes to
life.prospecting_daily (calls, contacts reached, appts set, appts kept). The dashboard already
blends manual + FUB and prefers FUB when a day has it, so wiring this flips prospecting from
hand-logged to automatic with zero dashboard changes.

API: https://api.followupboss.com/v1  ·  Auth: HTTP Basic (api_key as username, blank password).
Key lives in Drive (`fub-api-key.local.md`) — never committed. Pass via config or FUB_API_KEY.

Counting rules (documented so they're auditable, tune to DVN's FUB conventions):
  • calls        = every logged call created on the day
  • contacts     = calls whose outcome means a live conversation (see CONNECTED_OUTCOMES)
  • appts_set    = appointments CREATED on the day (booked)
  • appts_kept   = appointments whose START is on the day AND outcome is a "met" outcome
"""
import argparse, datetime as dt, json, os, sys

BASE = "https://api.followupboss.com/v1"
CONNECTED_OUTCOMES = {"Interested", "Not Interested", "Connected", "Talked", "Appointment Set"}
KEPT_OUTCOMES = {"Met", "Completed", "Showed"}


def _get(path, key, params=None):
    """GET a FUB collection, following pagination. Returns the concatenated list of records."""
    import requests
    out, offset = [], 0
    params = dict(params or {})
    while True:
        params.update({"limit": 100, "offset": offset})
        r = requests.get(f"{BASE}/{path}", auth=(key, ""), params=params,
                         headers={"Accept": "application/json"})
        r.raise_for_status()
        body = r.json()
        records = body.get(path, body.get("data", []))
        out.extend(records)
        meta = body.get("_metadata", {})
        if not records or len(out) >= meta.get("total", len(out)) or len(records) < 100:
            break
        offset += 100
    return out


def _on_day(ts, day):
    """True if an ISO timestamp falls on `day` (YYYY-MM-DD)."""
    return bool(ts) and ts[:10] == day


def normalize(calls, appts, day):
    calls_d = [c for c in calls if _on_day(c.get("created"), day)]
    contacts = [c for c in calls_d if c.get("outcome") in CONNECTED_OUTCOMES]
    appts_set = [a for a in appts if _on_day(a.get("created"), day)]
    appts_kept = [a for a in appts
                  if _on_day(a.get("start"), day) and a.get("outcome") in KEPT_OUTCOMES]
    return {"life.prospecting_daily": [{
        "day": day,
        "calls": len(calls_d),
        "contacts": len(contacts),
        "appts_set": len(appts_set),
        "appts_kept": len(appts_kept),
        "source": "fub",
    }]}


def pull(cfg, day=None):
    key = cfg.get("api_key") or os.environ.get("FUB_API_KEY")
    if not key:
        raise RuntimeError("no FUB api_key — set it in config.json or FUB_API_KEY")
    day = day or dt.date.today().isoformat()
    calls = _get("calls", key)
    appts = _get("appointments", key)
    return normalize(calls, appts, day)


if __name__ == "__main__":  # standalone backfill / smoke test
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--key", default=os.environ.get("FUB_API_KEY"))
    a = ap.parse_args()
    if not a.key:
        sys.exit("pass --key or set FUB_API_KEY")
    print(json.dumps(pull({"api_key": a.key}, a.date), indent=2))
