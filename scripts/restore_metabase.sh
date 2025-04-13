#!/bin/bash

# Exit on error
set -e

# Load environment variables
source .env

# Check if backup file is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <backup_file>"
  echo "Example: $0 ./backups/metabase_backup_20230101_120000.tar.gz"
  exit 1
fi

BACKUP_FILE=$1

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
  echo "Error: Backup file $BACKUP_FILE does not exist"
  exit 1
fi

echo "Starting Metabase restore at $(date)"

# Check if Metabase container is running
if ! docker-compose ps metabase | grep -q "Up"; then
  echo "Metabase container is not running. Starting Metabase..."
  docker-compose up -d metabase
  
  # Wait for Metabase to be ready
  echo "Waiting for Metabase to start..."
  until curl -s http://localhost:3000/api/health | grep -q "ok"; do
    echo "Metabase is not ready yet. Waiting..."
    sleep 5
  done
fi

# Create a temporary directory for the restore
TEMP_DIR=$(mktemp -d)
echo "Created temporary directory: $TEMP_DIR"

# Extract the backup file
echo "Extracting backup file..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Check if the export file exists
if [ ! -f "$TEMP_DIR/metabase-export.zip" ]; then
  echo "Error: Export file not found in backup"
  rm -rf "$TEMP_DIR"
  exit 1
fi

# Copy the export file to the container
echo "Copying export file to container..."
docker cp "$TEMP_DIR/metabase-export.zip" $(docker-compose ps -q metabase):/tmp/

# Import the data
echo "Importing data into Metabase..."
docker-compose exec -T metabase /bin/bash -c "java -jar /app/metabase.jar import /tmp/metabase-export.zip"

# Clean up
echo "Cleaning up..."
rm -rf "$TEMP_DIR"
docker-compose exec -T metabase /bin/bash -c "rm -f /tmp/metabase-export.zip"

echo "Metabase restore completed successfully at $(date)"
echo "You may need to restart Metabase for changes to take effect: docker-compose restart metabase" 