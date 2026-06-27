#!/usr/bin/env bash
# Convenience wrapper that starts the gunicorn process using the
# settings + gunicorn config committed to the repository.  Used as the
# default command in the production container and locally via
# ``make serve``.
set -euo pipefail

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-config.settings.production}"
export PYTHONUNBUFFERED=1

PORT="${PORT:-8000}"

exec gunicorn \
    --config config/gunicorn.conf.py \
    config.wsgi:application
