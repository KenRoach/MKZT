#!/bin/bash

# Exit on error
set -e

# Load environment variables
source .env

echo "Setting up Metabase..."

# Wait for Metabase to be ready
echo "Waiting for Metabase to start..."
until curl -s http://localhost:3000/api/health | grep -q "ok"; do
  echo "Metabase is not ready yet. Waiting..."
  sleep 5
done

echo "Metabase is ready!"

# Get the session token
echo "Getting session token..."
SESSION_TOKEN=$(curl -X POST http://localhost:3000/api/session \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin@metabase.local\",\"password\":\"admin\"}" | jq -r '.token')

if [ -z "$SESSION_TOKEN" ] || [ "$SESSION_TOKEN" = "null" ]; then
  echo "Failed to get session token. Please check Metabase credentials."
  exit 1
fi

echo "Session token obtained successfully."

# Create initial dashboards
echo "Creating initial dashboards..."

# Create Orders Dashboard
echo "Creating Orders Dashboard..."
curl -X POST http://localhost:3000/api/dashboard \
  -H "Content-Type: application/json" \
  -H "X-Metabase-Session: $SESSION_TOKEN" \
  -d '{
    "name": "Orders Overview",
    "description": "Overview of all orders in the system",
    "parameters": [],
    "collection_id": null
  }'

# Create Customers Dashboard
echo "Creating Customers Dashboard..."
curl -X POST http://localhost:3000/api/dashboard \
  -H "Content-Type: application/json" \
  -H "X-Metabase-Session: $SESSION_TOKEN" \
  -d '{
    "name": "Customer Analytics",
    "description": "Analytics about customer behavior and preferences",
    "parameters": [],
    "collection_id": null
  }'

# Create Merchants Dashboard
echo "Creating Merchants Dashboard..."
curl -X POST http://localhost:3000/api/dashboard \
  -H "Content-Type: application/json" \
  -H "X-Metabase-Session: $SESSION_TOKEN" \
  -d '{
    "name": "Merchant Performance",
    "description": "Performance metrics for merchants",
    "parameters": [],
    "collection_id": null
  }'

# Create Drivers Dashboard
echo "Creating Drivers Dashboard..."
curl -X POST http://localhost:3000/api/dashboard \
  -H "Content-Type: application/json" \
  -H "X-Metabase-Session: $SESSION_TOKEN" \
  -d '{
    "name": "Driver Analytics",
    "description": "Analytics about driver performance and delivery times",
    "parameters": [],
    "collection_id": null
  }'

echo "Metabase setup completed successfully!"
echo "You can access Metabase at http://localhost:3000"
echo "Default credentials: admin@metabase.local / admin" 