"""Tests for the RequestIDMiddleware and SecurityHeadersMiddleware."""
from __future__ import annotations

from django.test import Client, TestCase, override_settings


class RequestIDMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_generates_request_id_when_missing(self):
        response = self.client.get("/livez")
        self.assertEqual(response.status_code, 200)
        self.assertIn("X-Request-ID", response.headers)
        self.assertEqual(len(response.headers["X-Request-ID"]), 32)

    def test_honors_inbound_request_id(self):
        response = self.client.get("/livez", HTTP_X_REQUEST_ID="abc-123")
        self.assertEqual(response.headers["X-Request-ID"], "abc-123")

    def test_caps_inbound_request_id_length(self):
        long = "x" * 256
        response = self.client.get("/livez", HTTP_X_REQUEST_ID=long)
        self.assertEqual(len(response.headers["X-Request-ID"]), 64)


class SecurityHeadersMiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_always_on_headers(self):
        response = self.client.get("/livez")
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")
        self.assertIn("accelerometer=()", response.headers.get("Permissions-Policy", ""))
        self.assertEqual(response.headers.get("Cross-Origin-Opener-Policy"), "same-origin")

    @override_settings(DEBUG=True)
    def test_coep_skipped_in_debug(self):
        response = self.client.get("/livez")
        self.assertNotIn("Cross-Origin-Embedder-Policy", response.headers)
