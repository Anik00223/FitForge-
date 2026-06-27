#!/usr/bin/env bash
# Restore the most recent (or user-specified) backup into ``$DATABASE_URL``.
set -euo pipefail

: "${DATABASE_URL:?DATABASE_URL must be set}"
: "${BACKUP_DIR:=./backups}"

file="${1:-}"
if [[ -z "${file}" ]]; then
    file=$(ls -1t "${BACKUP_DIR}"/fitforge-*.sql.gz 2>/dev/null | head -n 1 || true)
fi

if [[ -z "${file}" || ! -f "${file}" ]]; then
    echo "[restore] no backup file found (looked in ${BACKUP_DIR})" >&2
    exit 1
fi

echo "[restore] loading ${file} into ${DATABASE_URL%%@*}@***"
if [[ "${file}" == *.gz ]]; then
    gunzip -c "${file}" | psql --set ON_ERROR_STOP=1 "${DATABASE_URL}"
else
    psql --set ON_ERROR_STOP=1 "${DATABASE_URL}" < "${file}"
fi
echo "[restore] done"
