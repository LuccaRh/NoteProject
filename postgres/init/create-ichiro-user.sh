#!/bin/sh
# Runs once, on the first start with an empty volume: ichiro connects as
# a user that is not a superuser, so the row-level security of the notes
# applies to it (the migrations still run as POSTGRES_USER)
set -e

# The password goes as a psql variable, quoted by psql (:'password')
psql -v ON_ERROR_STOP=1 -v password="$ICHIRO_DB_PASSWORD" \
    -U "$POSTGRES_USER" -d "$POSTGRES_DB" <<'SQL'
CREATE ROLE ichiro LOGIN NOSUPERUSER NOBYPASSRLS PASSWORD :'password';
SQL
