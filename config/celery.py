"""Celery application factory for FitForge.

Celery is used to keep long-running AI plan generation off the request
thread.  The broker and result backend default to the same Redis instance
that powers the cache, which keeps the operational footprint small on
Kuberns (only one managed Redis add-on is required).
"""
from __future__ import annotations

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

app = Celery("fitforge")

# Pull configuration from Django settings (any key prefixed with CELERY_).
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks in every installed app.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> str:
    """Cheap task used to verify the worker is wired up."""
    return f"Request: {self.request!r}"


# Optional periodic schedule placeholder.  Disabled by default because the
# project has no recurring jobs, but left here as a documented hook so
# operators can enable scheduled plan refreshes, weekly summaries, etc.
app.conf.beat_schedule = {
    "ping": {
        "task": "config.celery.debug_task",
        "schedule": crontab(minute="*/30"),
    }
}
