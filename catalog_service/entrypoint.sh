#!/bin/sh
set -e

mkdir -p "$(dirname "$CATALOG_DB_PATH")"

if [ ! -f "$CATALOG_DB_PATH" ]; then
  python init_db.py
fi

exec python app.py
