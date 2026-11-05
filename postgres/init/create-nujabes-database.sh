#!/bin/sh
# Runs once, on the first start with an empty volume: nujabes gets a migrator,
# which owns the database and the tables, and an app user that only reads
# and writes rows
set -e

# The passwords go as psql variables, quoted by psql (:'password')
psql -v ON_ERROR_STOP=1 -v password="$NUJABES_DB_PASSWORD" \
    -v migrator_password="$NUJABES_MIGRATOR_PASSWORD" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
CREATE ROLE nujabes_migrator LOGIN PASSWORD :'migrator_password';
CREATE ROLE nujabes LOGIN PASSWORD :'password';
CREATE DATABASE nujabes OWNER nujabes_migrator;
\connect nujabes
ALTER DEFAULT PRIVILEGES FOR ROLE nujabes_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO nujabes;
ALTER DEFAULT PRIVILEGES FOR ROLE nujabes_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO nujabes;
SQL
