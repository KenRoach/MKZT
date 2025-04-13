#!/bin/bash

# Load environment variables
source .env

# Extract database name from DATABASE_URL
DB_NAME=$(echo $DATABASE_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')
DB_USER=$(echo $DATABASE_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DATABASE_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')

# Create database
echo "Creating database $DB_NAME..."
psql -U postgres -c "CREATE DATABASE $DB_NAME;"

# Create user if it doesn't exist
echo "Creating user $DB_USER..."
psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

# Grant privileges
echo "Granting privileges..."
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "Database setup completed!" 