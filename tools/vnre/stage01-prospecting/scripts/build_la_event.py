#!/usr/bin/env python3
"""
build_la_event.py — Stage 01 booking → handoff bridge.

The keystone of appointment-booking: turn a booked listing appointment (from DVN, an
ISA, Upfirst, or a voice agent) into a well-formed Google Calendar `LA:` event in the
exact shape `plp-folder-build` parses — so the PLP folder + presentation pipeline runs
automatically downstream. Also emits the FUB note text and the predicted PLP folder name.

Pure stdlib, no network. The skill takes this output and calls the Calendar MCP
`create_event` (summary / startTime / endTime / location / description / timeZone) behind
a confirmation gate, then logs the FUB note.
"""
import argparse
import json
import re
from datetime import datetime, timedelta

DEFAULT_TZ = "America/Chicago"     # Kansas City metro = Central


def fmt_dt(dt):
    return dt.strftime("%A, %B %-d, %Y at %-I:%M %p")

def address_str(a):
    street = (a.get("propertyStreet") or "").strip()
    city = (a.get("propertyCity") or "").strip()
    state = (a.get("propertyState") or "").strip()
    zc = (a.get("propertyZip") or "").strip()
    tail = " ".join(x for x in (city, state, zc) if x)
    return ", ".join(x for x in (street, tail) if x)

def folder_address(a):
    """Address as used in the PLP folder name: street + city, no state/zip noise."""
    street = (a.get("propertyStreet") or "").strip()
    city = (a.get("propertyCity") or "").strip()
    state = (a.get("propertyState") or "").strip()
    return " ".join(x for x in (street, city, state) if x)


def line(label, val):
    return f"- {label}: {val}" if val not in (None, "", []) else None

def section(title, items):
    body = [x for x in items if x]
    return ([title] + body + [""]) if body else []


def build_description(a, dt):
    name = a.get("name", "")
    L = [f"PRE-QUAL SUMMARY — {name.upper()}", "",
         f"Appointment: {fmt_dt(dt)}",
         f"Property: {address_str(a)}"]
    if a.get("fubProfileUrl"):
        L.append(f"FUB Profile: {a['fubProfileUrl']}")
    if a.get("zillowUrl"):
        L.append(f"Zillow: {a['zillowUrl']}")
    L.append("")

    L += section("SOURCE & SITUATION", [
        line("Source", a.get("source")), line("County", a.get("county")),
        line("Interviewing other agents", a.get("interviewing")),
        line("Moving to", a.get("movingTo")), line("Timeline", a.get("timeline")),
        line("Plan to hire by", a.get("planToHire"))])
    L += section("PRICING", [
        line("Price expectation", a.get("priceExpectation")), line("Owe", a.get("owe")),
        line("Prior listing history", a.get("priorListingHistory"))])
    L += section("PROPERTY", [
        line("Beds/Baths", a.get("bedsBaths")), line("SqFt", a.get("sqft")),
        line("Garage", a.get("garage")), line("Lot", a.get("lot")),
        line("Condition", a.get("condition")), line("Updates", a.get("updates")),
        line("Known issues", a.get("knownIssues"))])
    qs = a.get("questionsForDvn") or []
    L += section("QUESTIONS FOR DVN", [f"- {q}" for q in qs])
    L += section("LOGISTICS / OPEN ITEMS", [line("", a.get("logistics")) and a.get("logistics")
                                            and f"- {a['logistics']}"])
    L += section("NOTES", [(f"- {a['notes']}" if a.get("notes") else None),
                           line("PLP instructions", a.get("plpInstructions"))])
    return "\n".join(L).rstrip() + "\n"


def build(a):
    if not a.get("name") or not a.get("datetime"):
        raise ValueError("appointment requires at least 'name' and 'datetime'")
    tz = a.get("timeZone", DEFAULT_TZ)
    start = datetime.strptime(a["datetime"][:19], "%Y-%m-%dT%H:%M:%S")
    end = start + timedelta(minutes=int(a.get("durationMin", 60)))
    return {
        "create_event": {
            "summary": f"LA: {a['name']}",
            "startTime": start.strftime("%Y-%m-%dT%H:%M:%S"),
            "endTime": end.strftime("%Y-%m-%dT%H:%M:%S"),
            "timeZone": tz,
            "location": address_str(a),
            "description": build_description(a, start),
        },
        "predictedPlpFolder": f"PLP - {a['name']}, {folder_address(a)}, {start.year}",
        "fubNote": (f"Listing appointment booked for {fmt_dt(start)} at "
                    f"{address_str(a) or 'TBD address'}. LA: calendar event created; "
                    f"PLP folder auto-builds on the next plp-folder-build run."),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--appt", help="appointment JSON")
    ap.add_argument("--out", help="output JSON (defaults to stdout)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not args.appt:
        ap.error("--appt required (or --selftest)")
    result = build(json.load(open(args.appt)))
    out = json.dumps(result, indent=2)
    (open(args.out, "w").write(out + "\n") if args.out else print(out))
    if args.out:
        print(f"LA event payload -> {args.out}")


def selftest():
    a = {"name": "Edwards, Shannon & Andrew", "propertyStreet": "16408 Riggs Rd",
         "propertyCity": "Stilwell", "propertyState": "KS", "datetime": "2026-06-20T14:00:00",
         "durationMin": 60, "source": "Expired", "county": "Johnson", "timeline": "30-60 days",
         "priceExpectation": "$640k", "bedsBaths": "4/3", "questionsForDvn": ["Commission?"],
         "plpInstructions": "Pull Matrix comps within 1.5mi"}
    r = build(a)
    ce = r["create_event"]
    assert ce["summary"] == "LA: Edwards, Shannon & Andrew", ce["summary"]
    assert ce["endTime"] == "2026-06-20T15:00:00", ce["endTime"]      # +60 min
    assert "Stilwell" in ce["location"] and "KS" in ce["location"]
    assert "PRE-QUAL SUMMARY — EDWARDS" in ce["description"]
    assert "Source: Expired" in ce["description"] and "Timeline: 30-60 days" in ce["description"]
    assert "Owe:" not in ce["description"]                            # empty fields omitted
    assert r["predictedPlpFolder"] == "PLP - Edwards, Shannon & Andrew, 16408 Riggs Rd Stilwell KS, 2026"
    assert "Johnson" not in ce["summary"]
    print("selftest OK — LA: title, address, end time, pre-qual description, and PLP folder name all correct")
    print("\n--- sample description ---\n" + ce["description"])


if __name__ == "__main__":
    main()
