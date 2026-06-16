"""OAuth 2.0 Authorization Code flow + encrypted local token storage.

Tokens are persisted to ``data/whoop_tokens.enc``, encrypted with a Fernet
key derived from the ``WHOOP_TOKEN_KEY`` passphrase. Tokens and the client
secret are never logged or printed.
"""

from __future__ import annotations

import base64
import http.server
import json
import logging
import secrets
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from typing import Optional

import requests

import config

log = logging.getLogger("whoop.auth")

# Static salt: the secret strength comes from WHOOP_TOKEN_KEY. A fixed salt is
# acceptable here because the encrypted file is local and single-user; it keeps
# the derived key stable across runs without storing extra state.
_KDF_SALT = b"whoop-tracker-token-store-v1"
# Refresh the access token this many seconds before it actually expires.
_EXPIRY_SKEW = 120


def _fernet():
    # Imported lazily so the rest of the package imports even where the
    # cryptography backend is unavailable; only token I/O needs it.
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    if not config.TOKEN_KEY:
        raise RuntimeError(
            "WHOOP_TOKEN_KEY is not set. Add it to your .env before running auth."
        )
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=_KDF_SALT,
        iterations=390_000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(config.TOKEN_KEY.encode("utf-8")))
    return Fernet(key)


@dataclass
class Tokens:
    access_token: str
    refresh_token: str
    expires_at: float  # epoch seconds
    scope: str = ""
    token_type: str = "bearer"

    @property
    def expired(self) -> bool:
        return time.time() >= (self.expires_at - _EXPIRY_SKEW)

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    @classmethod
    def from_json(cls, raw: str) -> "Tokens":
        return cls(**json.loads(raw))


class TokenStore:
    """Encrypted-at-rest token persistence."""

    def __init__(self, path=config.TOKEN_PATH):
        self.path = path

    def save(self, tokens: Tokens) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        blob = _fernet().encrypt(tokens.to_json().encode("utf-8"))
        self.path.write_bytes(blob)
        log.info("Saved encrypted tokens (scope=%s).", tokens.scope or "n/a")

    def load(self) -> Optional[Tokens]:
        if not self.path.exists():
            return None
        from cryptography.fernet import InvalidToken
        try:
            raw = _fernet().decrypt(self.path.read_bytes())
        except InvalidToken as exc:  # wrong passphrase / corrupt file
            raise RuntimeError(
                "Could not decrypt token file. Is WHOOP_TOKEN_KEY correct?"
            ) from exc
        return Tokens.from_json(raw.decode("utf-8"))


def _build_authorize_url(state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": config.CLIENT_ID,
        "redirect_uri": config.REDIRECT_URI,
        "scope": " ".join(config.SCOPES),
        "state": state,
    }
    return f"{config.OAUTH_AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """One-shot handler that captures the ?code=...&state=... callback."""

    result: dict = {}

    def do_GET(self):  # noqa: N802 (http.server API)
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        _CallbackHandler.result = {k: v[0] for k, v in qs.items()}
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        ok = "code" in _CallbackHandler.result
        body = (
            "<h2>WHOOP authorization complete.</h2><p>You can close this tab.</p>"
            if ok
            else "<h2>Authorization failed.</h2><p>Check the terminal.</p>"
        )
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *args):  # silence default stderr logging
        return


def _capture_auth_code(state: str, timeout: int = 300) -> str:
    parsed = urllib.parse.urlparse(config.REDIRECT_URI)
    host = parsed.hostname or "localhost"
    port = parsed.port or 8080
    server = http.server.HTTPServer((host, port), _CallbackHandler)
    server.timeout = timeout

    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    thread.join(timeout)
    server.server_close()

    result = _CallbackHandler.result
    if not result:
        raise TimeoutError("Timed out waiting for the OAuth callback.")
    if result.get("state") != state:
        raise RuntimeError("OAuth state mismatch — possible CSRF; aborting.")
    if "code" not in result:
        raise RuntimeError(f"OAuth error: {result.get('error', 'no code returned')}")
    return result["code"]


def _exchange(grant: dict) -> Tokens:
    """POST to the token endpoint and normalize the response into Tokens."""
    resp = requests.post(config.OAUTH_TOKEN_URL, data=grant, timeout=30)
    if resp.status_code != 200:
        # Never echo the body verbatim (may contain tokens). Status only.
        raise RuntimeError(f"Token endpoint returned HTTP {resp.status_code}.")
    payload = resp.json()
    return Tokens(
        access_token=payload["access_token"],
        # WHOOP rotates refresh tokens; fall back to the prior one if omitted.
        refresh_token=payload.get("refresh_token", grant.get("refresh_token", "")),
        expires_at=time.time() + float(payload.get("expires_in", 3600)),
        scope=payload.get("scope", " ".join(config.SCOPES)),
        token_type=payload.get("token_type", "bearer"),
    )


def run_oauth_flow(open_browser: bool = True) -> Tokens:
    """Full interactive Authorization Code flow; stores and returns tokens."""
    if not (config.CLIENT_ID and config.CLIENT_SECRET):
        raise RuntimeError("WHOOP_CLIENT_ID / WHOOP_CLIENT_SECRET not set in .env.")

    state = secrets.token_urlsafe(24)
    url = _build_authorize_url(state)
    print("Opening WHOOP authorization page. If it doesn't open, visit:\n", url)
    if open_browser:
        try:
            webbrowser.open(url)
        except Exception:  # headless environments
            pass

    code = _capture_auth_code(state)
    tokens = _exchange(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config.REDIRECT_URI,
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
        }
    )
    TokenStore().save(tokens)
    print("Authorization successful; tokens stored encrypted.")
    return tokens


def refresh(tokens: Tokens) -> Tokens:
    """Exchange a refresh token for a new access token; persist the result."""
    if not tokens.refresh_token:
        raise RuntimeError("No refresh token available; re-run `whoop auth`.")
    refreshed = _exchange(
        {
            "grant_type": "refresh_token",
            "refresh_token": tokens.refresh_token,
            "client_id": config.CLIENT_ID,
            "client_secret": config.CLIENT_SECRET,
            "scope": " ".join(config.SCOPES),
        }
    )
    TokenStore().save(refreshed)
    log.info("Refreshed access token.")
    return refreshed


def get_valid_access_token() -> str:
    """Return a usable access token, refreshing transparently if expired."""
    store = TokenStore()
    tokens = store.load()
    if tokens is None:
        raise RuntimeError("No stored tokens. Run `whoop auth` first.")
    if tokens.expired:
        tokens = refresh(tokens)
    return tokens.access_token
