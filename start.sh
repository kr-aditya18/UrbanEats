#!/bin/bash
python manage.py migrate --settings=foodonline_main.settings_render --noinput
exec gunicorn foodonline_main.wsgi:application --bind 0.0.0.0:10000 --workers 2 --timeout 120