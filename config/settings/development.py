"""Development settings (DEBUG=True, local Redis optional, console email)."""
from .base import *  # noqa: F401,F403
import os

DEBUG = True
ALLOWED_HOSTS = ["*"]

# --- Local SQLite override -----------------------------------------------
# When running locally (no VPN / no Supabase tunnel), override the DATABASE_URL
# so the dev server uses the local db.sqlite3 instead of the remote Postgres.
# Set USE_LOCAL_DB=false in .env to use the Supabase DB instead.
_use_local = os.environ.get("USE_LOCAL_DB", "true").lower() != "false"
if _use_local:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "fitforge-dev-cache",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
LOG_LEVEL = "DEBUG"
INTERNAL_IPS = ["127.0.0.1", "localhost"]

# django-debug-toolbar is opt-in
try:
    INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405
except ImportError:  # pragma: no cover - dev convenience
    pass
