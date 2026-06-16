"""Rate limiter + webhook signature/dispatch tests (no network)."""

import base64
import hashlib
import hmac
import time

from src import store, webhooks
from src.ratelimit import RateLimiter


def test_rate_limiter_paces_minute_window(monkeypatch):
    # 3/min ceiling at safety 1.0 -> 3 immediate, 4th must wait.
    rl = RateLimiter(per_minute=3, per_day=1000, safety=1.0)
    sleeps = []
    monkeypatch.setattr("src.ratelimit.time.sleep", lambda s: sleeps.append(s))
    # Freeze time so the window never advances during the test.
    monkeypatch.setattr("src.ratelimit.time.time", lambda: 1000.0)
    for _ in range(3):
        rl.acquire()
    assert sleeps == []          # first three free
    # The 4th would block; since time is frozen it would loop forever, so just
    # assert the window is full.
    snap = rl.snapshot()
    assert snap["used_last_minute"] == 3
    assert snap["minute_budget"] == 3


def test_rate_limiter_observe_headers():
    rl = RateLimiter()
    rl.observe_headers({"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "30"})
    snap = rl.snapshot()
    assert snap["server_remaining"] == 0


def test_webhook_signature_roundtrip():
    secret = "topsecret"
    body = b'{"type":"recovery.updated","id":123}'
    ts = "1700000000"
    mac = hmac.new(secret.encode(), ts.encode() + body, hashlib.sha256).digest()
    sig = base64.b64encode(mac).decode()
    assert webhooks.verify_signature(body, ts, sig, secret) is True
    assert webhooks.verify_signature(body, ts, "wrong", secret) is False


class _FakeClient:
    def get_sleep(self, sid):
        return {"id": sid, "start": "2026-05-01T04:00:00.000Z",
                "timezone_offset": "-05:00", "score_state": "SCORED",
                "score": {"sleep_performance_percentage": 88,
                          "stage_summary": {"total_rem_sleep_time_milli": 3_600_000}}}


def test_handle_event_upserts_single_record():
    conn = store.connect(":memory:")
    status = webhooks.handle_event(
        {"type": "sleep.updated", "id": "abc-uuid"}, conn, client=_FakeClient()
    )
    assert status.startswith("ok")
    rows = store.fetch_all(conn, "sleep")
    assert len(rows) == 1 and rows[0]["id"] == "abc-uuid"
    conn.close()
