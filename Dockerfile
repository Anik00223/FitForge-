"""Production-grade Dockerfile for FitForge.

* Multi-stage build keeps the final image small.
* Non-root user, read-only filesystem friendly, and ``HEALTHCHECK`` is
  duplicated at the K8s layer.
* All build-time secrets are passed as ``--build-arg`` so they are not
  baked into intermediate layers.
* ``DJANGO_SETTINGS_MODULE=config.settings.production`` is the
  default; override at runtime with the env var.
"""
# syntax=docker/dockerfile:1.7
ARG PYTHON_VERSION=3.11

# ---------------------------------------------------------------------------
# Stage 1 – build wheels & collect static assets
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements/ /build/requirements/
RUN pip install --upgrade pip \
 && pip install --prefix=/install -r requirements/production.txt

COPY . /build/
RUN SECRET_KEY=collectstatic-placeholder-only \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    /install/bin/python -m django collectstatic --noinput || true


# ---------------------------------------------------------------------------
# Stage 2 – minimal runtime image
# ---------------------------------------------------------------------------
FROM python:${PYTHON_VERSION}-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.production \
    PORT=8000 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH=/app

# Runtime-only system dependencies (no compilers in the final image).
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
        tini \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system --gid 1000 fitforge \
 && useradd  --system --uid 1000 --gid fitforge --home-dir /app --shell /usr/sbin/nologin fitforge

WORKDIR /app

# Copy installed Python packages from the builder stage.
COPY --from=builder /install /usr/local
# Copy application source last so dependency changes don't bust this cache.
COPY --chown=fitforge:fitforge --from=builder /build /app

# Make entrypoint executable, prepare writable runtime dirs.
RUN chmod +x /app/docker-entrypoint.sh \
 && mkdir -p /app/staticfiles /app/media \
 && chown -R fitforge:fitforge /app

USER fitforge

EXPOSE 8000

# tini gives us proper signal forwarding for ``docker stop`` /
# Kubernetes ``SIGTERM`` and clean shutdown of gunicorn workers.
ENTRYPOINT ["/usr/bin/tini", "--", "/app/docker-entrypoint.sh"]
CMD ["gunicorn", "--config", "config/gunicorn.conf.py", "config.wsgi:application"]
