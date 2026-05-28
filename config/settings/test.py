from .base import *

DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"

# Disable allauth redirect checks during tests
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"
