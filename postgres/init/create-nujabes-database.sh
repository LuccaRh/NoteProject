#!/bin/sh
# Runs once, on the first start with an empty volume: nujabes gets its own
# user and database, so it never sees the notes database
set -e

# The password goes as a psql variable, quoted by psql (:'password')
psql -v ON_ERROR_STOP=1 -v password="$NUJABES_DB_PASSWORD" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
CREATE ROLE nujabes LOGIN PASSWORD :'password';
CREATE DATABASE nujabes OWNER nujabes;
SQL
