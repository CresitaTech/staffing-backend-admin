#!/usr/bin/env bash

# Abort script at first error, when a command exits with non-zero status (except in until or while loops, if-tests, list constructs)
set -o errexit
# Causes a pipeline to return the exit status of the last command in the pipe that returned a non-zero return value.
set -o pipefail
# Export all defined variables
set -o allexport
# undefined variable results in error message, and forces an exit
set -o nounset


cmd="$@"

: "${DATABASE_URL:=mysql://trulocal:trulocal@db:3306/trulocal}"

# Python function to check if the DB is reachable.
function mysql_ready() {
python3 << END
import sys
import dj_database_url
import MySQLdb

try:
    url = dj_database_url.parse("$DATABASE_URL")
    print(url['HOST'])
    conn = MySQLdb.connect(url['HOST'], url['USER'], url['PASSWORD'], url['NAME'])
except MySQLdb.OperationalError:
    sys.exit(-1)
else:
    conn.close()
sys.exit(0)
END
}

if [[ -z ${DATABASE_URL} ]]; then
  echo "DATABASE_URL not set, continuing";
else
  until mysql_ready; do
    echo "MySQL cannot be reached at $DATABASE_URL, retrying in 1 second!";
    sleep 1
  done
fi

if [[ -z $cmd ]]; then
  python manage.py migrate sessions
  python manage.py migrate contenttypes
  python manage.py migrate auth
  python manage.py migrate trulocal_endpoints --database default
  python manage.py migrate trulocal_connect --database connect
  python manage.py migrate trulocal_web --database web
  python manage.py runserver 0.0.0.0:8001
else
  echo "Running command passed (by the compose file)"
  exec $cmd
fi
