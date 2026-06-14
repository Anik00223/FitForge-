"""Minimal URL conf for robots.txt — served as a plain-text view."""
from django.http import HttpResponse
from django.urls import path


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /api/",
        "Disallow: /healthz",
        "Disallow: /readyz",
        "Disallow: /livez",
        "Disallow: /metrics",
        "",
        "Sitemap: https://fitforge.app/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


urlpatterns = [
    path("", robots_txt),
]
