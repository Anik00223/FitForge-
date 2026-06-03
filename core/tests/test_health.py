"""Tests for the Kubernetes-style health endpoints."""
from __future__ import annotations

from unittest import mock

from django.test import Client, TestCase, override_settings


class HealthEndpointTests(TestCase):
    """``/livez`` must always answer 200, ``/readyz`` and ``/healthz``
    must reflect the state of the underlying dependencies.
    """

    def setUp(self):
        self.client = Client()

    def test_livez_always_200(self):
        response = self.client.get("/livez")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_readyz_healthy(self):
        # ``check_redis`` is mocked to avoid requiring a real broker
        # during tests; DB and cache are happy on the test runner.
        with mock.patch("core.health.check_redis", return_value=(True, "ok")):
            response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("database", payload["checks"])
        self.assertIn("cache", payload["checks"])
        self.assertIn("broker", payload["checks"])

    def test_readyz_degraded_when_db_unavailable(self):
        from django.db import connection

        with mock.patch.object(connection, "cursor") as cursor:
            cursor.side_effect = RuntimeError("simulated db outage")
            response = self.client.get("/readyz")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "degraded")

    def test_healthz_json(self):
        with mock.patch("core.health.check_redis", return_value=(True, "ok")):
            response = self.client.get(
                "/healthz",
                HTTP_ACCEPT="application/json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "fitforge")

    def test_healthz_html(self):
        with mock.patch("core.health.check_redis", return_value=(True, "ok")):
            response = self.client.get(
                "/healthz",
                HTTP_ACCEPT="text/html",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"fitforge", response.content)

    @override_settings(ENABLE_PROMETHEUS=False)
    def test_metrics_route_absent_when_disabled(self):
        response = self.client.get("/metrics")
        # When disabled, the catch-all 404 handler kicks in (404).
        self.assertEqual(response.status_code, 404)
