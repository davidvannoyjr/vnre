"""Credit Karma adapter — personal credit (LIVE, bands only).

Exposes score band + per-factor standings. The numeric score is NOT available from the
connector by design — store bands only. Live pull 2026-06-14: band GOOD.
"""
import datetime as dt

FACTOR_LABELS = {
    "PAYMENT_HISTORY": "Payment history", "CREDIT_CARD_UTILIZATION": "Card utilization",
    "DEROGATORY_MARKS": "Derogatory marks", "CREDIT_HISTORY_AGE": "Credit age",
    "TOTAL_ACCOUNTS": "Total accounts", "HARD_INQUIRIES": "Hard inquiries",
}


def normalize(payload):
    as_of = dt.date.today().isoformat()
    return {"life.credit_factors": [{
        "as_of": as_of, "band": payload["scoreBand"], "model": "VantageScore 3.0 (TransUnion)",
        "factor": FACTOR_LABELS.get(f["factorName"], f["factorName"]),
        "impact": f["impactLevel"], "standing": f["standing"],
    } for f in payload["creditFactors"]]}


def pull(cfg):
    raise NotImplementedError("wire Credit Karma connector; normalize() defines the target shape")
