"""Withings adapter — body measurements (PENDING DEVICE).

Withings API (OAuth2): measure?action=getmeas (weight, fat %), heart?action=list (BP).
Writes life.body_measurements.
"""


def pull(cfg):
    raise NotImplementedError("buy Withings scale + BPM, authorize OAuth, map getmeas → life.body_measurements")
