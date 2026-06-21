#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

ENV_FILE=".env"
if [ ! -f "$ENV_FILE" ]; then
  echo "Error: .env file not found in project root. Copy .env.example to .env and fill credentials."
  exit 1
fi

set -o allexport
source "$ENV_FILE"
set +o allexport

BACKUP_DIR="backups"
if [ ! -d "$BACKUP_DIR" ]; then
  echo "Error: backup directory '$BACKUP_DIR' not found. Run scripts/backup.sh first."
  exit 1
fi

SQL_FILE="${1:-}"
UPLOAD_FILE="${2:-}"

if [ -z "$SQL_FILE" ]; then
  SQL_FILE=$(ls -t "$BACKUP_DIR"/db_backup_*.sql 2>/dev/null | head -n 1 || true)
fi
if [ -z "$UPLOAD_FILE" ]; then
  UPLOAD_FILE=$(ls -t "$BACKUP_DIR"/uploads_backup_*.tar.gz 2>/dev/null | head -n 1 || true)
fi

if [ -z "$SQL_FILE" ] || [ ! -f "$SQL_FILE" ]; then
  echo "Error: SQL backup file not found. Provide path as first argument or create one in $BACKUP_DIR."
  exit 1
fi

export PGPASSWORD="${DB_PASSWORD:-}"

echo "Restoring database from: $SQL_FILE"
if command -v docker >/dev/null 2>&1 && docker compose ps db >/dev/null 2>&1; then
  docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
  docker compose exec -T db psql -U "$DB_USER" -d "$DB_NAME" < "$SQL_FILE"
else
  if ! command -v psql >/dev/null 2>&1; then
    echo "Error: psql is not available and Docker db service is not found."
    exit 1
  fi
  psql -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
  psql -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "$DB_USER" -d "$DB_NAME" -f "$SQL_FILE"
fi

echo "Database restore completed."

if [ -n "$UPLOAD_FILE" ] && [ -f "$UPLOAD_FILE" ]; then
  echo "Restoring uploads from: $UPLOAD_FILE"
  rm -rf uploads
  mkdir -p uploads
  tar -xzf "$UPLOAD_FILE"
  echo "Uploads restored to uploads/"
else
  echo "No uploads archive found, skipping uploads restore."
fi

echo "Restore completed successfully."
