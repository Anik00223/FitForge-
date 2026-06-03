# 🏋️‍♂️ FitForge

![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Supabase-336791?logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-Cache%20%2F%20Broker-DC382D?logo=redis)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Kustomize-326CE5?logo=kubernetes)
![Sentry](https://img.shields.io/badge/Observability-Sentry%20%2F%20Prom-362D59?logo=sentry)

**FitForge** is a production-grade, AI-powered fitness and nutrition
planner. Instead of static workout routines, FitForge leverages the
NVIDIA NIM API (Llama 3 70B) to generate highly personalized, dynamic
training blocks and macro-nutrient diets based on your unique body
metrics, goals, and equipment availability.

---

## ✨ Features

- **AI-Powered Planning** – 7-day workout & diet plans, generated async via Celery.
- **Social Auth** – Google, Microsoft, Apple via `django-allauth`.
- **Dynamic BMI Calculator** – interactive gauge with historical charts.
- **Progress Tracking** – daily workouts, weights, meals.
- **Macro Calculation** – TDEE + macro splits.
- **Premium UI** – dark/gold design system, Bootstrap 5, Chart.js, AOS.
- **Supabase** – managed Postgres for data, Supabase Auth for token-based sessions.
- **Production Hardened** – HSTS, CSP, Permissions-Policy, COOP/COEP.
- **Observable** – structured JSON logs, Sentry, Prometheus `/metrics`.
- **Kubernetes Ready** – Kustomize base + per-environment overlays, HPA, PDB, NetworkPolicy, daily DB backups.

---

## 🏗 Architecture

```mermaid
graph TD
    Client[Web Browser] --> |HTTPS| LB[Cluster Ingress / nginx]
    LB --> |Static / Media| WhiteNoise
    LB --> |HTTP| Gunicorn[Gunicorn gthread workers]
    Gunicorn --> Django
    Django --> Redis[(Redis 7 – cache + broker)]
    Django --> Postgres[(Postgres – Supabase / managed)]
    Django --> Celery[Celery worker Deployment]
    Celery --> Redis
    Celery --> NVIDIA[NVIDIA NIM API]
    Django --> Sentry
    Django --> Prometheus[/metrics]
```

| Path        | Purpose                                            |
|-------------|----------------------------------------------------|
| `/livez`    | Liveness probe – process is up                     |
| `/readyz`   | Readiness probe – DB, cache, broker reachable      |
| `/healthz`  | Human-friendly combined health page (HTML/JSON)    |
| `/metrics`  | Prometheus exposition (`django_prometheus`)        |

---

## 🛠 Tech Stack

| Category            | Technology                                      |
|---------------------|-------------------------------------------------|
| **Backend**         | Django 4.2, Django REST framework               |
| **Database**        | PostgreSQL 14+ (Supabase recommended)           |
| **Cache / Broker**  | Redis 7                                         |
| **AI**              | NVIDIA NIM API – Llama 3 70B                    |
| **Auth**            | `django-allauth` (Google / Microsoft / Apple)   |
| **Async**           | Celery 5 + Redis broker                         |
| **Frontend**        | Bootstrap 5, Chart.js, AOS, vanilla CSS         |
| **Observability**   | Sentry, structured JSON logs, Prometheus        |
| **Deployment**      | Docker, Kubernetes (Kustomize), Kuberns-ready   |
| **Web server**      | gunicorn (gthread) behind cluster ingress       |

---

## 🚀 Quick start (local dev)

```bash
# 1. Clone & setup
git clone https://github.com/yourusername/fitforge.git
cd fitforge
make install

# 2. Configure env
cp .env.example .env
$EDITOR .env

# 3. Start Redis (Docker is the easiest)
docker run -d --name fitforge-redis -p 6379:6379 redis:7-alpine

# 4. Migrate & run
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Hit <http://localhost:8000>. `make help` lists every developer target.

---

## 🐳 Docker (local production simulation)

```bash
cp .env.docker.example .env
$EDITOR .env
docker compose up --build -d
```

The stack ships: `web` (gunicorn) · `worker` (Celery) · `redis` · `nginx`.

Health checks are baked in for every service; `docker compose ps` shows
the live status.

---

## ☸️ Kubernetes / Kuberns

The project ships with a complete Kustomize tree under `k8s/`:

```bash
# Validate
make k8s-validate

# Deploy to staging
make k8s-apply-staging

# Deploy to production (after CI has built & pushed the image)
make k8s-apply-prod
```

See [`k8s/README.md`](k8s/README.md) for the manifest map, probe layout,
resource profile, and backup strategy.

### One-time migration

```bash
kubectl create job -n fitforge \
    --from=cronjob/fitforge-db-backup fitforge-migrate-$(date +%s) \
    -o yaml --dry-run=client | \
    sed 's|fitforge-db-backup|fitforge-migrate|' | kubectl apply -f -
```

### Image

```bash
docker build -t registry.fitforge.app/fitforge:$GIT_SHA .
docker push           registry.fitforge.app/fitforge:$GIT_SHA
kubectl set image deployment/fitforge-web web=registry.fitforge.app/fitforge:$GIT_SHA -n fitforge-prod
```

---

## 🧪 Testing & quality

```bash
make test     # full suite with coverage (fails under 70 %)
make lint     # ruff lint + format check
make format   # auto-fix
```

CI runs the same targets on Python 3.11 and 3.12 against every PR.

---

## 🔑 Environment variables

See [`.env.example`](.env.example) for the full list with defaults and
descriptions.  All sensitive values must be supplied via the platform's
secret store (Kuberns secrets, Sealed Secrets, AWS SM, etc.).

---

## 🛡 Security highlights

- `SECRET_KEY` required at startup (no insecure default).
- HSTS 1y + preload, CSP, X-Frame-Options, Permissions-Policy, COOP/COEP.
- Read-only root filesystem in the container; writable dirs are
  `emptyDir` mounts.
- `tini` PID 1 for clean signal handling.
- Non-root `fitforge` user (UID 1000).
- Bandit scan in CI; `ruff` lint enforces `flake8-bandit` (S-codes).

---

## 📄 License

MIT — see [LICENSE](LICENSE).
