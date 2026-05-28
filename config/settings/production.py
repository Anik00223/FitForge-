from .base import *

from decouple import config

DEBUG = config("DEBUG", default=False, cast=bool)
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True

# Security Settings
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
