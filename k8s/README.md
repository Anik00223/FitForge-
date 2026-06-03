# Kubernetes deployment

This directory contains a complete, production-ready Kubernetes
manifest set for **FitForge**, generated with Kustomize.  The base
manifests are environment-agnostic; per-environment overlays tweak
replica counts, image tags, ingress hostnames, and logging.

```
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml        # web + Celery worker
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   ├── networkpolicy.yaml
│   ├── servicemonitor.yaml
│   ├── migrate-job.yaml
│   └── backup-cronjob.yaml
└── overlays/
    ├── production/
    └── staging/
```

## Quick start

```bash
# Validate the manifests
kubectl --dry-run=client apply -k k8s/overlays/production

# Deploy to staging first
kubectl apply -k k8s/overlays/staging

# Run the database migrations once
kubectl create job -n fitforge-staging \
    --from=cronjob/fitforge-db-backup fitforge-migrate-$(date +%s) \
    -o yaml --dry-run=client | \
    sed 's|fitforge-db-backup|fitforge-migrate|' | kubectl apply -f -
```

## Probes

| Path       | Probe     | Purpose                              |
|------------|-----------|--------------------------------------|
| `/livez`   | Liveness  | Process is up                        |
| `/readyz`  | Readiness | DB, cache, and broker are reachable  |
| `/healthz` | Operator  | Combined HTML/JSON health page       |
| `/metrics` | Prometheus| ``django_prometheus`` exposition      |

## Resource profile

| Container | CPU req | CPU lim | Mem req | Mem lim |
|-----------|---------|---------|---------|---------|
| web       | 200m    | 1000m   | 256Mi   | 1Gi     |
| worker    | 200m    | 2000m   | 512Mi   | 2Gi     |

Tune via overlays.

## Backups

`fitforge-db-backup` runs daily at 03:00 UTC and keeps the 14 most
recent SQL dumps on the `fitforge-backups` PVC.  Restore with
`gunzip < backup.sql.gz | psql "$DATABASE_URL"`.
