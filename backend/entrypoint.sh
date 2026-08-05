#!/bin/sh
set -e

echo "Running makemigrations..."
python manage.py makemigrations

echo "Running migrate..."
python manage.py migrate

# Django's own `runserver` is explicitly documented as unfit for
# production: it has no worker pool, so it processes requests with far
# less concurrency than a real WSGI server, and lacks the hardening one
# provides — a handful of concurrent slow requests (never mind an actual
# DoS attempt) can back up every other user's requests behind them. Use it
# only for local development (DJANGO_DEBUG=True); anything else runs
# behind gunicorn, matching how DEBUG already gates dev-vs-prod behavior
# in config/settings.py. Worker/thread counts here are a safe starting
# point — tune to the deployment host's actual CPU count.
if [ "$DJANGO_DEBUG" = "True" ]; then
  echo "Starting Django development server (DJANGO_DEBUG=True)..."
  exec python manage.py runserver 0.0.0.0:8000
else
  echo "Collecting static files..."
  python manage.py collectstatic --noinput

  echo "Starting gunicorn..."
  exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 60
fi
