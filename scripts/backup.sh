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
mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
DB_BACKUP="$BACKUP_DIR/db_backup_${TIMESTAMP}.sql"
UPLOAD_BACKUP="$BACKUP_DIR/uploads_backup_${TIMESTAMP}.tar.gz"
UPLOADS_DIR="uploads"

if [ -z "${DB_HOST:-}" ] || [ -z "${DB_USER:-}" ] || [ -z "${DB_NAME:-}" ]; then
  echo "Error: DB_HOST, DB_USER and DB_NAME must be set in .env"
  exit 1
fi

export PGPASSWORD="${DB_PASSWORD:-}"

echo "Creating database backup: $DB_BACKUP"
if command -v docker >/dev/null 2>&1 && docker compose ps db >/dev/null 2>&1; then
  docker compose exec -T db pg_dump --clean --if-exists -U "$DB_USER" -d "$DB_NAME" > "$DB_BACKUP"
else
  if ! command -v pg_dump >/dev/null 2>&1; then
    echo "Error: pg_dump is not available and Docker db service is not found."
    exit 1
  fi
  pg_dump --clean --if-exists -h "${DB_HOST:-localhost}" -p "${DB_PORT:-5432}" -U "$DB_USER" "$DB_NAME" > "$DB_BACKUP"
fi

echo "Database backup saved to $DB_BACKUP"

if [ ! -d "$UPLOADS_DIR" ]; then
  echo "Warning: uploads directory not found. Creating empty uploads directory."
  mkdir -p "$UPLOADS_DIR"
  touch "$UPLOADS_DIR/.gitkeep"
fi

echo "Creating uploads archive: $UPLOAD_BACKUP"
tar -czf "$UPLOAD_BACKUP" "$UPLOADS_DIR"
echo "Uploads backup saved to $UPLOAD_BACKUP"

echo "Backup completed successfully."
