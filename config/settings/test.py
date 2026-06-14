"""Test settings — fast, isolated, no external dependencies."""
from .base import *  # noqa: F401,F403

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # In-memory DB — faster than file-based
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "fitforge-test-cache",
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.db"

# allauth: disable email verification + HTTP during tests
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

# Celery: run tasks synchronously in tests (no broker needed)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable django-axes in tests to avoid lockout interference
AXES_ENABLED = False

# Use console email during tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Disable Sentry in tests
SENTRY_DSN = ""

# Faster password hashing in tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
