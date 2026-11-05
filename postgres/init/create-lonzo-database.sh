#!/bin/sh
# Runs once, on the first start with an empty volume: lonzo gets a migrator,
# which owns the database and the tables, and an app user that only reads
# and writes rows, under the row-level security of the chats
set -e

# The passwords go as psql variables, quoted by psql (:'password')
psql -v ON_ERROR_STOP=1 -v password="$LONZO_DB_PASSWORD" \
    -v migrator_password="$LONZO_MIGRATOR_PASSWORD" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
CREATE ROLE lonzo_migrator LOGIN BYPASSRLS PASSWORD :'migrator_password';
CREATE ROLE lonzo LOGIN PASSWORD :'password';
CREATE DATABASE lonzo OWNER lonzo_migrator;
\connect lonzo
ALTER DEFAULT PRIVILEGES FOR ROLE lonzo_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO lonzo;
ALTER DEFAULT PRIVILEGES FOR ROLE lonzo_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO lonzo;
SQL
