"""Atomic, Redis-backed rate limiter for FitForge views.

Uses a sliding-window counter stored as an integer key in Redis.
Atomic INCR + EXPIRE avoids the race condition of the previous
list-based implementation.  The window bucket resets every
`window` seconds so the limit is approximate (±1 bucket period)
which is acceptable for abuse prevention.
"""
from __future__ import annotations

import logging
from functools import wraps

from django.contrib import messages
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone

logger = logging.getLogger("fitforge.rate_limit")


def rate_limit(
    key_prefix: str,
    limit: int,
    window: int,
    html_redirect: bool = False,
):
    """Decorator that enforces a per-user rate limit.

    Args:
        key_prefix:    Short identifier baked into the cache key, e.g.
                       ``"planner_generate"``.
        limit:         Maximum number of calls allowed within ``window``.
        window:        Time bucket size in seconds (e.g. 3600 = 1 hour).
        html_redirect: If True, flash a Django message and redirect back
                       to the same path instead of returning a JSON 429.
                       Use for HTML views; leave False for AJAX/API views.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"error": "Unauthorized"}, status=401)

            # Bucket key: resets every `window` seconds — atomic, no race.
            bucket = int(timezone.now().timestamp()) // window
            cache_key = f"rl:{key_prefix}:{request.user.pk}:{bucket}"

            # cache.add is atomic: sets key only if it doesn't exist.
            cache.add(cache_key, 0, timeout=window * 2)
            count = cache.incr(cache_key)

            if count > limit:
                logger.warning(
                    "Rate limit hit key=%s user=%s count=%d limit=%d",
                    key_prefix,
                    request.user.pk,
                    count,
                    limit,
                )
                if html_redirect:
                    messages.error(
                        request,
                        f"You have reached the limit of {limit} requests. "
                        f"Please try again later.",
                    )
                    return redirect(request.path)
                return JsonResponse(
                    {
                        "error": "Rate limit exceeded.",
                        "limit": limit,
                        "window_seconds": window,
                    },
                    status=429,
                )

            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
