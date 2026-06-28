# Production-grade gunicorn configuration.
#
# Most knobs are overridable via environment variables so the same
# image runs in any environment (laptop, CI, Kuberns) without rebuilds.
import multiprocessing
import os


bind = os.environ.get("GUNICORN_BIND", f"0.0.0.0:{os.environ.get('PORT', '8000')}")
workers = int(os.environ.get("GUNICORN_WORKERS", str(min(4, multiprocessing.cpu_count() * 2 + 1))))
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "gthread")
threads = int(os.environ.get("GUNICORN_THREADS", "4"))
worker_tmp_dir = os.environ.get("GUNICORN_WORKER_TMP_DIR", "/dev/shm")
timeout = int(os.environ.get("GUNICORN_TIMEOUT", "300"))
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", "60"))
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", "10"))
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", "100"))
limit_request_line = int(os.environ.get("GUNICORN_LIMIT_REQUEST_LINE", "8190"))
limit_request_fields = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELDS", "100"))
limit_request_field_size = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", "8190"))

# Logging – emit to stdout/stderr so Kubernetes / Docker can scrape
# the pod logs without a sidecar.
accesslog = os.environ.get("GUNICORN_ACCESSLOG", "-")
errorlog = os.environ.get("GUNICORN_ERRORLOG", "-")
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
access_log_format = (
    '%(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s "%({x-request-id}i)s"'
)

# Process names – show up nicely in `ps` and `kubectl exec`.
proc_name = os.environ.get("GUNICORN_PROC_NAME", "fitforge")

# Preload app for faster worker boot, smaller RSS, and to share
# read-only state.  Disabled if you rely on ``--reload``.
preload_app = os.environ.get("GUNICORN_PRELOAD_APP", "true").lower() in ("1", "true", "yes")

# Send a SIGTERM to workers when shutting down, and wait the graceful
# timeout before sending SIGKILL.  Matches the Pod's
# ``terminationGracePeriodSeconds``.
def when_ready(server):
    server.log.info("fitforge is online: %s workers x %s threads", workers, threads)


def worker_int(worker):
    worker.log.info("worker %s received SIGINT/SIGTERM", worker.pid)


def worker_abort(worker):
    worker.log.warning("worker %s aborted", worker.pid)

