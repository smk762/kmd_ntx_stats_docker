#!/usr/bin/env bash
set -Eeuo pipefail

# Import (restore) a Postgres SQL dump into the docker compose "db" service.
# Usage: util/import_postgres.sh /absolute/path/to/dump.sql.gz
# The target schema is dropped and recreated before import.

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 /path/to/postgres.sql.gz" >&2
  exit 1
fi

DUMP_FILE="$1"
if [[ ! -f "${DUMP_FILE}" ]]; then
  echo "Dump file not found: ${DUMP_FILE}" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PGUSER="${PGUSER:-postgres}"
PGDATABASE="${PGDATABASE:-postgres}"

echo "Ensuring postgres container is running..."
docker compose --project-directory "${REPO_ROOT}" up -d db >/dev/null

echo "Dropping and recreating public schema in ${PGDATABASE}"
docker compose --project-directory "${REPO_ROOT}" exec -T db psql \
  --username "${PGUSER}" \
  --dbname "${PGDATABASE}" \
  --command "DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public; GRANT ALL ON SCHEMA public TO ${PGUSER};"

echo "Importing dump from ${DUMP_FILE}"
gunzip -c "${DUMP_FILE}" | docker compose --project-directory "${REPO_ROOT}" exec -T db psql \
  --username "${PGUSER}" \
  --dbname "${PGDATABASE}"

echo "Import complete."

