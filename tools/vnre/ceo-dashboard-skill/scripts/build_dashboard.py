#!/usr/bin/env python3
"""
build_dashboard.py — VNRE Stage 07 CEO P&L dashboard.

Takes the QuickBooks P&L (account report) + A/R aging + the 2026 plan and renders a
one-screen CEO dashboard: actuals vs plan, annualized pace, the 50%-margin guard,
and an A/R / collections flag — each with a red/amber/green status and an action.

Pure stdlib, no network. Feed it the JSON the QuickBooks MCP tools return (or any
dict with the same top-level keys). Real financials never need to live in the repo.
"""
import argparse
import json
from datetime import date, datetime

GREEN, AMBER, RED = "🟢", "🟡", "🔴"


def rag(actual, target, green=0.95, amber=0.80, higher_is_better=True):
    if target == 0:
        return AMBER
    ratio = actual / target
    if not higher_is_better:
        ratio = 2 - ratio
    return GREEN if ratio >= green else AMBER if ratio >= amber else RED

def usd(n):
    return f"${n:,.0f}"

def pct(n):
    return f"{n*100:.0f}%"

def parse_date(s):
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


# ----------------------------------------------------------------- inputs
def read_pl(pl):
    income = pl.get("totalIncome") or 0
    expenses = pl.get("totalExpenses") or 0
    gross = pl.get("grossProfit")
    net = pl.get("netIncome")
    cogs = (income - gross) if gross is not None else pl.get("totalCOGS") or 0
    if net is None:
        net = income - cogs - expenses
    return {
        "income": income, "cogs": cogs, "expenses": expenses, "net": net,
        "margin": (net / income) if income else 0,
        "start": parse_date(pl.get("periodStart")), "end": parse_date(pl.get("periodEnd")),
    }

def read_ar(ar):
    s = (ar or {}).get("summary", {})
    return {
        "total": s.get("totalReceivables", 0), "overdue": s.get("totalOverdue", 0),
        "overduePct": (s.get("overduePercent", 0) or 0) / 100,
        "buckets": s.get("bucketTotals", {}),
        "top": s.get("topOverdueCustomers", []),
    }


