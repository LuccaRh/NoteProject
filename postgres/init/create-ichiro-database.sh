#!/bin/sh
# Runs once, on the first start with an empty volume: ichiro gets a migrator,
# which owns the database and the tables, and an app user that only reads
# and writes rows, under the row-level security of the notes
set -e

# The passwords go as psql variables, quoted by psql (:'password')
psql -v ON_ERROR_STOP=1 -v password="$ICHIRO_DB_PASSWORD" \
    -v migrator_password="$ICHIRO_MIGRATOR_PASSWORD" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
CREATE ROLE ichiro_migrator LOGIN BYPASSRLS PASSWORD :'migrator_password';
CREATE ROLE ichiro LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD :'password';
CREATE DATABASE ichiro OWNER ichiro_migrator;
\connect ichiro
ALTER DEFAULT PRIVILEGES FOR ROLE ichiro_migrator IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ichiro;
ALTER DEFAULT PRIVILEGES FOR ROLE ichiro_migrator IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO ichiro;
SQL
