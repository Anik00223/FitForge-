"""Supabase client helpers using the official Python client with a safe fallback.

This module exposes a small helper to create a Supabase client and to
retrieve the Supabase user associated with an access token. It prefers
the official `supabase` client when available and falls back to the
Auth REST endpoint via `requests` if needed.
"""
from typing import Optional, Dict
from django.conf import settings
import requests

try:
    from supabase import create_client
except Exception:  # pragma: no cover - optional dependency
    create_client = None

SUPABASE_URL = getattr(settings, "SUPABASE_URL", "")
SUPABASE_PUBLISHABLE_KEY = getattr(settings, "SUPABASE_PUBLISHABLE_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")


def create_supabase_client(service_role: bool = False):
    """Return a supabase client or None if the dependency/keys are missing."""
    key = SUPABASE_SERVICE_ROLE_KEY if service_role else SUPABASE_PUBLISHABLE_KEY
    if not create_client or not SUPABASE_URL or not key:
        return None
    return create_client(SUPABASE_URL, key)


def get_user_from_token(token: str, service_role: bool = True) -> Optional[Dict]:
    """Return the Supabase user dict for the given access token.

    Attempts to use the official client where possible, otherwise falls
    back to the auth REST endpoint.
    """
    if not token or not SUPABASE_URL:
        return None

    client = create_supabase_client(service_role=service_role)
    if client:
        try:
            auth = getattr(client, "auth", None)
            if auth:
                # try possible API shapes (auth.api.get_user or auth.get_user)
                api = getattr(auth, "api", None)
                if api and hasattr(api, "get_user"):
                    res = api.get_user(token)
                    if isinstance(res, dict) and "user" in res:
                        return res["user"]
                    return res
                if hasattr(auth, "get_user"):
                    res = auth.get_user(token)
                    if isinstance(res, dict) and "user" in res:
                        return res["user"]
                    if hasattr(res, "user"):
                        return getattr(res, "user")
                    return res
        except Exception:
            # fall through to REST fallback
            pass

    # REST fallback (works with publishable or service role key)
    headers = {
        "Authorization": f"Bearer {token}",
        "apikey": SUPABASE_PUBLISHABLE_KEY or SUPABASE_SERVICE_ROLE_KEY,
    }
    try:
        resp = requests.get(f"{SUPABASE_URL.rstrip('/')}/auth/v1/user", headers=headers, timeout=5)
        if resp.status_code != 200:
            return None
        return resp.json()
    except requests.RequestException:
        return None
