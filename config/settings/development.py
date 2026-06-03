"""Development settings (DEBUG=True, local Redis optional, console email)."""
from .base import *  # noqa: F401,F403


DEBUG = True
ALLOWED_HOSTS = ["*"]

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
