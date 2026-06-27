#!/usr/bin/env bash
# Production entrypoint script for the FitForge container.
# Waits for dependencies and runs migrations before starting the application.
set -euo pipefail

# Wait for database and Redis to become ready
if [[ -f "/app/scripts/wait_for_deps.sh" ]]; then
    /app/scripts/wait_for_deps.sh
fi

# Apply database migrations during container start-up (only for gunicorn web process)
if [[ "${1:-}" == "gunicorn" ]]; then
    echo "Applying database migrations..."
    python manage.py migrate --noinput
fi

# Run the CMD instruction passed by Docker/Kubernetes/Render
exec "$@"
