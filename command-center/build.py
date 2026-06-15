#!/usr/bin/env python3
"""
build.py — VNRE Operations Command Center build / refresh engine.

The "Coefficient layer": connects the company's live data sources to a single
embedded snapshot, then injects it into a self-contained dashboard the team can
open by double-click (no server, works offline).

Two jobs:
  1. INJECT  — take data/snapshot.json and embed it into index.html between the
               /*VNRE_SNAPSHOT_START*/ ... /*VNRE_SNAPSHOT_END*/ markers.
  2. REFRESH — transform the raw JSON the QuickBooks MCP tools return (P&L,
               A/R aging, Balance Sheet) into the snapshot's `finance` block,
               then inject. Listing-funnel / pipeline / EOS fields come from the
               Google Drive trackers and are updated in snapshot.json directly
               (the trackers are the source of truth; see README "Connector map").

Pure stdlib. No network. Deterministic. `--selftest` runs fully offline.

Usage
-----
  python3 build.py                      # inject data/snapshot.json -> index.html
  python3 build.py --refresh-financials \
        --pl _data/pl.json --ar _data/ar.json --balance _data/bs.json
  python3 build.py --selftest

Refreshing financials (weekly, from the QuickBooks MCP):
  - profit_loss_quickbooks_account(periodStart=YYYY-01-01)  -> _data/pl.json
  - qbo_accounting_get_ar_aging_summary()                   -> _data/ar.json
  - qbo_accounting_get_balance_sheet(start=end=today)       -> _data/bs.json
  Save each report's JSON to _data/ (gitignored), then run --refresh-financials.
"""
import argparse, json, os, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SNAP = os.path.join(HERE, "data", "snapshot.json")
HTML = os.path.join(HERE, "index.html")
START = "/*VNRE_SNAPSHOT_START*/"
END = "/*VNRE_SNAPSHOT_END*/"


# --------------------------------------------------------------- QuickBooks P&L
def _pl_rows(pl):
    """The MCP P&L nests account lines under reportData.data.rows (recursive)."""
    return (pl.get("reportData") or {}).get("data", {}).get("rows", []) or []


def _row_name(r):
    for c in r.get("cells", []):
        if c.get("name") == "ACCOUNT_NAME":
            return c.get("value")
    return None


def _row_total(r):
    for c in r.get("cells", []):
        if c.get("name") == "DETAIL_NATURAL_HOME_AMOUNT__TOTAL":
            return c.get("value")
    return None


def _row_own(r):
    for c in r.get("cells", []):
        if c.get("name") == "DETAIL_NATURAL_HOME_AMOUNT__TOTAL_WITHOUT_SUBGROUPS":
            return c.get("value")
    return None


def _flatten_pl(rows, depth=0, out=None):
    out = [] if out is None else out
    for r in rows:
        name = _row_name(r)
        own, tot = _row_own(r), _row_total(r)
        val = own if (own not in (None, 0)) else tot
        out.append((depth, name, val, own, tot))
        out = _flatten_pl(r.get("rows") or [], depth + 1, out)
    return out


def transform_pl(pl):
    """QuickBooks P&L JSON -> finance.pl + incomeMix + expenseTop."""
    income = pl.get("totalIncome") or 0
    gross = pl.get("grossProfit")
    expenses = pl.get("totalExpenses") or 0
    net = pl.get("netIncome")
    cogs = (income - gross) if gross is not None else 0
    if net is None:
        net = income - cogs - expenses

    flat = _flatten_pl(_pl_rows(pl))
    # income leaf accounts (own value present, name starts with a 4xxx code, not a "Total")
    income_mix, expense_top = [], []
    for depth, name, val, own, tot in flat:
        if not name or own in (None, 0):
            continue
        n = str(name)
        if n.startswith(("4011", "4012", "4013")):  # commission by state
            label = {"4011": "Commission — KS", "4012": "Commission — KCMO",
                     "4013": "Commission — MO"}[n[:4]]
            income_mix.append({"label": label, "amount": round(own, 2)})
        elif n.startswith("4005"):
            income_mix.append({"label": "RE Systems Design", "amount": round(own, 2)})
        elif n.startswith("4015"):
            income_mix.append({"label": "Digital Marketing", "amount": round(own, 2)})
        elif n.startswith("4100"):
            income_mix.append({"label": "Rental Income", "amount": round(own, 2)})
        elif n.startswith("4700"):
            income_mix.append({"label": "Interest", "amount": round(own, 2)})

    # expense categories = the 6xxx/7xxx/8xxx/9xxx GROUP subtotals (depth 1 under Expenses)
    for depth, name, val, own, tot in flat:
        if not name or tot in (None, 0):
            continue
        n = str(name)
        if n[:4].isdigit() and n[0] in "6789" and not n.startswith(("9500", "9505")):
            # group subtotal rows carry tot but own is None/0
            if (own in (None, 0)) and tot:
                expense_top.append({"label": n, "amount": round(tot, 2)})
    expense_top.sort(key=lambda x: -x["amount"])

    return {
        "pl": {
            "periodStart": pl.get("periodStart"),
            "periodEnd": pl.get("periodEnd"),
            "basis": "accrual",
            "income": round(income, 2), "cogs": round(cogs, 2),
            "grossProfit": round(gross, 2) if gross is not None else None,
            "expenses": round(expenses, 2), "net": round(net, 2),
            "margin": round(net / income, 4) if income else 0,
        },
        "incomeMix": income_mix or None,
        "expenseTop": expense_top[:12] or None,
    }


