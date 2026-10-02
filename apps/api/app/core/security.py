"""
Market AI — API authentication primitives.

Two layers:

1. `require_api_key` — a FastAPI dependency that enforces an `X-API-Key`
   header on write/mutation endpoints when `MARKET_AI_API_KEY` is set in the
   environment. In dev (no env var set) it is a no-op, so running without
   configuration still Just Works for local testing — but production is
   expected to set the key.

2. `caller_id` — a FastAPI dependency that derives a stable per-caller
   identifier from the `X-User-Id` header (defaults to `"public"`). It is
   used to scope paper-trading accounts, alert rules, etc. per browser /
   deployment, instead of sharing one global singleton across all users.
"""

from __future__ import annotations

import os
import re
from typing import Optional

from fastapi import Header, HTTPException, status

_API_KEY_ENV = "MARKET_AI_API_KEY"
_SAFE_USER_ID = re.compile(r"^[A-Za-z0-9_.:@-]{1,64}$")


def require_api_key(x_api_key: Optional[str] = Header(default=None)) -> None:
    """Enforce the X-API-Key header when `MARKET_AI_API_KEY` is set.

    - Env var unset  → auth is disabled (dev mode).
    - Env var set    → header must match exactly or the request is rejected
                       with 401.
    """
    expected = os.getenv(_API_KEY_ENV)
    if not expected:
        return
    if not x_api_key or x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )


def caller_id(x_user_id: Optional[str] = Header(default=None)) -> str:
    """Return a sanitized per-caller identifier for state scoping.

    Defaults to `"public"` when the header is not provided. Rejects values
    that contain characters outside a conservative allowlist, to make it
    safe for use as a dictionary / database key.
    """
    if not x_user_id:
        return "public"
    uid = x_user_id.strip()
    if not _SAFE_USER_ID.match(uid):
        raise HTTPException(status_code=400, detail="Invalid X-User-Id header.")
    return uid
