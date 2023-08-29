#!/bin/sh
set -e

# compile the translations files
python manage.py compilemessages
python manage.py collectstatic --noinput