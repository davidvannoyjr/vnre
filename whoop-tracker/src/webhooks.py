"""WHOOP webhook receiver — push beats polling.

WHOOP can POST an event whenever a record is created/updated, instead of you
polling. Each event is HMAC-SHA256 signed with your client secret over
``timestamp + raw_body`` and delivered with ``X-WHOOP-Signature`` and
``X-WHOOP-Signature-Timestamp`` headers.

On a verified event we fetch ONLY the affected record (one request) and upsert
it — far cheaper than a windowed poll. Run this behind HTTPS (a reverse proxy
or tunnel) and register the public URL in your WHOOP app settings.

This uses the stdlib http.server so there is no web-framework dependency. For
the SaaS path, port the verify+dispatch functions into your async framework of
choice; they are intentionally framework-agnostic.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import http.server
import json
import logging
from typing import Optional

import config
from . import store
from .client import WhoopClient

log = logging.getLogger("whoop.webhooks")


def verify_signature(raw_body: bytes, timestamp: str, signature: str,
                     secret: Optional[str] = None) -> bool:
    """Constant-time verification of a WHOOP webhook signature."""
    secret = secret or config.CLIENT_SECRET
    if not (secret and timestamp and signature):
        return False
    mac = hmac.new(secret.encode("utf-8"),
                   timestamp.encode("utf-8") + raw_body,
                   hashlib.sha256).digest()
    expected = base64.b64encode(mac).decode("utf-8")
    return hmac.compare_digest(expected, signature)


def handle_event(event: dict, conn, client: Optional[WhoopClient] = None) -> str:
    """Fetch the single affected record and upsert it. Returns a status string."""
    client = client or WhoopClient()
    etype = (event.get("type") or "").lower()
    rid = event.get("id")
    if rid is None:
        return "ignored: no id"

    try:
        if etype.startswith("sleep"):
            store.upsert_sleep(conn, client.get_sleep(rid))
        elif etype.startswith("workout"):
            store.upsert_workout(conn, client.get_workout(rid))
        elif etype.startswith("recovery"):
            # Recovery events carry the cycle id in v2; pull its recovery.
            cid = event.get("cycle_id", rid)
            store.upsert_recovery(conn, client.get_recovery_for_cycle(cid))
        elif etype.startswith("cycle"):
            store.upsert_cycle(conn, client.get_cycle(rid))
        else:
            return f"ignored: unknown type {etype}"
    except Exception as exc:  # log and ack so WHOOP doesn't hammer retries
        log.exception("Webhook handler error for %s", etype)
        return f"error: {exc}"

    conn.commit()
    log.info("Applied webhook %s id=%s.", etype, rid)
    return f"ok: {etype}"


class _Handler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        ts = self.headers.get("X-WHOOP-Signature-Timestamp", "")
        sig = self.headers.get("X-WHOOP-Signature", "")
        if not verify_signature(raw, ts, sig):
            self.send_response(401)
            self.end_headers()
            self.wfile.write(b"invalid signature")
            return
        try:
            event = json.loads(raw.decode("utf-8"))
        except ValueError:
            self.send_response(400)
            self.end_headers()
            return
        conn = store.connect()
        try:
            handle_event(event, conn)
        finally:
            conn.close()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        return


def serve(host: str = "0.0.0.0", port: int = 8099) -> None:
    """Run the webhook receiver (blocking)."""
    logging.basicConfig(level=logging.INFO)
    server = http.server.ThreadingHTTPServer((host, port), _Handler)
    log.info("WHOOP webhook receiver listening on %s:%d", host, port)
    server.serve_forever()


if __name__ == "__main__":
    serve()
