#!/usr/bin/env python3
"""
fub_push.py — write client Lifetime Value back to Follow Up Boss (safely).

Consumes the writeback plan from build_clv.py and sets each FUB person's
"Lifetime Value" custom field via PUT /people/{id}. Touches ONLY that one field —
never overwrites anything else.

Safety: dry-run by DEFAULT. It prints exactly what would change and writes nothing
until you pass --commit. --selftest verifies payload construction offline.

Auth identical to fub_pull.py (Basic key + X-System headers; FUB_API_KEY env or key file).
"""
import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE = "https://api.followupboss.com/v1"


def field_key(custom_field_name):
    """FUB exposes a custom field named 'Lifetime Value' as the key 'customLifetimeValue'."""
    parts = re.sub(r"[^A-Za-z0-9 ]", "", custom_field_name).split()
    return "custom" + "".join(w[:1].upper() + w[1:] for w in parts)


class FUB:
    def __init__(self, api_key, x_system=None, x_system_key=None):
        token = base64.b64encode(f"{api_key}:".encode()).decode()
        self.headers = {"Authorization": f"Basic {token}", "Content-Type": "application/json"}
        if x_system:
            self.headers["X-System"] = x_system
        if x_system_key:
            self.headers["X-System-Key"] = x_system_key

    def put_person(self, pid, body):
        data = json.dumps(body).encode()
        req = urllib.request.Request(f"{BASE}/people/{pid}", data=data, headers=self.headers, method="PUT")
        for attempt in range(5):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    return r.status
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    time.sleep(int(e.headers.get("Retry-After", 2 ** attempt)))
                    continue
                raise
        raise RuntimeError(f"PUT failed: person {pid}")


def load_key(config):
    key = os.environ.get("FUB_API_KEY")
    if not key and config.get("apiKeyFile"):
        raw = open(os.path.expanduser(config["apiKeyFile"])).read()
        m = re.search(r"[A-Za-z0-9]{20,}", raw)
        key = m.group(0) if m else raw.strip()
    if not key:
        sys.exit("No API key. Set FUB_API_KEY or config.apiKeyFile.")
    return key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", help="writeback plan from build_clv.py")
    ap.add_argument("--config")
    ap.add_argument("--commit", action="store_true", help="actually write (default: dry-run)")
    ap.add_argument("--min", type=int, default=0, help="skip CLV below this")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        key = field_key("Lifetime Value")
        assert key == "customLifetimeValue", key
        assert field_key("CLV") == "customCLV", field_key("CLV")
        print("selftest OK — custom field key derivation correct")
        return

    if not args.plan:
        sys.exit("need --plan (or --selftest)")
    plan = json.load(open(args.plan))
    key = field_key(plan.get("customFieldName", "Lifetime Value"))
    rows = [r for r in plan["writeback"] if r["personId"] and r["lifetimeValue"] >= args.min]

    print(f"{'COMMIT' if args.commit else 'DRY-RUN'} · field '{key}' · {len(rows)} contacts\n")
    for r in rows[:25]:
        print(f"  person {r['personId']:>8}  {r['name'][:28]:28}  -> ${r['lifetimeValue']:,}  "
              f"({r['closings']} closings, {r['matchConfidence']})")
    if len(rows) > 25:
        print(f"  … and {len(rows) - 25} more")

    if not args.commit:
        print("\nDry run — nothing written. Re-run with --commit to apply.")
        return

    cfg = json.load(open(args.config)) if args.config else {}
    api = FUB(load_key(cfg), cfg.get("xSystem"), cfg.get("xSystemKey"))
    ok = 0
    for r in rows:
        api.put_person(r["personId"], {key: r["lifetimeValue"]})
        ok += 1
    print(f"\nwrote Lifetime Value to {ok} contacts.")


if __name__ == "__main__":
    main()
