#!/bin/sh
set -e

# Load DB settings from DATABASE_URL if provided; otherwise from config.ini
# Accept override via CONFIG_PATH env var; default to /root/.meteostat-server/config.ini inside container

if [ -n "$DATABASE_URL" ]; then
  # Parse DATABASE_URL using Python for reliability
  eval "$(python - <<'PY'
import os
from urllib.parse import urlparse
u = urlparse(os.environ.get('DATABASE_URL', ''))
print(f"DB_USER='{u.username or ''}'")
print(f"DB_PASS='{u.password or ''}'")
print(f"DB_HOST='{u.hostname or 'localhost'}'")
print(f"DB_PORT='{u.port or 3306}'")
path = (u.path or '/').lstrip('/')
print(f"DB_NAME='{path.split('?')[0] if path else ''}'")
PY
)"
else
  CONFIG_PATH=${CONFIG_PATH:-/root/.meteostat-server/config.ini}
  if [ ! -f "$CONFIG_PATH" ]; then
    echo "Config file not found at $CONFIG_PATH and DATABASE_URL not set" >&2
    exit 1
  fi
  # Extract values from [database] section
  DB_HOST=$(sed -nr "/^\[database\]/ { :l /^host[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" "$CONFIG_PATH")
  DB_PORT=$(sed -nr "/^\[database\]/ { :l /^port[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" "$CONFIG_PATH")
  DB_USER=$(sed -nr "/^\[database\]/ { :l /^user[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" "$CONFIG_PATH")
  DB_PASS=$(sed -nr "/^\[database\]/ { :l /^password[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" "$CONFIG_PATH")
  DB_NAME=$(sed -nr "/^\[database\]/ { :l /^name[ ]*=/ { s/.*=[ ]*//; p; q;}; n; b l;}" "$CONFIG_PATH")
  DB_HOST=${DB_HOST:-localhost}
  DB_PORT=${DB_PORT:-3306}
fi

if [ -z "$DB_USER" ] || [ -z "$DB_NAME" ]; then
  echo "Database credentials incomplete (user/name)" >&2
  exit 1
fi

# Import SQL into MySQL
set -x
curl -fsSL 'https://bulk.meteostat.net/v2/internal/stations.sql' | mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME"
curl -fsSL 'https://bulk.meteostat.net/v2/internal/inventory.sql' | mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASS" "$DB_NAME"
set +x

echo "DB import completed"
