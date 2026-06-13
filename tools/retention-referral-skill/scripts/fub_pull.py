#!/usr/bin/env python3
"""
fub_pull.py — Follow Up Boss pull for the VNRE retention/referral engine.

Self-contained. Talks directly to the Follow Up Boss v1 REST API and emits the
contact schema that build_retention_brief.py consumes. No third party, no MCP
helper — runs anywhere with network + the API key (DVN's Mac, a cron box, etc.).

What it assembles per contact (Past Client + Sphere segments):
  id, firstName, lastName, address, city, tags, stage,
  closeDate, salePrice            <- most-recent WON deal
  lastContactDate                 <- max across calls/texts/emails/notes (bulk, scalable)
  recentPropertyViewDate          <- most-recent property-view event  (active-move signal)
  mortgageRate, birthday,         <- person custom fields (optional; sharpen moments)
  preferredChannel, lifetimeValue

Auth: HTTP Basic, API key as username, blank password, plus the registered
X-System / X-System-Key headers (higher rate limits — the "VNRE-Claude" system).

Config: pass --config config.json (see config.example.json). The API key is read
from FUB_API_KEY env var or the `apiKeyFile` path — never hardcode or commit it.

Usage:
  FUB_API_KEY=xxx python3 fub_pull.py --config config.json --out _data/retention-pull-2026-06-13.json
  python3 fub_pull.py --selftest        # verify assembly logic offline, no network
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta

BASE = "https://api.followupboss.com/v1"


# --------------------------------------------------------------- tiny helpers
def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def iso(s):
    """Normalize a FUB timestamp to YYYY-MM-DD, or None."""
    if not s:
        return None
    s = str(s)
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else None

def max_date(a, b):
    return max([x for x in (a, b) if x], default=None)


# --------------------------------------------------------------- API client
class FUB:
    def __init__(self, api_key, x_system=None, x_system_key=None, verbose=True):
        token = base64.b64encode(f"{api_key}:".encode()).decode()
        self.headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}
        if x_system:
            self.headers["X-System"] = x_system
        if x_system_key:
            self.headers["X-System-Key"] = x_system_key
        self.verbose = verbose

    def _get(self, path, params):
        url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
        for attempt in range(5):
            req = urllib.request.Request(url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                if e.code == 429:                      # rate limited — back off
                    wait = int(e.headers.get("Retry-After", 2 ** attempt))
                    time.sleep(wait)
                    continue
                raise
            except urllib.error.URLError:
                time.sleep(2 ** attempt)
        raise RuntimeError(f"FUB GET failed after retries: {path}")

    def paginate(self, path, params, collection, stop_before=None, date_field="created", limit=100):
        """Yield records page by page. If stop_before (YYYY-MM-DD) is set and records
        are sorted newest-first, stop once we pass it (keeps comm pulls cheap)."""
        offset = 0
        while True:
            page = self._get(path, {**params, "limit": limit, "offset": offset})
            items = page.get(collection, [])
            if not items:
                return
            for it in items:
                if stop_before and iso(it.get(date_field)) and iso(it.get(date_field)) < stop_before:
                    return
                yield it
            meta = page.get("_metadata", {})
            if len(items) < limit or not meta.get("next") and (offset + limit) >= meta.get("total", 0):
                return
            offset += limit


# --------------------------------------------------------------- assembly (pure, testable)
def index_deals(deals):
    """personId -> {closeDate, salePrice, address, city} from the most-recent WON deal."""
    by_person = {}
    for d in deals:
        if str(d.get("status", "")).lower() not in ("won", "closed", "sold"):
            continue
        close = iso(d.get("closedDate") or d.get("projectedCloseDate") or d.get("closeDate"))
        price = d.get("price") or d.get("value") or d.get("salePrice")
        addr = (d.get("address") or {}) if isinstance(d.get("address"), dict) else {}
        rec = {"closeDate": close, "salePrice": price,
               "address": addr.get("street") or d.get("propertyAddress"),
               "city": addr.get("city") or d.get("propertyCity")}
        for p in d.get("people", []) or ([{"id": d.get("personId")}] if d.get("personId") else []):
            pid = str(p.get("id"))
            cur = by_person.get(pid)
            if not cur or (close and (not cur["closeDate"] or close > cur["closeDate"])):
                by_person[pid] = rec
    return by_person

def index_last_contact(comm_records):
    """personId -> latest communication date across all comm types."""
    out = {}
    for c in comm_records:
        pid = str(c.get("personId") or (c.get("people") or [{}])[0].get("id"))
        d = iso(c.get("created") or c.get("date"))
        if pid and d:
            out[pid] = max_date(out.get(pid), d)
    return out

def index_property_views(events):
    """personId -> latest property-view event date."""
    out = {}
    for e in events:
        etype = (e.get("type") or "") + " " + (e.get("description") or "")
        if "propert" not in etype.lower() and "view" not in etype.lower():
            continue
        pid = str(e.get("personId") or (e.get("person") or {}).get("id"))
        d = iso(e.get("created") or e.get("occurred"))
        if pid and d:
            out[pid] = max_date(out.get(pid), d)
    return out

def cf(person, *names):
    """Read a FUB person custom field by any of several display names."""
    for n in names:
        for key in (n, "customField" + n.replace(" ", ""), n.replace(" ", "")):
            if person.get(key) not in (None, ""):
                return person.get(key)
        for cfv in person.get("customFields", []) or []:
            if norm(cfv.get("name")) == norm(n) and cfv.get("value") not in (None, ""):
                return cfv.get("value")
    return None

def assemble(people, deals_idx, last_idx, views_idx):
    """Join everything into the engine's contact schema. Pure — unit-testable."""
    out = []
    for p in people:
        pid = str(p.get("id"))
        deal = deals_idx.get(pid, {})
        addr0 = (p.get("addresses") or [{}])[0]
        rate = cf(p, "Mortgage Rate", "Rate")
        clv = cf(p, "Lifetime Value", "Lifetime Commission", "CLV")
        out.append({
            "id": pid,
            "firstName": p.get("firstName"), "lastName": p.get("lastName"),
            "name": p.get("name"),
            "address": deal.get("address") or addr0.get("street"),
            "city": deal.get("city") or addr0.get("city"),
            "tags": p.get("tags", []), "stage": p.get("stage"),
            "email": (p.get("emails") or [{}])[0].get("value"),
            "closeDate": deal.get("closeDate") or cf(p, "Closing Date", "Close Date"),
            "salePrice": deal.get("salePrice") or cf(p, "Sale Price", "Purchase Price"),
            "lastContactDate": last_idx.get(pid),
            "recentPropertyViewDate": views_idx.get(pid),
            "mortgageRate": float(rate) if rate and str(rate).replace(".", "").isdigit() else None,
            "birthday": cf(p, "Birthday", "Birth Date"),
            "preferredChannel": cf(p, "Preferred Channel", "Best Contact Method"),
            "lifetimeValue": float(re.sub(r"[^0-9.]", "", str(clv))) if clv else None,
        })
    return out