# ----------------------------------------------------------------- render
def build(pl, ar, plan, today):
    p = read_pl(pl)
    a = read_ar(ar) if ar else None
    end = p["end"] or today
    start = p["start"] or date(end.year, 1, 1)
    elapsed = max((end - start).days, 1) / 365.0
    ann = (lambda v: v / elapsed)

    rev_t, net_t = plan["revenueTarget"], plan["netTarget"]
    opex_t, margin_t = plan["opexTarget"], plan["marginTarget"]

    L = [f"# VNRE CEO Dashboard — {end.isoformat()}",
         f"_{pl.get('companyName', 'Van Noy Real Estate')} · {start.isoformat()} → {end.isoformat()} "
         f"({pct(elapsed)} of year) · accrual_", "",
         "## Scorecard — actual vs 2026 plan", "",
         "| Metric | YTD actual | Annualized | 2026 plan | Pace | |",
         "|---|---:|---:|---:|---:|:-:|"]

    def row(label, ytd, plan_v, higher=True, money=True):
        an = ann(ytd)
        fmt = usd if money else pct
        flag = rag(an, plan_v, higher_is_better=higher)
        pace = f"{(an/plan_v*100):.0f}%" if plan_v else "—"
        L.append(f"| {label} | {fmt(ytd)} | {fmt(an)} | {fmt(plan_v)} | {pace} | {flag} |")

    row("Revenue / income", p["income"], rev_t)
    row("Operating expenses", p["expenses"], opex_t, higher=False)
    row("Net profit", p["net"], net_t)
    # margin is a ratio, not annualized
    mflag = rag(p["margin"], margin_t)
    L.append(f"| **Net margin** | **{pct(p['margin'])}** | — | **{pct(margin_t)}** | "
             f"{p['margin']/margin_t*100:.0f}% | {mflag} |")
    L.append("")

    # margin guard
    L += ["## 🎯 50% margin guard", ""]
    if p["margin"] >= margin_t * 0.95:
        L.append(f"{GREEN} Margin {pct(p['margin'])} is on target.")
    else:
        gap = (margin_t - p["margin"]) * p["income"]
        L.append(f"{mflag} Margin **{pct(p['margin'])}** vs **{pct(margin_t)}** target — a "
                 f"**{usd(gap)}** profit gap at current revenue. Levers: cost of sales / commission "
                 f"splits ({usd(p['cogs'])} YTD) and operating expenses ({usd(p['expenses'])} YTD).")
    L.append("")

    # A/R
    if a:
        L += ["## 💵 A/R & collections", "",
              f"Receivables **{usd(a['total'])}** · overdue **{pct(a['overduePct'])}**."]
        nineties = a["buckets"].get("91+", 0)
        if nineties:
            who = ", ".join(f"{c['name']} ({usd(c['overdue'])})" for c in a["top"]
                            if c.get("overdue", 0) and c.get("overdue") >= nineties * 0.5) or "—"
            L.append(f"{RED} **{usd(nineties)} is 91+ days** — collect now: {who}.")
        elif a["overduePct"] > 0.5:
            L.append(f"{AMBER} Over half of A/R is past due — work the 1–30 bucket before it ages.")
        else:
            L.append(f"{GREEN} A/R aging is healthy.")
        L.append("")

    # actions
    L += ["## ▶ This week's actions", ""]
    acts = []
    if p["margin"] < margin_t * 0.95:
        acts.append(f"Close the margin gap: review the {usd(p['cogs'])} cost-of-sales and "
                    f"{usd(p['expenses'])} opex lines against plan.")
    if ann(p["income"]) < rev_t * 0.95:
        acts.append(f"Revenue pace ~{ann(p['income'])/rev_t*100:.0f}% of plan — protect listing "
                    f"appointments (the funnel that drives GCI).")
    if a and a["buckets"].get("91+", 0):
        acts.append(f"Collect the {usd(a['buckets']['91+'])} sitting 91+ days.")
    L += [f"- {x}" for x in acts] or ["- On plan — hold the line."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pl", help="QuickBooks P&L JSON")
    ap.add_argument("--ar", help="QuickBooks A/R aging JSON (optional)")
    ap.add_argument("--plan", required=False, help="2026 plan JSON")
    ap.add_argument("--out", help="output markdown")
    ap.add_argument("--today", default=date.today().isoformat())
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if not (args.pl and args.plan and args.out):
        ap.error("--pl, --plan and --out are required")
    pl = json.load(open(args.pl))
    ar = json.load(open(args.ar)) if args.ar else None
    plan = json.load(open(args.plan))
    open(args.out, "w").write(build(pl, ar, plan, parse_date(args.today)))
    print(f"dashboard -> {args.out}")


def selftest():
    pl = {"companyName": "Test RE", "periodStart": "2026-01-01", "periodEnd": "2026-07-02",
          "totalIncome": 500000, "grossProfit": 400000, "totalExpenses": 250000, "netIncome": 150000}
    plan = {"revenueTarget": 1250000, "opexTarget": 537500, "netTarget": 625000, "marginTarget": 0.50}
    ar = {"summary": {"totalReceivables": 16050, "totalOverdue": 16050, "overduePercent": 100,
                      "bucketTotals": {"91+": 11500, "1-30": 4550},
                      "topOverdueCustomers": [{"name": "All Western Mortgage", "overdue": 11500}]}}
    p = read_pl(pl)
    assert p["cogs"] == 100000 and abs(p["margin"] - 0.30) < 1e-9, p
    out = build(pl, ar, plan, date(2026, 7, 2))
    assert "CEO Dashboard" in out and "margin guard" in out and "91+ days" in out
    assert "50%" in out and "All Western Mortgage" in out
    print("selftest OK — P&L parse, margin guard, pace, and A/R flag all render")


if __name__ == "__main__":
    main()
