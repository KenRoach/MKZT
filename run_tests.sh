#!/bin/bash

# Exit on error
set -e

echo "Starting Docker Compose services..."
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 10

# Run database migrations
echo "Running database migrations..."
docker-compose exec app python run_migrations.py

# Populate sample data
echo "Populating sample data..."
docker-compose exec app python populate_sample_data.py

# Run tests
echo "Running tests..."
docker-compose run test

# Perform health checks
echo "Performing health checks..."
curl -s http://localhost:8000/health | grep -q "healthy" || { echo "Health check failed"; exit 1; }
echo "Health check passed"

curl -s http://localhost:8000/metrics | grep -q "status" || { echo "Metrics check failed"; exit 1; }
echo "Metrics check passed"

echo "All tests and health checks passed successfully!" 