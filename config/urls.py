from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.tracker.views import dashboard_view, home_view
from apps.accounts.views import profile_setup
from core.health import healthz, livez, readyz


urlpatterns = [
    path("", home_view, name="home"),
    path("accounts/", include("apps.accounts.urls")),
    path("accounts/", include("allauth.urls")),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("profile/setup/", profile_setup, name="profile_setup"),
    path("tracker/", include("apps.tracker.urls")),
    path("nutrition/", include("apps.nutrition.urls")),
    path("planner/", include("apps.ai_planner.urls")),
    path("admin/", admin.site.urls),
    # Kubernetes / uptime-monitor probes (must remain cheap and unauthenticated)
    path("livez", livez, name="livez"),
    path("readyz", readyz, name="readyz"),
    path("healthz", healthz, name="healthz"),
    # SEO
    path("robots.txt", include("core.robots_urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Prometheus exposition endpoint.  Only mounted when the optional
# ``django_prometheus`` app is installed AND the operator has not
# disabled metrics.  Mounted at /metrics to match the scrape config
# used by the bundled ServiceMonitor.
if getattr(settings, "ENABLE_PROMETHEUS", True):
    try:
        urlpatterns.append(path("metrics", include("django_prometheus.urls")))
    except ImportError:  # pragma: no cover
        pass

# Custom error handlers (defined once — previously duplicated)
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"
