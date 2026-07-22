#!/bin/sh
set -e

echo "Waiting for PostgreSQL at ${DB_HOST:-db}:${DB_PORT:-5432}..."
until python - <<'PYEOF'
import os, socket, sys
host = os.getenv("DB_HOST", "db")
port = int(os.getenv("DB_PORT", "5432"))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
try:
    s.connect((host, port))
    s.close()
except OSError:
    sys.exit(1)
PYEOF
do
  sleep 1
done
echo "PostgreSQL is up."

# Seul le service web applique les migrations et collecte les statiques,
# pour éviter que le worker et le beat ne le fassent en même temps.
if [ "$1" = "gunicorn" ]; then
  python manage.py migrate --noinput
  python manage.py collectstatic --noinput
fi

exec "$@"
