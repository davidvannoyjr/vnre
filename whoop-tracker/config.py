"""Central configuration: environment loading, paths, and WHOOP constants.

NOTE ON API VERSION
-------------------
The original build spec referenced the WHOOP **v1** API. As of the build
date the v1 API has been fully deprecated (WHOOP retired v1 in Oct 2025) and
**v2** is the only live version. Per the spec's "live docs win" rule this
project targets v2:

  * IDs for sleep and workout records are now **UUID strings** (v1 used ints).
  * Cycle ids remain integers; recovery is keyed by ``cycle_id`` and carries
    the associated sleep's UUID in ``sleep_id``.
  * Score fields are nested under a ``score`` object alongside ``score_state``.
  * Pagination returns ``next_token`` in the body; requests send ``nextToken``,
    ``limit`` (max 25), ``start`` and ``end``.

Everything below is verified against https://developer.whoop.com/api (v2).
"""

from __future__ import annotations

import os
from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "whoop.db"
TOKEN_PATH = DATA_DIR / "whoop_tokens.enc"
LOG_PATH = DATA_DIR / "whoop.log"
WORKBOOK_PATH = ROOT / "whoop_dashboard.xlsx"
INTERVENTIONS_CSV = DATA_DIR / "interventions.csv"


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (avoids a python-dotenv dependency).

    Lines like ``KEY=value`` are loaded into os.environ unless already set.
    Blank lines and ``#`` comments are ignored. Existing env vars win so the
    process environment can override the file.
    """
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv(ROOT / ".env")

# --------------------------------------------------------------------------
# OAuth / API constants
# --------------------------------------------------------------------------
API_BASE = "https://api.prod.whoop.com/developer"
OAUTH_AUTHORIZE_URL = "https://api.prod.whoop.com/oauth/oauth2/auth"
OAUTH_TOKEN_URL = "https://api.prod.whoop.com/oauth/oauth2/token"

# `offline` is required to be issued a refresh token.
SCOPES = [
    "read:profile",
    "read:body_measurement",
    "read:cycles",
    "read:recovery",
    "read:sleep",
    "read:workout",
    "offline",
]

# Collection endpoints (paginated). Profile + body are singletons.
ENDPOINTS = {
    "profile": "/v2/user/profile/basic",
    "body": "/v2/user/measurement/body",
    "cycles": "/v2/cycle",
    "recovery": "/v2/recovery",
    "sleep": "/v2/activity/sleep",
    "workout": "/v2/activity/workout",
}

# Resources that support incremental (watermarked) collection sync.
COLLECTION_RESOURCES = ["cycles", "recovery", "sleep", "workout"]

PAGE_LIMIT = 25  # WHOOP max page size.

# Env-backed credentials (may be empty until `whoop auth` is run).
CLIENT_ID = os.environ.get("WHOOP_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("WHOOP_CLIENT_SECRET", "")
REDIRECT_URI = os.environ.get("WHOOP_REDIRECT_URI", "http://localhost:8080/callback")
TOKEN_KEY = os.environ.get("WHOOP_TOKEN_KEY", "")

# --------------------------------------------------------------------------
# Domain constants
# --------------------------------------------------------------------------
KJ_TO_CAL = 0.239006  # kilojoules -> kilocalories

# WHOOP-style recovery thresholds (also surfaced in the workbook Config tab).
RECOVERY_RED_MAX = 33      # 0-33  -> red
RECOVERY_YELLOW_MAX = 66   # 34-66 -> yellow; 67+ -> green

# Anomaly threshold on the 30-day z-score.
Z_ANOMALY = 1.5

# Cycle -> calendar-day mapping rule, documented once and reused in the
# workbook Config tab and README.
CYCLE_DAY_RULE = (
    "Each physiological cycle is assigned to the calendar day of the LOCAL "
    "date of its start timestamp (cycle.start shifted by cycle.timezone_offset). "
    "A WHOOP cycle does not equal a calendar day; this rule makes the daily "
    "view stable and matches how the WHOOP app attributes a day's recovery."
)
