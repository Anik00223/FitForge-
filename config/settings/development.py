from .base import *


DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "fitforge-dev-cache",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.db"
STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"
