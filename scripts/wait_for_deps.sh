#!/usr/bin/env bash
# Wait for the database and Redis endpoints to be reachable before
# running migrations or starting the worker.  Designed to be used as
# a ``command:`` shim inside init containers or local scripts.
set -euo pipefail

: "${DATABASE_URL:=}"
: "${REDIS_URL:=}"
: "${DB_HOST:=}"
: "${DB_PORT:=5432}"

wait_for_host_port() {
    local host="$1"
    local port="$2"
    local proto="${3:-tcp}"
    if [[ -z "${host}" ]]; then return 0; fi
    echo "[wait] probing ${proto}://${host}:${port}"
    for attempt in $(seq 1 60); do
        if (echo > "/dev/tcp/${host}/${port}") >/dev/null 2>&1; then
            echo "[wait] ${host}:${port} is reachable"
            return 0
        fi
        sleep 2
    done
    echo "[wait] timeout waiting for ${host}:${port}" >&2
    return 1
}

wait_for() {
    local url="$1"
    if [[ -z "${url}" ]]; then return 0; fi
    local proto=${url%%://*}
    local rest=${url#*://}
    local host_port=${rest#*@}
    host_port=${host_port%%/*}
    local host=${host_port%%:*}
    local port=${host_port#*:}
    [[ "${host_port}" == "${port}" ]] && port="5432"
    [[ "${proto}" == "redis" ]] && port="${port:-6379}"
    [[ "${proto}" == "postgresql" || "${proto}" == "postgres" ]] && port="${port:-5432}"

    wait_for_host_port "${host}" "${port}" "${proto}"
}

if [[ -n "${DATABASE_URL}" ]]; then
    wait_for "${DATABASE_URL}"
elif [[ -n "${DB_HOST}" ]]; then
    wait_for_host_port "${DB_HOST}" "${DB_PORT}" "postgresql"
fi

wait_for "${REDIS_URL}"

