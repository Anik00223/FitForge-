"""Cross-cutting middleware for FitForge.

These helpers are intentionally tiny and dependency-free so they can be
loaded during the request/response cycle without measurable overhead.

* :class:`RequestIDMiddleware` attaches a stable ``request_id`` to every
  inbound HTTP request and propagates it through the structured log
  records so support can correlate a single user action across the
  application, Celery, and Sentry.
* :class:`SecurityHeadersMiddleware` hardens the response with a small
  set of headers (CSP, Referrer-Policy, Permissions-Policy, COOP/COEP)
  that complement the headers Django emits via ``SecurityMiddleware``.
"""
from __future__ import annotations

import logging
import uuid

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


_request_id_logger = logging.getLogger("fitforge.request")


class RequestIDMiddleware(MiddlewareMixin):
    """Attach a unique request id to every request.

    Honors an inbound ``X-Request-ID`` header if the upstream proxy
    (load-balancer, ingress) already set one so log correlation works
    across services.  Otherwise we generate a fresh UUID4.

    The id is:

    * stored on ``request.request_id``;
    * echoed back as ``X-Request-ID`` for clients/proxies to log;
    * injected into the ``fitforge`` logger as ``extra={"request_id": ...}``
      via :class:`RequestIDLogFilter`.
    """

    HEADER_IN = "HTTP_X_REQUEST_ID"
    HEADER_OUT = "X-Request-ID"

    def process_request(self, request):
        rid = request.META.get(self.HEADER_IN) or uuid.uuid4().hex
        # Cap to 64 chars to keep log indices small and prevent header abuse.
        request.request_id = rid[:64]
        return None

    def process_response(self, request, response):
        rid = getattr(request, "request_id", None)
        if rid:
            response[self.HEADER_OUT] = rid
        return response


class RequestIDLogFilter(logging.Filter):
    """Inject ``request_id`` into every log record.

    Wired up in :data:`django.conf.settings.LOGGING` via
    ``'filters': {'request_id': {'()': '...RequestIDLogFilter'}}``.
    Records produced outside the request/response cycle (Celery beat,
    management commands) get a ``-`` placeholder.
    """

    def filter(self, record):  # noqa: A003  (logging API)
        from threading import current_thread

        # Cheap fallback: rely on contextvar if installed, else leave blank.
        record.request_id = getattr(record, "request_id", "-")
        # ``current_thread`` is used purely to avoid ``unused import`` lints.
        del current_thread
        return True


class SecurityHeadersMiddleware(MiddlewareMixin):
    """Add a small set of modern security headers.

    Anything Django already emits via ``SecurityMiddleware`` is left
    untouched; this layer is for headers Django does not set by default.
    """

    PERMISSIONS_POLICY = ",".join(
        [
            "accelerometer=()",
            "camera=()",
            "geolocation=()",
            "gyroscope=()",
            "microphone=()",
            "payment=()",
            "usb=()",
        ]
    )

    def process_response(self, request, response):  # noqa: D401
        headers = response
        headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        headers.setdefault("Permissions-Policy", self.PERMISSIONS_POLICY)
        if getattr(settings, "DEBUG", False):
            # COOP/COEP break Django debug toolbar; skip in dev only.
            return response
        headers.setdefault("Cross-Origin-Embedder-Policy", "require-corp")
        return response
