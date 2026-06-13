#!/usr/bin/env python3
"""
build_clv.py — VNRE client Lifetime Value, from the correct source.

QuickBooks "sales by customer" is VNRE's B2B *partner* income (mortgage, title,
insurance, co-op brokers) — NOT per-client commission. So client CLV is computed
from the closing record: the Deal Sheets / vnre_sold_history.json (1,450+ closings,
2009–2026) plus FUB won deals, summed per past client across all their closings
(repeat clients rank highest). Output is a writeback plan for fub_push.py to set
each FUB person's "Lifetime Value" custom field.

Pure stdlib, no network. Commission basis is configurable and degrades gracefully.
"""
import argparse
import json
import re

# ----------------------------------------------------------------- defaults (override via --config)
CFG = {
    "listingRate": 0.025,            # commission rate, listing side
    "buyerRate": 0.025,              # commission rate, buyer side
    "defaultRate": 0.025,
    "avgGci": {"listing": 12000, "buyer": 5500, "default": 8500},  # from the 2026 plan
    "customFieldName": "Lifetime Value",
}


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())

def last_name(rec):
    n = rec.get("lastName") or rec.get("family") or rec.get("name") or ""
    return n.split()[-1] if n else ""

def commission_of(rec, cfg):
    """Best available commission for one closing; returns (amount, basis)."""
    for k in ("commission", "gci", "GCI"):
        if isinstance(rec.get(k), (int, float)) and rec[k] > 0:
            return float(rec[k]), "actual"
    price = rec.get("salePrice") or rec.get("price")
    side = (rec.get("side") or "").lower()
    if isinstance(price, (int, float)) and price > 0:
        rate = cfg["listingRate"] if "list" in side else cfg["buyerRate"] if "buy" in side else cfg["defaultRate"]
        return price * rate, f"price×{rate}"
    if side:
        g = cfg["avgGci"].get("listing" if "list" in side else "buyer", cfg["avgGci"]["default"])
        return float(g), "avgGci/side"
    return float(cfg["avgGci"]["default"]), "avgGci/default"


def build_people_index(people):
    idx = {"addr": {}, "namecity": {}, "name": {}}
    for p in people:
        ln = norm(last_name(p))
        idx["addr"].setdefault(ln + norm(p.get("address", "")), p)
        idx["namecity"].setdefault(ln + norm(p.get("city", "")), p)
        idx["name"].setdefault(norm((p.get("firstName", "") + p.get("lastName", "")) or p.get("name", "")), p)
    return idx

def match_person(rec, idx):
    ln = norm(last_name(rec))
    if rec.get("address") and (p := idx["addr"].get(ln + norm(rec["address"]))):
        return p, "address"
    if rec.get("city") and (p := idx["namecity"].get(ln + norm(rec.get("city", "")))):
        return p, "name+city"
    fn = norm((rec.get("firstName", "") or "") + (rec.get("lastName", "") or last_name(rec)))
    if (p := idx["name"].get(fn)):
        return p, "name"
    return None, "unmatched"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sold", help="closing records (CLV source)")
    ap.add_argument("--people", help="FUB people (writeback targets)")
    ap.add_argument("--config")
    ap.add_argument("--out", help="writeback plan JSON")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    cfg = dict(CFG)
    if args.config:
        cfg.update(json.load(open(args.config)))
    if args.selftest:
        return selftest(cfg)
    if not (args.sold and args.people and args.out):
        ap.error("--sold, --people and --out are required")

    sold = json.load(open(args.sold))
    sold = sold.get("deals", sold) if isinstance(sold, dict) else sold
    people = json.load(open(args.people))
    people = people.get("contacts", people) if isinstance(people, dict) else people
    idx = build_people_index(people)

    clients = {}     # key -> aggregate
    for rec in sold:
        amt, basis = commission_of(rec, cfg)
        person, conf = match_person(rec, idx)
        key = str(person.get("id")) if person else "unmatched:" + norm(last_name(rec)) + norm(rec.get("address", ""))
        c = clients.setdefault(key, {
            "personId": person.get("id") if person else None,
            "name": (person.get("firstName", "") + " " + person.get("lastName", "")).strip()
                    if person else (rec.get("family") or rec.get("name") or last_name(rec)),
            "lifetimeValue": 0.0, "closings": 0, "matchConfidence": conf if person else "unmatched",
            "bases": set(),
        })
        c["lifetimeValue"] += amt
        c["closings"] += 1
        c["bases"].add(basis)

    matched, unmatched = [], []
    for c in clients.values():
        c["lifetimeValue"] = round(c["lifetimeValue"])
        c["basis"] = "+".join(sorted(c.pop("bases")))
        (matched if c["personId"] else unmatched).append(c)
    matched.sort(key=lambda x: x["lifetimeValue"], reverse=True)
    unmatched.sort(key=lambda x: x["lifetimeValue"], reverse=True)

    json.dump({"customFieldName": cfg["customFieldName"], "writeback": matched,
               "unmatchedClients": unmatched,
               "summary": {"matched": len(matched), "unmatched": len(unmatched),
                           "totalCLV": round(sum(c["lifetimeValue"] for c in matched + unmatched))}},
              open(args.out, "w"), indent=2)
    print(f"CLV: {len(matched)} matched to FUB, {len(unmatched)} unmatched (candidates to add). "
          f"-> {args.out}")


def selftest(cfg):
    sold = [
        {"family": "Edwards", "address": "16408 Riggs Rd", "city": "Stilwell", "side": "listing", "salePrice": 400000},
        {"family": "Edwards", "address": "9 Old St", "city": "Stilwell", "side": "buyer", "salePrice": 300000},  # repeat client
        {"family": "Nomatch", "address": "1 Nowhere", "city": "Olathe", "commission": 9000},
    ]
    people = [{"id": 1, "firstName": "Andrew", "lastName": "Edwards", "address": "16408 Riggs Rd", "city": "Stilwell"}]
    idx = build_people_index(people)
    # Edwards listing -> 400000*0.025=10000 ; buyer -> 300000*0.025=7500 ; both attribute to person 1 (repeat)
    p, conf = match_person(sold[0], idx)
    assert p and p["id"] == 1 and conf == "address", conf
    a0, _ = commission_of(sold[0], cfg); assert a0 == 10000, a0
    a1, _ = commission_of(sold[1], cfg); assert a1 == 7500, a1
    a2, b2 = commission_of(sold[2], cfg); assert a2 == 9000 and b2 == "actual", (a2, b2)
    p2, conf2 = match_person(sold[2], idx); assert p2 is None and conf2 == "unmatched"
    print("selftest OK — commission basis, repeat-client aggregation, and matching all correct")


if __name__ == "__main__":
    main()