# --------------------------------------------------------------- A/R aging
def transform_ar(ar):
    s = (ar or {}).get("summary", {})
    bt = s.get("bucketTotals", {}) or {}
    buckets = {
        "current": bt.get("Current", 0), "1-30": bt.get("1-30", 0),
        "31-60": bt.get("31-60", 0), "61-90": bt.get("61-90", 0),
        "91+": bt.get("91+", 0),
    }
    customers = [{"name": c["name"], "amount": c.get("overdue", c.get("total", 0)),
                 "bucket": _bucket_for(c, s)} for c in s.get("topOverdueCustomers", [])]
    nineties = [c for c in customers if c["bucket"] == "91+"]
    at_risk = max(nineties, key=lambda c: c["amount"], default=None)
    return {
        "total": s.get("totalReceivables", 0), "overdue": s.get("totalOverdue", 0),
        "overduePct": round((s.get("overduePercent", 0) or 0) / 100, 4),
        "buckets": buckets,
        "atRisk": ({"amount": at_risk["amount"], "customer": at_risk["name"], "bucket": "91+"}
                   if at_risk else None),
        "customers": customers,
    }


def _bucket_for(c, summary):
    for b, lst in (summary.get("customersByBucket") or {}).items():
        if any(x["name"] == c["name"] for x in lst):
            return b
    return "1-30"


# --------------------------------------------------------------- Balance sheet
def transform_balance(bs):
    s = (bs or {}).get("summary", {})
    ab, lb, rt = s.get("assetBreakdown", {}), s.get("liabilityBreakdown", {}), s.get("ratios", {})
    return {
        "asOf": (bs.get("period") or "").replace("As of ", ""),
        "cash": ab.get("cash"), "accountsReceivable": ab.get("accountsReceivable"),
        "totalAssets": s.get("totalAssets"), "totalLiabilities": s.get("totalLiabilities"),
        "equity": s.get("totalEquity"), "workingCapital": rt.get("workingCapital"),
        "currentRatio": rt.get("currentRatio"), "debtToEquity": rt.get("debtToEquity"),
        "creditCards": lb.get("creditCards"), "autoNote": lb.get("longTermLiabilities"),
    }


# --------------------------------------------------------------- snapshot I/O
REQUIRED = ["meta", "finance", "funnel", "pipeline", "database", "eos", "systems"]


def validate(snap):
    missing = [k for k in REQUIRED if k not in snap]
    if missing:
        raise ValueError(f"snapshot missing top-level keys: {missing}")
    pl = snap["finance"].get("pl", {})
    for k in ("income", "expenses", "net"):
        if pl.get(k) is None:
            raise ValueError(f"finance.pl.{k} is required")
    return True


def inject(snap, html_path=HTML):
    with open(html_path) as f:
        html = f.read()
    i, j = html.find(START), html.find(END)
    if i == -1 or j == -1:
        raise RuntimeError("snapshot markers not found in index.html")
    block = START + "\n" + json.dumps(snap, indent=2) + "\n" + END
    new = html[:i] + block + html[j + len(END):]
    with open(html_path, "w") as f:
        f.write(new)
    return len(json.dumps(snap))


