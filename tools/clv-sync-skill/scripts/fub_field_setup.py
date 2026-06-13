#!/usr/bin/env python3
"""
fub_field_setup.py — create/verify the Follow Up Boss custom fields the suite needs.

You haven't mapped a client Lifetime Value field in FUB yet, so the CLV sync has
nowhere to write. This sets that up: it checks /customFields for the field, creates
it if missing (and creation is permitted), and reports the API key (e.g.
customLifetimeValue) to drop into clv-sync's config.json. If your FUB plan only allows
custom fields via the admin UI, it prints the exact click-path instead of failing.

Read-only by default (--check). Pass --create to actually create missing fields.
Auth identical to the other FUB scripts (Basic key + X-System headers).
"""
import argparse
import base64
import json
import os
import re
import sys
import urllib.error
import urllib.request

BASE = "https://api.followupboss.com/v1"

# Fields the suite uses. type: text|number|date|dropdown.
SUITE_FIELDS = [
    {"name": "Lifetime Value", "type": "number", "used_by": "clv-sync (CLV scoring in the Database & COI brief)"},
    {"name": "Mortgage Rate", "type": "number", "used_by": "Database & COI refi touch"},
    {"name": "Preferred Channel", "type": "text", "used_by": "Database & COI + active-hunter delivery"},
    {"name": "Opt-Out", "type": "text", "used_by": "compliance suppression (or use a tag)"},
]


def field_key(name):
    """FUB exposes a custom field 'Lifetime Value' as the person key 'customLifetimeValue'."""
    parts = re.sub(r"[^A-Za-z0-9 ]", "", name).split()
    return "custom" + "".join(w[:1].upper() + w[1:] for w in parts)

def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


class FUB:
    def __init__(self, key, x_system=None, x_system_key=None):
        tok = base64.b64encode(f"{key}:".encode()).decode()
        self.h = {"Authorization": f"Basic {tok}", "Content-Type": "application/json"}
        if x_system:
            self.h["X-System"] = x_system
        if x_system_key:
            self.h["X-System-Key"] = x_system_key

    def _req(self, path, method="GET", body=None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(f"{BASE}/{path}", data=data, headers=self.h, method=method)
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode() or "{}")

    def list_fields(self):
        _, j = self._req("customFields")
        return j.get("customfields", j.get("customFields", []))

    def create_field(self, name, ftype):
        return self._req("customFields", "POST", {"name": name, "type": ftype})


def load_key(cfg):
    key = os.environ.get("FUB_API_KEY")
    if not key and cfg.get("apiKeyFile"):
        raw = open(os.path.expanduser(cfg["apiKeyFile"])).read()
        m = re.search(r"[A-Za-z0-9]{20,}", raw)
        key = m.group(0) if m else raw.strip()
    if not key:
        sys.exit("No API key. Set FUB_API_KEY or config.apiKeyFile.")
    return key


def ui_steps(name, ftype):
    return (f'   FUB → Admin → Custom Fields → "Add Custom Field" → '
            f'Name: "{name}", Type: {ftype} → Save. '
            f'Then set clv-sync config customFieldName = "{name}".')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config")
    ap.add_argument("--create", action="store_true", help="create missing fields (default: check only)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()

    cfg = json.load(open(args.config)) if args.config else {}
    api = FUB(load_key(cfg), cfg.get("xSystem"), cfg.get("xSystemKey"))
    try:
        existing = api.list_fields()
    except urllib.error.HTTPError as e:
        sys.exit(f"Could not list custom fields ({e.code}). Check API key / permissions.")
    by_norm = {norm(f.get("name")): f for f in existing}

    print(f"{'CREATE' if args.create else 'CHECK'} mode · {len(existing)} custom fields in FUB\n")
    for spec in SUITE_FIELDS:
        hit = by_norm.get(norm(spec["name"]))
        if hit:
            print(f"  ✅ '{spec['name']}' exists → key `{field_key(spec['name'])}`  ({spec['used_by']})")
            continue
        if not args.create:
            print(f"  ⬜ '{spec['name']}' MISSING  ({spec['used_by']})")
            print(ui_steps(spec["name"], spec["type"]))
            continue
        try:
            status, _ = api.create_field(spec["name"], spec["type"])
            print(f"  ➕ created '{spec['name']}' ({status}) → key `{field_key(spec['name'])}`")
        except urllib.error.HTTPError as e:
            print(f"  ⚠️  API create not permitted for '{spec['name']}' ({e.code}). Use the UI:")
            print(ui_steps(spec["name"], spec["type"]))

    print(f"\nNext: set clv-sync config.json customFieldName = \"Lifetime Value\" "
          f"(key {field_key('Lifetime Value')}), then run build_clv.py + fub_push.py.")


def selftest():
    assert field_key("Lifetime Value") == "customLifetimeValue"
    assert field_key("Mortgage Rate") == "customMortgageRate"
    assert norm("Lifetime Value") == norm("lifetime  value!")
    # existence match is normalized (case/space/punct-insensitive)
    existing = [{"name": "Lifetime  Value"}, {"name": "Mortgage Rate"}]
    by = {norm(f["name"]): f for f in existing}
    assert by.get(norm("lifetime value"))
    assert not by.get(norm("Preferred Channel"))
    print("selftest OK — field-key derivation + normalized existence matching correct")


if __name__ == "__main__":
    main()
