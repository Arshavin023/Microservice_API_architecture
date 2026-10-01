#!/bin/bash
set -e
set -u

function create_multiple_databases() {
    IFS=',' read -ra DB_LIST <<< "$POSTGRES_MULTIPLE_DATABASES"
    for db in "${DB_LIST[@]}"; do
        echo "Creating database: '$db'"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
            CREATE DATABASE "$db";
            GRANT ALL PRIVILEGES ON DATABASE "$db" TO "$POSTGRES_USER";
EOSQL
    done
}

if [ -n "${POSTGRES_MULTIPLE_DATABASES:-}" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"
    create_multiple_databases
    echo "Multiple databases created successfully."
fi