# --------------------------------------------------------------- CLI
def cmd_refresh(args):
    snap = json.load(open(SNAP))
    if args.pl:
        upd = transform_pl(json.load(open(args.pl)))
        snap["finance"]["pl"] = upd["pl"]
        if upd["incomeMix"]:
            snap["finance"]["incomeMix"] = upd["incomeMix"]
        if upd["expenseTop"]:
            snap["finance"]["expenseTop"] = upd["expenseTop"]
    if args.ar:
        snap["finance"]["ar"] = transform_ar(json.load(open(args.ar)))
    if args.balance:
        snap["finance"]["balance"] = transform_balance(json.load(open(args.balance)))
    snap["meta"]["asOf"] = args.asof or snap["meta"].get("asOf")
    snap["meta"]["generated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    validate(snap)
    json.dump(snap, open(SNAP, "w"), indent=2)
    n = inject(snap)
    print(f"refreshed financials + injected ({n} bytes) -> index.html")


def cmd_inject(args):
    snap = json.load(open(SNAP))
    validate(snap)
    n = inject(snap)
    print(f"injected snapshot ({n} bytes) -> index.html")


def selftest():
    # P&L (shape mirrors the QuickBooks MCP output)
    pl = {
        "totalIncome": 446501.03, "grossProfit": 349572.73, "totalExpenses": 267109.92,
        "netIncome": 82462.81, "periodStart": "2026-01-01", "periodEnd": "2026-06-15",
        "reportData": {"data": {"rows": [
            {"cells": [{"name": "ACCOUNT_NAME", "value": "Income"},
                       {"name": "DETAIL_NATURAL_HOME_AMOUNT__TOTAL", "value": 446501.03}],
             "rows": [
                {"cells": [{"name": "ACCOUNT_NAME", "value": "4011 KS"},
                           {"name": "DETAIL_NATURAL_HOME_AMOUNT__TOTAL_WITHOUT_SUBGROUPS", "value": 227888.78},
                           {"name": "DETAIL_NATURAL_HOME_AMOUNT__TOTAL", "value": 227888.78}]},
                {"cells": [{"name": "ACCOUNT_NAME", "value": "4100 Rental Income"},
                           {"name": "DETAIL_NATURAL_HOME_AMOUNT__TOTAL_WITHOUT_SUBGROUPS", "value": 8750},
                           {"name": "DETAIL_NATURAL_HOME_AMOUNT__TOTAL", "value": 8750}]}]},
            {"cells": [{"name": "ACCOUNT_NAME", "value": "6000 Payroll Expenses"},
                       {"name": "DETAIL_NATURAL_HOME_AMOUNT__TOTAL", "value": 85523.73}]},
        ]}},
    }
    out = transform_pl(pl)
    assert out["pl"]["income"] == 446501.03
    assert abs(out["pl"]["cogs"] - 96928.30) < 0.01, out["pl"]["cogs"]
    assert abs(out["pl"]["margin"] - 0.1847) < 0.001, out["pl"]["margin"]
    assert {"label": "Commission — KS", "amount": 227888.78} in out["incomeMix"]
    assert any(e["label"].startswith("6000") for e in out["expenseTop"])

    ar = {"summary": {"totalReceivables": 16050, "totalOverdue": 16050, "overduePercent": 100,
                      "bucketTotals": {"Current": 0, "1-30": 4550, "91+": 11500},
                      "topOverdueCustomers": [{"name": "All Western Mortgage", "overdue": 11500},
                                              {"name": "HomeSmart Encore", "overdue": 2000}],
                      "customersByBucket": {"91+": [{"name": "All Western Mortgage", "amount": 11500}],
                                            "1-30": [{"name": "HomeSmart Encore", "amount": 2000}]}}}
    a = transform_ar(ar)
    assert a["atRisk"]["amount"] == 11500 and a["atRisk"]["customer"] == "All Western Mortgage"
    assert a["buckets"]["91+"] == 11500 and a["overduePct"] == 1.0

    bs = {"period": "As of Jun 15, 2026", "summary": {
        "totalAssets": 128066.03, "totalLiabilities": 70642.09, "totalEquity": 57423.94,
        "assetBreakdown": {"cash": 25888.38, "accountsReceivable": 16050},
        "liabilityBreakdown": {"creditCards": 14196.30, "longTermLiabilities": 47282.51},
        "ratios": {"currentRatio": 1.81, "debtToEquity": 1.23, "workingCapital": 18956.64}}}
    b = transform_balance(bs)
    assert b["cash"] == 25888.38 and b["currentRatio"] == 1.81

    # round-trip validate against the real snapshot if present
    if os.path.exists(SNAP):
        validate(json.load(open(SNAP)))
    print("selftest OK — P&L / A/R / balance transforms + snapshot validate all pass")


def main():
    ap = argparse.ArgumentParser(description="VNRE Command Center build/refresh")
    ap.add_argument("--refresh-financials", action="store_true",
                    help="transform QBO JSON into the finance block, then inject")
    ap.add_argument("--pl"); ap.add_argument("--ar"); ap.add_argument("--balance")
    ap.add_argument("--asof", help="override meta.asOf (YYYY-MM-DD)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.refresh_financials:
        return cmd_refresh(args)
    return cmd_inject(args)


if __name__ == "__main__":
    main()
