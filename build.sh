#!/usr/bin/env bash
# Render build command. Runs on every deploy (free tier has no shell, so all setup happens here).
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py createcachetable
python manage.py bootstrap   # demo user + superuser from DJANGO_SUPERUSER_* env vars
