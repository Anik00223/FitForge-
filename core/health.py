"""Operational endpoints for Kubernetes probes and load-balancer health.

Three independent endpoints are exposed:

* ``/livez``  – liveness probe.  Returns 200 as long as the Python
  process can answer HTTP.  Used by the kubelet to decide when to
  restart a stuck container.
* ``/readyz`` – readiness probe.  Verifies the database connection,
  cache backend, and Celery broker are reachable.  Used by the
  Service load-balancer to decide whether to send traffic to the pod.
* ``/healthz`` – human-friendly combined health page (HTML or JSON
  based on the ``Accept`` header).  Useful for uptime monitors and
  on-call dashboards.

The views deliberately avoid touching the ORM more than once per call
to keep probe latency < 50 ms even on a busy node.
"""
from __future__ import annotations

import logging
import time
from typing import Any, Callable

from django.conf import settings
from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from core.utils import check_redis


logger = logging.getLogger("fitforge.health")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _check_database() -> tuple[bool, str]:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return True, "ok"
    except Exception as exc:  # pragma: no cover - depends on environment
        return False, f"{type(exc).__name__}: {exc}"


def _check_cache() -> tuple[bool, str]:
    try:
        from django.core.cache import cache

        cache.set("fitforge:health:ping", "pong", timeout=10)
        value = cache.get("fitforge:health:ping")
        if value != "pong":
            return False, "roundtrip failed"
        return True, "ok"
    except Exception as exc:  # pragma: no cover
        return False, f"{type(exc).__name__}: {exc}"


def _check_broker() -> tuple[bool, str]:
    if not getattr(settings, "CELERY_BROKER_URL", ""):
        return True, "disabled"
    try:
        ok, detail = check_redis(settings.CELERY_BROKER_URL)
        return ok, detail
    except Exception as exc:  # pragma: no cover
        return False, f"{type(exc).__name__}: {exc}"


CHECKS: dict[str, Callable[[], tuple[bool, str]]] = {
    "database": _check_database,
    "cache": _check_cache,
    "broker": _check_broker,
}


def _run_checks() -> tuple[int, dict[str, Any]]:
    started = time.perf_counter()
    results: dict[str, dict[str, Any]] = {}
    for name, check in CHECKS.items():
        ok, detail = check()
        results[name] = {"ok": ok, "detail": detail}
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    all_ok = all(r["ok"] for r in results.values())
    status = 200 if all_ok else 503
    payload = {
        "status": "ok" if all_ok else "degraded",
        "checks": results,
        "latency_ms": latency_ms,
        "release": getattr(settings, "SENTRY_RELEASE", "") or "dev",
        "environment": getattr(settings, "SENTRY_ENVIRONMENT", "unknown"),
    }
    return status, payload


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------
@csrf_exempt
@require_GET
@never_cache
def livez(request: HttpRequest) -> JsonResponse:
    """Liveness probe – the process is up and the WSGI handler is responsive."""
    return JsonResponse({"status": "ok"}, status=200)


@csrf_exempt
@require_GET
@never_cache
def readyz(request: HttpRequest) -> JsonResponse:
    """Readiness probe – the pod can serve real traffic."""
    status, payload = _run_checks()
    if status != 200:
        logger.warning("readyz reported degraded state: %s", payload)
    return JsonResponse(payload, status=status)


@csrf_exempt
@require_GET
@never_cache
def healthz(request: HttpRequest) -> JsonResponse:
    """Combined health page for humans and uptime monitors."""
    status, payload = _run_checks()
    payload["name"] = "fitforge"
    accept = request.META.get("HTTP_ACCEPT", "")
    if "text/html" in accept and "application/json" not in accept:
        return render(request, "errors/health.html", {"payload": payload}, status=status)
    return JsonResponse(payload, status=status)
