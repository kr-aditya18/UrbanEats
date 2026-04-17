#!/bin/bash
set -e

echo "==> Running migrations..."
python manage.py migrate \
    --settings=foodonline_main.settings_render \
    --noinput

echo "==> Loading data..."
python manage.py loaddata datadump.json \
    --settings=foodonline_main.settings_render \
    --ignorenonexistent

echo "==> Starting Gunicorn..."
exec gunicorn foodonline_main.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --log-level info