#!/usr/bin/env bash
set -Eeuo pipefail

# Export (dump) the Postgres database that backs docker compose service "db".
# Creates a gzipped SQL dump that can be restored with util/import_postgres.sh.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-${REPO_ROOT}/backups}"

mkdir -p "${BACKUP_DIR}"

TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
DEFAULT_FILE="${BACKUP_DIR}/postgres-${TIMESTAMP}.sql.gz"
DUMP_FILE="${1:-${DEFAULT_FILE}}"

PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-postgres}"

echo "Ensuring postgres container is running..."
docker compose --project-directory "${REPO_ROOT}" up -d db >/dev/null

echo "Exporting database ${PGDATABASE} as user ${PGUSER} to ${DUMP_FILE}"
docker compose --project-directory "${REPO_ROOT}" exec -T db pg_dump \
  --username "${PGUSER}" \
  "${PGDATABASE}" | gzip > "${DUMP_FILE}"

echo "Backup complete: ${DUMP_FILE}"

