#!/usr/bin/env python3
"""
partner_value.py — turn QuickBooks "Sales by Customer" into a partner-nurture brief.

VNRE's QBO customers are B2B partners (lenders, title/banks, insurance, co-op brokers,
builders) — this is the income behind the plan's $25k Vendor MSA line and the "strategic
partnerships" thrust. This ranks partners, classifies them, flags concentration risk, and
proposes nurture actions. Feed it the JSON from the QBO sales-by-customer MCP tool.

Pure stdlib, no network.
"""
import argparse
import json
import re

TYPES = [
    ("Lender", ("mortgage", "funding", "lend", "loan", "bank", "capital", "finance")),
    ("Title / Escrow", ("title", "escrow", "closing")),
    ("Insurance", ("insurance", "insur")),
    ("Co-op Brokerage", ("realty", "real estate", "century", "keller", "remax", "re/max",
                          "compass", "group", "homesmart", "brokerage")),
    ("Builder", ("build", "homes inc", "construction", "ubuildit")),
]

def classify(name):
    n = name.lower()
    for label, kws in TYPES:
        if any(k in n for k in kws):
            return label
    return "Other / Vendor"

def rows_from_report(data):
    """Accept the raw MCP report or a simple [{name, sales}] list."""
    if isinstance(data, dict) and "summary" in data and data["summary"].get("topCustomers"):
        return [(c["name"], float(c["sales"])) for c in data["summary"]["topCustomers"]]
    if isinstance(data, dict) and "reportData" in data:
        out = []
        for row in data["reportData"]["rows"]:
            cells = {c["name"]: c["value"] for c in row["cells"]}
            out.append((cells.get("Customer"), float(cells.get("Total Sales") or 0)))
        return out
    return [(r["name"], float(r["sales"])) for r in data]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--qbo", required=True, help="QBO sales-by-customer JSON")
    ap.add_argument("--out", required=True)
    ap.add_argument("--period", default="last year")
    args = ap.parse_args()

    rows = sorted(rows_from_report(json.load(open(args.qbo))), key=lambda x: x[1], reverse=True)
    total = sum(s for _, s in rows) or 1
    top5 = sum(s for _, s in rows[:5]) / total * 100

    by_type = {}
    for name, sales in rows:
        by_type.setdefault(classify(name), 0)
        by_type[classify(name)] += sales

    out = [f"# VNRE Partner Value Brief — {args.period}", "",
           f"**${total:,.0f}** in partner/referral income across **{len(rows)}** partners · "
           f"top 5 = **{top5:.0f}%** (concentration risk if any single one churns).",
           "", "_Source: QuickBooks Sales by Customer. Serves the $25k Vendor MSA line + the "
           "'strategic partnerships' thrust. Reciprocity: who are you sending business back to?_",
           "", "## Partners by income", "", "| Partner | Type | Income | Share |", "|---|---|---:|---:|"]
    for name, sales in rows:
        out.append(f"| {name} | {classify(name)} | ${sales:,.0f} | {sales/total*100:.0f}% |")
    out += ["", "## By partner type", "", "| Type | Income |", "|---|---:|"]
    for t, v in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        out.append(f"| {t} | ${v:,.0f} |")
    out += ["", "## Suggested actions",
            f"- **Lock the top 5** ({top5:.0f}% of partner income) with formal MSAs and a quarterly check-in — "
            "concentration here is your biggest single risk.",
            "- **Confirm reciprocity:** for each lender/title/insurance partner, verify you're getting "
            "referrals back proportional to what you send. The refi touch (retention engine) routes "
            "past clients to your lender partner — that flow should show up here over time.",
            "- **Coverage gaps:** if a partner type is missing or thin (e.g., no Title/Escrow line), "
            "that's an open MSA opportunity toward the $25k goal.",
            "- **Cross-link to FUB:** tag the FUB contacts behind these partners as `Partner/{type}` so "
            "referral flow is trackable both directions."]
    open(args.out, "w").write("\n".join(out) + "\n")
    print(f"partner brief -> {args.out} ({len(rows)} partners, top5 {top5:.0f}%)")


if __name__ == "__main__":
    main()
