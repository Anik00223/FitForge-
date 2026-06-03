"""FitForge Django project package.

Exposes the default Celery app so that ``@shared_task`` decorators and the
worker process can find the application configuration automatically.
"""
from .celery import app as celery_app

__all__ = ("celery_app",)
