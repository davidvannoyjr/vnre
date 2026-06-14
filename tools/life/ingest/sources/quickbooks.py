"""QuickBooks Online adapter — business finance layer.

Pulls P&L (YTD + monthly), balance sheet (cash/AR/equity/liabilities), and A/R aging, then
normalizes to life.finance_biz_snapshot + life.finance_biz_monthly. The normalization below is
exactly what produced warehouse-snapshot.json from the live QBO data on 2026-06-14.

Auth: QBO OAuth2 (refresh_token in config). Reports API:
  GET /v3/company/{realm}/reports/ProfitAndLoss?start_date=&end_date=&summarize_column_by=Month
  GET /v3/company/{realm}/reports/BalanceSheet?date=
  GET /v3/company/{realm}/reports/AgedReceivables?date=
"""
import datetime as dt


def _qbo_get(cfg, report, params):
    """Call the QBO Reports API. Returns parsed JSON. (Token refresh omitted for brevity.)"""
    # import requests
    # tok = refresh_access_token(cfg)
    # url = f"https://quickbooks.api.intuit.com/v3/company/{cfg['realm_id']}/reports/{report}"
    # return requests.get(url, params=params, headers={"Authorization": f"Bearer {tok}",
    #                                                    "Accept": "application/json"}).json()
    raise NotImplementedError("wire QBO OAuth + Reports API; see normalize() for the target shape")


def normalize(pl, pl_monthly, bs, ar):
    """Map raw QBO report payloads → warehouse rows. Pure function, unit-testable."""
    revenue = pl["totalIncome"]
    gross = pl["grossProfit"]
    net = pl["netIncome"]
    opex = pl["totalExpenses"]
    snap = bs["summary"]
    ar_buckets = ar["summary"]["bucketTotals"]
    over_30 = sum(v for k, v in ar_buckets.items() if k in ("31-60", "61-90", "91+"))

    flags = []
    if abs(snap.get("netIncomeYTD", net) - net) > 1:
        flags.append("Balance-sheet net income != P&L net income — reconcile basis.")

    snapshot = {
        "as_of": dt.date.today().isoformat(),
        "revenue_ytd": round(revenue, 2),
        "gross_profit_ytd": round(gross, 2),
        "opex_ytd": round(opex, 2),
        "net_income_ytd": round(net, 2),
        "margin": round(net / revenue, 4) if revenue else None,
        "cash": snap["assetBreakdown"]["cash"],
        "accounts_receivable": snap["assetBreakdown"]["accountsReceivable"],
        "ar_over_30": over_30,
        "equity": snap["totalEquity"],
        "liabilities": snap["totalLiabilities"],
        "current_ratio": snap["ratios"]["currentRatio"],
        "flags": flags,
    }
    monthly = [
        {"month": f"{m['key'][:7]}-01", "revenue": round(m["totalIncome"], 2),
         "net_income": round(m["netIncome"], 2), "expenses": round(m["totalExpenses"], 2)}
        for m in pl_monthly
    ]
    return {"life.finance_biz_snapshot": [snapshot], "life.finance_biz_monthly": monthly}


def pull(cfg):
    today = dt.date.today()
    yr_start = today.replace(month=1, day=1).isoformat()
    pl = _qbo_get(cfg, "ProfitAndLoss", {"start_date": yr_start, "end_date": today.isoformat()})
    pl_m = _qbo_get(cfg, "ProfitAndLoss",
                    {"start_date": yr_start, "end_date": today.isoformat(), "summarize_column_by": "Month"})
    bs = _qbo_get(cfg, "BalanceSheet", {"date": today.isoformat()})
    ar = _qbo_get(cfg, "AgedReceivables", {"date": today.isoformat()})
    return normalize(pl, _monthly_rows(pl_m), bs, ar)


def _monthly_rows(pl_m):
    """Flatten QBO month columns into [{key, totalIncome, netIncome, totalExpenses}]."""
    return pl_m.get("monthlyBreakdown", [])
