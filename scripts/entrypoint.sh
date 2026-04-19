#!/bin/bash
set -e

# Wait for MySQL to be available
echo "Waiting for MySQL..."
while ! nc -z mysql 3306; do
  sleep 0.1
done
echo "MySQL is up - executing commands"

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput || true

# Optionally populate DB. Set POPULATE_DB=true in .env to enable.
if [ "${POPULATE_DB}" = "true" ]; then
  echo "POPULATE_DB is true — attempting to populate database"
  # Try to load fixture if exists, otherwise call populate script
  if [ -f "data/initial_data.json" ]; then
    python manage.py loaddata data/initial_data.json || true
  else
    # Use utils/db_populate.py script to populate mangas (may take long)
    python - <<'PY'
from utils.db_populate import populate_mangas
populate_mangas()
PY
  fi
fi

# Start the application
exec "$@"
