#!/usr/bin/env bash
set -e

# ── Defaults ───────────────────────────────────────────────────────────────
# Set default values for database and Redis if not already defined
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}


# ── Wait for Services ───────────────────────────────────────────────────────
# Wait until PostgreSQL is ready to accept connections
echo "⏳  Waiting for PostgreSQL ($DB_HOST:$DB_PORT)…"
while ! nc -z "$DB_HOST" "$DB_PORT"; do sleep 0.2; done
echo "✅  PostgreSQL is up."


# ── Migrate and Run Gunicorn ────────────────────────────────────────────────
# Apply Django database migrations
python manage.py migrate --noinput

# If script arguments are provided, execute them directly
if [[ $# -gt 0 ]]; then
  exec "$@"
else
  # Otherwise, start the Gunicorn server with default or provided settings
  exec gunicorn project.wsgi:application \
       -b 0.0.0.0:8000 \
       --workers "${GUNICORN_WORKERS:-3}" \
       --timeout "${GUNICORN_TIMEOUT:-60}"
fi
