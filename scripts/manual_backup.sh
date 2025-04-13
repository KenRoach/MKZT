#!/bin/bash

# Exit on error
set -e

echo "Starting manual database backup..."

# Run the backup script
./scripts/backup_database.sh

# Check if backup was successful
if [ $? -eq 0 ]; then
  echo "Manual backup completed successfully"
  
  # List the most recent backup
  LATEST_BACKUP=$(ls -t ./backups/mkzt_backup_*.sql.gz | head -1)
  BACKUP_SIZE=$(du -h "$LATEST_BACKUP" | cut -f1)
  
  echo "Latest backup: $LATEST_BACKUP"
  echo "Backup size: $BACKUP_SIZE"
else
  echo "Manual backup failed"
  exit 1
fi 