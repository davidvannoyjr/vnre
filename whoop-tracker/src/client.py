"""WHOOP v2 REST client: auth header injection, pagination, and backoff.

Pagination contract (v2): collection responses look like
``{"records": [...], "next_token": "..."}``. Send the cursor back as the
``nextToken`` query param. ``limit`` caps at 25. ``start``/``end`` are ISO-8601
UTC bounds. Records are returned newest-first.
"""

from __future__ import annotations

import logging
import random
import time
from typing import Dict, Iterator, Optional

import requests

import config
from . import auth
from .ratelimit import RateLimiter

log = logging.getLogger("whoop.client")

_MAX_RETRIES = 6
_BACKOFF_BASE = 1.5  # seconds; doubled each retry
_BACKOFF_CAP = 60.0  # max single backoff sleep


class WhoopClient:
    def __init__(self, session: Optional[requests.Session] = None,
                 limiter: Optional[RateLimiter] = None):
        self.session = session or requests.Session()
        # Proactively pace to WHOOP's 100/min + 10k/day app-wide quota.
        self.limiter = limiter or RateLimiter(per_minute=100, per_day=10_000)

    # -- low level ---------------------------------------------------------
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {auth.get_valid_access_token()}",
            "Accept": "application/json",
        }

    def _request(self, path: str, params: Optional[dict] = None) -> dict:
        """GET with retry/backoff. Honors Retry-After on 429/503."""
        url = f"{config.API_BASE}{path}"
        attempt = 0
        while True:
            attempt += 1
            self.limiter.acquire()  # proactive quota pacing
            resp = self.session.get(
                url, headers=self._headers(), params=params, timeout=30
            )
            # Feed server-reported quota back into the limiter.
            self.limiter.observe_headers(resp.headers)

            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 401 and attempt == 1:
                # Token may have just expired mid-run; force a refresh + retry.
                log.info("401 received; refreshing token and retrying.")
                continue

            if resp.status_code in (429, 500, 502, 503, 504):
                if attempt > _MAX_RETRIES:
                    raise RuntimeError(
                        f"GET {path} failed after {_MAX_RETRIES} retries "
                        f"(HTTP {resp.status_code})."
                    )
                delay = self._backoff_delay(resp, attempt)
                log.warning(
                    "HTTP %s on %s; backing off %.1fs (attempt %d/%d).",
                    resp.status_code, path, delay, attempt, _MAX_RETRIES,
                )
                time.sleep(delay)
                continue

            raise RuntimeError(f"GET {path} -> HTTP {resp.status_code}: {resp.text[:200]}")

    @staticmethod
    def _backoff_delay(resp: requests.Response, attempt: int) -> float:
        """Honor Retry-After if present, else exponential backoff with jitter."""
        retry_after = resp.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return float(retry_after)
            except ValueError:
                pass
        base = min(_BACKOFF_BASE * (2 ** (attempt - 1)), _BACKOFF_CAP)
        # Full jitter avoids thundering-herd retries against the shared quota.
        return random.uniform(0, base)

    # -- singletons --------------------------------------------------------
    def get_profile(self) -> dict:
        return self._request(config.ENDPOINTS["profile"])

    def get_body(self) -> dict:
        return self._request(config.ENDPOINTS["body"])

    # -- collections -------------------------------------------------------
    def paginate(
        self,
        path: str,
        start: Optional[str] = None,
        end: Optional[str] = None,
    ) -> Iterator[dict]:
        """Yield every record across all pages for a collection endpoint."""
        next_token: Optional[str] = None
        while True:
            params: Dict[str, object] = {"limit": config.PAGE_LIMIT}
            if start:
                params["start"] = start
            if end:
                params["end"] = end
            if next_token:
                params["nextToken"] = next_token

            page = self._request(path, params=params)
            for record in page.get("records", []):
                yield record

            next_token = page.get("next_token")
            if not next_token:
                break

    def iter_cycles(self, start=None, end=None) -> Iterator[dict]:
        return self.paginate(config.ENDPOINTS["cycles"], start, end)

    def iter_recovery(self, start=None, end=None) -> Iterator[dict]:
        return self.paginate(config.ENDPOINTS["recovery"], start, end)

    def iter_sleep(self, start=None, end=None) -> Iterator[dict]:
        return self.paginate(config.ENDPOINTS["sleep"], start, end)

    def iter_workouts(self, start=None, end=None) -> Iterator[dict]:
        return self.paginate(config.ENDPOINTS["workout"], start, end)

    # -- single records (used by the webhook receiver; minimal quota) -------
    def get_sleep(self, sleep_id: str) -> dict:
        return self._request(f"/v2/activity/sleep/{sleep_id}")

    def get_workout(self, workout_id: str) -> dict:
        return self._request(f"/v2/activity/workout/{workout_id}")

    def get_cycle(self, cycle_id) -> dict:
        return self._request(f"/v2/cycle/{cycle_id}")

    def get_recovery_for_cycle(self, cycle_id) -> dict:
        return self._request(f"/v2/cycle/{cycle_id}/recovery")
