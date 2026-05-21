from pathlib import Path

import dj_database_url
from decouple import config


BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = config("SECRET_KEY", default="dev-secret-key-change-me-please-fitforge-local-only-12345")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1,0.0.0.0").split(",")
CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="http://localhost,http://127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.microsoft",
    "allauth.socialaccount.providers.apple",

    "apps.accounts",
    "apps.tracker",
    "apps.nutrition",
    "apps.ai_planner",
    "core",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ROOT_URLCONF = "config.urls"

DATABASE_URL = config("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config("REDIS_URL", default="redis://localhost:6379/0"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
SESSION_COOKIE_AGE = 86400 * 7
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_HTTPONLY = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.global_context",
            ],
        },
    }
]

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

NVIDIA_API_KEY = config("NVIDIA_API_KEY", default="")
NVIDIA_BASE_URL = config("NVIDIA_BASE_URL", default="https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = config("NVIDIA_MODEL", default="meta/llama-3.3-70b-instruct")

# ---------- django-allauth settings ----------
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "optional"
ACCOUNT_SIGNUP_REDIRECT_URL = "/profile/setup/"
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_STORE_TOKENS = True

SOCIALACCOUNT_ADAPTER = "apps.accounts.adapters.FitForgeSocialAccountAdapter"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            "client_id": config("GOOGLE_CLIENT_ID", default=""),
            "secret": config("GOOGLE_CLIENT_SECRET", default=""),
        },
    },
    "microsoft": {
        "APPS": [
            {
                "client_id": config("MICROSOFT_CLIENT_ID", default=""),
                "secret": config("MICROSOFT_CLIENT_SECRET", default=""),
                "settings": {
                    "tenant": config("MICROSOFT_TENANT_ID", default="common"),
                },
            }
        ],
    },
    "apple": {
        "APPS": [
            {
                "client_id": config("APPLE_SERVICE_ID", default=""),
                "secret": config("APPLE_KEY_ID", default=""),
                "key": config("APPLE_TEAM_ID", default=""),
                "settings": {
                    "certificate_key": config("APPLE_PRIVATE_KEY", default=""),
                }
            }
        ],
    },
}
