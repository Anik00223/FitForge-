from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.tracker.views import dashboard_view, home_view
from apps.accounts.views import profile_setup


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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "core.views.error_404"
handler500 = "core.views.error_500"