# --------------------------------------------------------------- live pull
def run(config, out_path):
    key = os.environ.get("FUB_API_KEY") or (
        open(os.path.expanduser(config["apiKeyFile"])).read().strip()
        if config.get("apiKeyFile") else None)
    if not key:
        sys.exit("No API key. Set FUB_API_KEY or config.apiKeyFile.")
    # the key file is markdown — grab the first token that looks like a key
    key = re.search(r"[A-Za-z0-9]{20,}", key).group(0) if len(key) > 60 else key

    api = FUB(key, config.get("xSystem"), config.get("xSystemKey"))
    since = (date.today() - timedelta(days=config.get("commLookbackDays", 1095))).isoformat()

    people = []
    for seg in config["segments"]:                      # by stage and/or tag
        params = {"sort": "name"}
        if seg.get("stage"):
            params["stage"] = seg["stage"]
        if seg.get("tag"):
            params["tags"] = seg["tag"]
        params["fields"] = "allFields"
        people += list(api.paginate("people", params, "people"))

    deals = list(api.paginate("deals", {}, "deals"))
    comms = []
    for path in ("calls", "textMessages", "emails", "notes"):
        comms += list(api.paginate(path, {"sort": "-created"}, path, stop_before=since))
    events = list(api.paginate("events", {"sort": "-created"}, "events", stop_before=since))

    contacts = assemble(people, index_deals(deals), index_last_contact(comms),
                        index_property_views(events))
    json.dump({"pulledAt": datetime.now().isoformat(), "count": len(contacts),
               "contacts": contacts}, open(out_path, "w"), indent=2)
    print(f"pulled {len(contacts)} contacts -> {out_path}")


# --------------------------------------------------------------- offline self-test
def selftest():
    people = [{"id": 1, "firstName": "Andrew", "lastName": "Edwards", "stage": "Past Client",
               "tags": ["Past Client"], "addresses": [{"street": "16408 Riggs Rd", "city": "Stilwell"}],
               "customFields": [{"name": "Mortgage Rate", "value": "7.5"},
                                {"name": "Lifetime Value", "value": "$18,500"}]}]
    deals = [{"status": "Won", "closedDate": "2021-06-10T00:00:00Z", "price": 400000,
              "people": [{"id": 1}]}]
    comms = [{"personId": 1, "created": "2026-01-01T10:00:00Z"},
             {"personId": 1, "created": "2025-09-01T10:00:00Z"}]
    events = [{"personId": 1, "type": "Property Viewed", "created": "2026-06-01T08:00:00Z"}]
    got = assemble(people, index_deals(deals), index_last_contact(comms), index_property_views(events))[0]
    assert got["closeDate"] == "2021-06-10", got
    assert got["salePrice"] == 400000, got
    assert got["lastContactDate"] == "2026-01-01", got          # newest of the two
    assert got["recentPropertyViewDate"] == "2026-06-01", got
    assert got["mortgageRate"] == 7.5, got
    assert got["lifetimeValue"] == 18500.0, got
    assert got["address"] == "16408 Riggs Rd", got
    print("selftest OK — assembly joins deals, comms, events, and custom fields correctly")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.config or not args.out:
        sys.exit("need --config and --out (or --selftest)")
    run(json.load(open(args.config)), args.out)


if __name__ == "__main__":
    main()
