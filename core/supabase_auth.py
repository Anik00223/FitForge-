"""Supabase token verification and Django mapping helpers.

This module provides a tiny helper to verify a Supabase access token
via the Supabase Auth REST endpoint and map/create a Django user.

Usage (middleware): include `core.supabase_auth.SupabaseAuthMiddleware`
in `MIDDLEWARE` (after AuthenticationMiddleware) to populate
`request.supabase_user` and to map the request to a Django `request.user`.
"""
from typing import Optional, Dict
from django.conf import settings
from django.contrib.auth import get_user_model
from core.supabase_client import get_user_from_token

User = get_user_model()

SUPABASE_URL = getattr(settings, "SUPABASE_URL", "")
SUPABASE_PUBLISHABLE_KEY = getattr(settings, "SUPABASE_PUBLISHABLE_KEY", "")
SUPABASE_SERVICE_ROLE_KEY = getattr(settings, "SUPABASE_SERVICE_ROLE_KEY", "")


def get_supabase_user(access_token: str) -> Optional[Dict]:
    """Return the Supabase user object for a valid access token or None.

    Prefer the official client wrapper in `core.supabase_client` with a
    fallback to the REST endpoint if the client isn't available.
    """
    if not access_token:
        return None
    return get_user_from_token(access_token, service_role=True)


def get_or_create_user(supabase_user: Dict) -> Optional[User]:
    """Map the Supabase user to a Django user (create if necessary)."""
    if not supabase_user:
        return None

    email = supabase_user.get("email")
    if not email:
        return None

    username = (
        supabase_user.get("user_metadata", {}).get("full_name")
        or email.split("@")[0]
    )

    user, created = User.objects.get_or_create(
        email=email,
        defaults={"username": username, "is_active": True},
    )

    if created:
        # Ensure unusable password for externally-authenticated users
        user.set_unusable_password()
        user.save()

    return user


from django.utils.deprecation import MiddlewareMixin


class SupabaseAuthMiddleware(MiddlewareMixin):
    """Middleware that accepts `Authorization: Bearer <token>` and maps it.

    - If a valid Supabase access token is present, `request.supabase_user`
      will contain the Supabase user JSON and `request.user` will be the
      associated (or newly-created) Django user.
    - Does not create a Django session; this is token-based per-request auth.
    """

    def process_request(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return None

        sup_user = get_supabase_user(token)
        if not sup_user:
            return None

        user = get_or_create_user(sup_user)
        if user:
            request.supabase_user = sup_user
            request.user = user

        return None
