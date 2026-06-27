#!/usr/bin/env bash
# Postgres backup helper used by the ``fitforge-db-backup`` CronJob
# and by the ``scripts/backup_local.sh`` convenience script.
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL must be set}"
: "${BACKUP_DIR:=./backups}"
: "${BACKUP_KEEP:=14}"

mkdir -p "${BACKUP_DIR}"

ts=$(date -u +%Y%m%dT%H%M%SZ)
out="${BACKUP_DIR}/fitforge-${ts}.sql.gz"

echo "[backup] dumping ${DATABASE_URL%%@*}@*** -> ${out}"
pg_dump --no-owner --no-privileges --format=plain "${DATABASE_URL}" | gzip -9 > "${out}"
echo "[backup] wrote $(du -h "${out}" | cut -f1)"

echo "[backup] pruning backups older than the ${BACKUP_KEEP} most recent"
ls -1t "${BACKUP_DIR}"/fitforge-*.sql.gz 2>/dev/null \
    | tail -n +$((BACKUP_KEEP + 1)) \
    | xargs -r rm -f
echo "[backup] done"
