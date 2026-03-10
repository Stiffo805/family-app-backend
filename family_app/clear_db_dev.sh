#!/bin/bash

# --- Database cleanup and Django sync script ---

# 1. Warning and Confirmation
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
echo "WARNING: This script will DESTROY the database '$DB_NAME'."
echo "It will also delete ALL local migration files."
echo "THIS ACTION CANNOT BE UNDONE!"
echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
read -p "Are you sure you want to proceed? (y/n): " confirm

if [[ $confirm != "y" && $confirm != "Y" ]]; then
    echo "Operation cancelled by user."
    exit 0
fi

ENV_PATH="../.env"

# 2. Load environment variables
if [ -f $ENV_PATH ]; then
    export $(grep -v '^#' $ENV_PATH | xargs)
    echo "Environment variables loaded."
else
    echo "Error: .env file not found!"
    exit 1
fi

# 3. Reset database
echo "Recreating database: $DB_NAME"
export PGPASSWORD=$DB_PASSWORD

# Terminate other connections to prevent "database is being accessed" error
psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"

psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -h "$DB_HOST" -U "$DB_USER" -d "postgres" -c "CREATE DATABASE $DB_NAME;"

# 4. Handle migrations carefully
echo "Cleaning up old migration files..."
# Delete all .py files in migration folders except __init__.py
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 5. Re-generate and apply migrations
echo "Generating new initial migrations..."
python manage.py makemigrations

echo "Applying migrations to the new database..."
python manage.py migrate

echo "Creating admin user..."
python manage.py createsuperuser --username admin --email admin@example.com --no-input

echo "Database sync completed successfully."
unset PGPASSWORD