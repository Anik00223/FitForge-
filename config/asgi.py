"""ASGI entry point for FitForge.

We use ASGI (in addition to WSGI) so the application can host
Server-Sent Events streams used by the AI planner to push live progress
to the browser.  The Celery worker still uses the WSGI-compatible
Django settings module.
"""
import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_asgi_application()
