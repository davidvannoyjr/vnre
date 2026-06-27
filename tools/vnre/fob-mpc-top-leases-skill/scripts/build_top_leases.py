#!/usr/bin/env python3
"""
build_top_leases.py — FOB MPC Check: top 3 lease listings this week.

Pulls FUB deals tagged/typed as lease listings, filters to the current week
(Monday–Sunday), ranks by list price (desc), and surfaces the top N.

MPC = Market Pulse Check — a fast, on-demand snapshot of lease pipeline activity.

Usage:
  FUB_API_KEY=xxx python3 build_top_leases.py --config config.json --out "YYYY-MM-DD MPC Top Leases.md"
  python3 build_top_leases.py --selftest
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
from datetime import date, timedelta

BASE = "https://api.followupboss.com/v1"

# ─── tunable constants (also settable via config.json) ────────────────
TOP_N = 3
DEFAULT_LEASE_TYPES = ["Lease", "Rental", "Lease Listing"]
DEFAULT_ACTIVE_STAGES = ["Active", "Active KO", "Coming Soon", "New"]
# ──────────────────────────────────────────────────────────────────────


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def iso(s):
    if not s:
        return None
    m = re.match(r"(\d{4}-\d{2}-\d{2})", str(s))
    return m.group(1) if m else None


def week_window(today=None):
    """Return (monday_iso, sunday_iso) for the week containing today."""
    d = today or date.today()
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday.isoformat(), sunday.isoformat()


# ─── FUB API client ───────────────────────────────────────────────────
class FUB:
    def __init__(self, api_key, x_system=None, x_system_key=None):
        token = base64.b64encode(f"{api_key}:".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {token}",
            "Content-Type": "application/json",
        }
        if x_system:
            self.headers["X-System"] = x_system
        if x_system_key:
            self.headers["X-System-Key"] = x_system_key

    def _get(self, path, params):
        url = f"{BASE}/{path}?{urllib.parse.urlencode(params)}"
        for attempt in range(5):
            req = urllib.request.Request(url, headers=self.headers)
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    wait = int(e.headers.get("Retry-After", 2 ** attempt))
                    time.sleep(wait)
                    continue
                raise
            except urllib.error.URLError:
                time.sleep(2 ** attempt)
        raise RuntimeError(f"FUB GET failed after retries: {path}")

    def paginate(self, path, params, collection, limit=100):
        offset = 0
        while True:
            page = self._get(path, {**params, "limit": limit, "offset": offset})
            items = page.get(collection, [])
            if not items:
                return
            yield from items
            meta = page.get("_metadata", {})
            total = meta.get("total", 0)
            if len(items) < limit or (offset + limit) >= total:
                return
            offset += limit


# ─── core logic (pure, testable) ──────────────────────────────────────
def is_lease(deal, lease_types, active_stages):
    """Return True if this deal is an active lease listing."""
    deal_type = norm(deal.get("type") or deal.get("pipeline") or deal.get("pipelineName") or "")
    stage = norm(deal.get("stage") or "")
    tags = [norm(t) for t in (deal.get("tags") or [])]

    type_match = any(norm(lt) in deal_type or deal_type in norm(lt) for lt in lease_types)
    tag_match = any(norm(lt) in tags for lt in lease_types)
    stage_ok = (not active_stages) or any(
        norm(s) in stage or stage in norm(s) for s in active_stages
    )
    return (type_match or tag_match) and stage_ok


def parse_price(deal):
    raw = deal.get("price") or deal.get("value") or deal.get("monthlyRent") or 0
    if isinstance(raw, (int, float)):
        return float(raw)
    cleaned = re.sub(r"[^0-9.]", "", str(raw))
    return float(cleaned) if cleaned else 0.0


def parse_address(deal):
    addr = deal.get("address")
    if isinstance(addr, dict):
        parts = [addr.get("street"), addr.get("city"), addr.get("state")]
        return ", ".join(p for p in parts if p)
    return str(addr or deal.get("propertyAddress") or deal.get("name") or "Unknown address")


def contact_name(deal):
    people = deal.get("people") or []
    if people:
        p = people[0]
        return p.get("name") or f"{p.get('firstName', '')} {p.get('lastName', '')}".strip()
    return deal.get("personName") or "—"


def filter_this_week(deals, monday, sunday):
    out = []
    for d in deals:
        created = iso(d.get("created"))
        updated = iso(d.get("updated"))
        relevant = max([x for x in (created, updated) if x], default=None)
        if relevant and monday <= relevant <= sunday:
            out.append(d)
    return out


def rank_leases(deals, lease_types, active_stages, monday, sunday, top_n=TOP_N):
    candidates = [d for d in deals if is_lease(d, lease_types, active_stages)]
    this_week = filter_this_week(candidates, monday, sunday)
    ranked = sorted(
        this_week,
        key=lambda d: (parse_price(d), iso(d.get("created")) or ""),
        reverse=True,
    )
    return ranked[:top_n]


def fmt_price(price):
    return f"${price:,.0f}/mo" if price else "—"


def render_brief(leases, monday, sunday, today_str):
    lines = [
        "# FOB MPC Check — Top Lease Listings",
        f"Week of {monday} → {sunday}  |  Run {today_str}",
        "",
    ]
    if not leases:
        lines += ["No lease listings entered or updated in FUB this week.", ""]
        return "\n".join(lines)

    for i, d in enumerate(leases, 1):
        addr = parse_address(d)
        price = parse_price(d)
        created = iso(d.get("created")) or "—"
        stage = d.get("stage") or "—"
        client = contact_name(d)
        notes = (d.get("description") or d.get("notes") or "").strip()[:120]

        lines += [f"## #{i} — {addr}"]
        lines += [f"**Price:** {fmt_price(price)}  |  **Listed:** {created}  |  **Stage:** {stage}"]
        lines += [f"**Client:** {client}"]
        if notes:
            lines += [f"**Notes:** {notes}"]
        lines += [""]

    lines += [
        "---",
        f"*{len(leases)} lease listing(s) surfaced · FOB MPC Check*",
    ]
    return "\n".join(lines)


# ─── live run ─────────────────────────────────────────────────────────
def run(config, out_path, today=None):
    key = os.environ.get("FUB_API_KEY") or (
        open(os.path.expanduser(config["apiKeyFile"])).read().strip()
        if config.get("apiKeyFile") else None
    )
    if not key:
        sys.exit("No API key. Set FUB_API_KEY or config.apiKeyFile.")
    key = re.search(r"[A-Za-z0-9]{20,}", key).group(0) if len(key) > 60 else key

    lease_types = config.get("leaseTypes", DEFAULT_LEASE_TYPES)
    active_stages = config.get("activeStages", DEFAULT_ACTIVE_STAGES)
    top_n = config.get("topN", TOP_N)

    today_d = date.fromisoformat(today) if today else date.today()
    monday, sunday = week_window(today_d)

    api = FUB(key, config.get("xSystem"), config.get("xSystemKey"))
    deals = list(api.paginate("deals", {"sort": "-created"}, "deals"))
    print(f"pulled {len(deals)} deals from FUB")

    leases = rank_leases(deals, lease_types, active_stages, monday, sunday, top_n)
    brief = render_brief(leases, monday, sunday, today_d.isoformat())

    open(out_path, "w").write(brief)
    print(f"top {len(leases)} lease listing(s) -> {out_path}")
    return leases


# ─── offline self-test ────────────────────────────────────────────────
def selftest():
    today = date(2026, 6, 26)
    monday, sunday = week_window(today)
    assert monday == "2026-06-22", monday
    assert sunday == "2026-06-28", sunday

    deals = [
        {
            "id": 1, "type": "Lease", "stage": "Active", "price": 2200,
            "created": "2026-06-23T10:00:00Z",
            "address": {"street": "4400 Oak St", "city": "Overland Park"},
            "people": [{"name": "Sarah Kim"}], "description": "2BR/2BA, updated kitchen",
        },
        {
            "id": 2, "type": "Lease Listing", "stage": "Coming Soon", "price": 1850,
            "created": "2026-06-24T08:00:00Z",
            "address": {"street": "210 Main Ave", "city": "Olathe"},
            "people": [{"name": "Marcus Webb"}],
        },
        {
            "id": 3, "type": "Lease", "stage": "Active", "price": 2800,
            "created": "2026-06-25T15:00:00Z",
            "address": {"street": "7700 Roe Ave", "city": "Prairie Village"},
            "people": [{"name": "Jennifer Park"}], "description": "3BR corner unit, new appliances",
        },
        {
            "id": 4, "type": "Sale", "stage": "Active", "price": 450000,
            "created": "2026-06-25T12:00:00Z",
            "address": {"street": "999 Seller Lane", "city": "Leawood"},
            "people": [{"name": "Bob Buyer"}],
        },
        {
            "id": 5, "type": "Lease", "stage": "Active", "price": 1500,
            "created": "2026-06-10T12:00:00Z",   # prior week — excluded
            "address": {"street": "Old Deal Rd", "city": "KC"},
        },
    ]

    leases = rank_leases(deals, DEFAULT_LEASE_TYPES, DEFAULT_ACTIVE_STAGES, monday, sunday)
    assert len(leases) == 3, f"expected 3, got {len(leases)}"
    assert leases[0]["id"] == 3, f"expected highest-price first (id=3), got {leases[0]['id']}"
    assert leases[1]["id"] == 1, f"expected id=1 second, got {leases[1]['id']}"
    assert leases[2]["id"] == 2, f"expected id=2 third, got {leases[2]['id']}"

    # sale deal excluded
    assert all(d["id"] != 4 for d in leases), "sale deal must not appear"
    # prior-week lease excluded
    assert all(d["id"] != 5 for d in leases), "prior-week lease must not appear"

    brief = render_brief(leases, monday, sunday, "2026-06-26")
    assert "7700 Roe Ave" in brief
    assert "$2,800/mo" in brief
    assert "FOB MPC Check" in brief
    assert "#1" in brief

    # empty week
    empty = render_brief([], monday, sunday, "2026-06-26")
    assert "No lease listings" in empty

    print("selftest OK — filter, rank, and render all pass")


def main():
    ap = argparse.ArgumentParser(description="FOB MPC Check — top lease listings this week")
    ap.add_argument("--config", help="Path to config.json")
    ap.add_argument("--out", help="Output path for the brief (.md)")
    ap.add_argument("--today", help="Override today's date (YYYY-MM-DD) for testing")
    ap.add_argument("--selftest", action="store_true", help="Run offline tests and exit")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.config or not args.out:
        sys.exit("need --config and --out  (or --selftest)")
    run(json.load(open(args.config)), args.out, args.today)


if __name__ == "__main__":
    main()
