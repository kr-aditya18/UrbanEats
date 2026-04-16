#!/bin/bash
set -e

echo "==> Running migrations..."
python manage.py migrate \
    --settings=foodonline_main.settings_render \
    --noinput

# ── ONE-TIME ONLY: load initial data ─────────────────────────────────────────
# After first successful deploy, comment this out and push again.
# Keeping it permanently will re-load data on every container restart (bad).
echo "==> Loading datadump.json..."
python manage.py loaddata datadump.json \
    --settings=foodonline_main.settings_render

echo "==> Starting Gunicorn..."
exec gunicorn foodonline_main.wsgi:application \
    --bind 0.0.0.0:10000 \
    --workers 2 \
    --timeout 120 \
    --log-level info