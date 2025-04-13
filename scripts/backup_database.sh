#!/bin/bash

# Exit on error
set -e

# Load environment variables
source .env

# Set variables
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups"
BACKUP_FILE="${BACKUP_DIR}/mkzt_backup_${TIMESTAMP}.sql"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

# Extract database connection details from DATABASE_URL
DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASSWORD=$(echo $DATABASE_URL | sed -n 's/.*:\([^@]*\)@.*/\1/p')

echo "Starting database backup at $(date)"

# Perform the backup
PGPASSWORD=${DB_PASSWORD} pg_dump \
  --host=${DB_HOST} \
  --port=${DB_PORT} \
  --username=${DB_USER} \
  --dbname=${DB_NAME} \
  --format=custom \
  --file=${BACKUP_FILE}

# Compress the backup
gzip ${BACKUP_FILE}

echo "Database backup completed: ${BACKUP_FILE}.gz"

# Backup Metabase if it's running
if docker-compose ps metabase | grep -q "Up"; then
  echo "Starting Metabase backup..."
  ./scripts/backup_metabase.sh
else
  echo "Metabase is not running. Skipping Metabase backup."
fi

# Clean up old backups (older than RETENTION_DAYS)
find ${BACKUP_DIR} -name "mkzt_backup_*.sql.gz" -type f -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "metabase_backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete

echo "Old backups cleaned up"

# Log backup size
BACKUP_SIZE=$(du -h "${BACKUP_FILE}.gz" | cut -f1)
echo "Database backup size: ${BACKUP_SIZE}"

echo "All backups completed successfully at $(date)" 