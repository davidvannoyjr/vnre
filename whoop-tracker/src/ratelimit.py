"""Quota-aware rate limiting for the WHOOP API.

WHOOP enforces app-wide limits of 100 requests/minute and 10,000/day. This
limiter is proactive (it paces requests so we rarely hit a 429 at all) and
reactive (it absorbs server-reported limits via the X-RateLimit headers).

Sliding-window counters keep it accurate without a background thread. It is
single-process; for the future multi-tenant SaaS path, swap the in-memory
deques for a shared Redis token bucket keyed per app — the call sites do not
change.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import deque
from typing import Optional

log = logging.getLogger("whoop.ratelimit")


class RateLimiter:
    def __init__(self, per_minute: int = 100, per_day: int = 10_000,
                 safety: float = 0.9):
        # Pace to `safety` of the published ceiling to leave headroom for other
        # clients sharing the app-wide quota.
        self.per_minute = max(1, int(per_minute * safety))
        self.per_day = max(1, int(per_day * safety))
        self._minute = deque()  # timestamps (epoch s) of recent requests
        self._day = deque()
        self._lock = threading.Lock()
        # Server-reported state from X-RateLimit headers.
        self._server_remaining: Optional[int] = None
        self._server_reset_at: Optional[float] = None

    def _prune(self, now: float) -> None:
        while self._minute and now - self._minute[0] >= 60:
            self._minute.popleft()
        while self._day and now - self._day[0] >= 86_400:
            self._day.popleft()

    def acquire(self) -> None:
        """Block until a request may be sent without breaching a window."""
        while True:
            with self._lock:
                now = time.time()
                self._prune(now)

                wait = 0.0
                if len(self._minute) >= self.per_minute:
                    wait = max(wait, 60 - (now - self._minute[0]))
                if len(self._day) >= self.per_day:
                    wait = max(wait, 86_400 - (now - self._day[0]))
                # Honor a server-reported exhaustion window.
                if (self._server_remaining is not None and self._server_remaining <= 0
                        and self._server_reset_at and self._server_reset_at > now):
                    wait = max(wait, self._server_reset_at - now)

                if wait <= 0:
                    self._minute.append(now)
                    self._day.append(now)
                    return
            log.info("Rate limit pacing: sleeping %.1fs.", wait)
            time.sleep(min(wait, 60) + 0.05)

    def observe_headers(self, headers) -> None:
        """Update state from X-RateLimit-* response headers when present."""
        remaining = headers.get("X-RateLimit-Remaining")
        reset = headers.get("X-RateLimit-Reset")
        if remaining is not None:
            try:
                self._server_remaining = int(remaining)
            except ValueError:
                pass
        if reset is not None:
            try:
                # Reset may be epoch seconds or seconds-until-reset; treat small
                # values as a delta from now.
                val = float(reset)
                self._server_reset_at = val if val > 1e6 else time.time() + val
            except ValueError:
                pass

    def snapshot(self) -> dict:
        with self._lock:
            now = time.time()
            self._prune(now)
            return {
                "used_last_minute": len(self._minute),
                "used_last_day": len(self._day),
                "minute_budget": self.per_minute,
                "day_budget": self.per_day,
                "server_remaining": self._server_remaining,
            }
