#!/bin/bash

# Exit on error
set -e

# Load environment variables
source .env

# Set variables
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="./backups"
METABASE_BACKUP_FILE="${BACKUP_DIR}/metabase_backup_${TIMESTAMP}.tar.gz"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p ${BACKUP_DIR}

echo "Starting Metabase backup at $(date)"

# Check if Metabase container is running
if ! docker-compose ps metabase | grep -q "Up"; then
  echo "Metabase container is not running. Skipping Metabase backup."
  exit 0
fi

# Create a temporary directory for the backup
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Export Metabase data
echo "Exporting Metabase data..."
docker-compose exec -T metabase /bin/bash -c "mkdir -p /tmp/metabase-backup && \
  java -jar /app/metabase.jar export /tmp/metabase-backup/metabase-export.zip"

# Copy the export file from the container
echo "Copying export file from container..."
docker cp $(docker-compose ps -q metabase):/tmp/metabase-backup/metabase-export.zip "$TEMP_DIR/"

# Create a tar archive of the export
echo "Creating archive..."
tar -czf "$METABASE_BACKUP_FILE" -C "$TEMP_DIR" .

# Clean up
echo "Cleaning up..."
rm -rf "$TEMP_DIR"
docker-compose exec -T metabase /bin/bash -c "rm -rf /tmp/metabase-backup"

# Clean up old backups (older than RETENTION_DAYS)
find ${BACKUP_DIR} -name "metabase_backup_*.tar.gz" -type f -mtime +${RETENTION_DAYS} -delete

echo "Old Metabase backups cleaned up"

# Log backup size
BACKUP_SIZE=$(du -h "$METABASE_BACKUP_FILE" | cut -f1)
echo "Metabase backup size: ${BACKUP_SIZE}"

echo "Metabase backup completed successfully at $(date)" 