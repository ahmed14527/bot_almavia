#!/bin/bash
set -e

echo "[Entrypoint] Starting Backend Initialization..."

# Wait for database if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
  echo "[Entrypoint] Waiting for PostgreSQL database to accept connections..."
  python - <<'EOF'
import os
import sys
import time
import dj_database_url
import psycopg2

db_url = os.environ.get('DATABASE_URL')
db_config = dj_database_url.parse(db_url)
max_retries = 30
retry = 0

while retry < max_retries:
    try:
        conn = psycopg2.connect(
            dbname=db_config['NAME'],
            user=db_config['USER'],
            password=db_config['PASSWORD'],
            host=db_config['HOST'],
            port=db_config.get('PORT', 5432),
            connect_timeout=3
        )
        conn.close()
        print("[Entrypoint] Database is ready!")
        sys.exit(0)
    except Exception as e:
        retry += 1
        print(f"[Entrypoint] Database not ready yet ({retry}/{max_retries})... Waiting 2s.")
        time.sleep(2)

print("[Entrypoint] ERROR: Could not connect to database after maximum retries.")
sys.exit(1)
EOF
fi

# Wait for Redis if CELERY_BROKER_URL is set
if [ -n "$CELERY_BROKER_URL" ]; then
  echo "[Entrypoint] Waiting for Redis broker..."
  python - <<'EOF'
import os
import sys
import time
import redis

broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
max_retries = 20
retry = 0

while retry < max_retries:
    try:
        r = redis.Redis.from_url(broker_url, socket_timeout=3)
        if r.ping():
            print("[Entrypoint] Redis broker is ready!")
            sys.exit(0)
    except Exception as e:
        retry += 1
        print(f"[Entrypoint] Redis not ready yet ({retry}/{max_retries})... Waiting 2s.")
        time.sleep(2)

print("[Entrypoint] WARNING: Redis could not be reached. Continuing...")
EOF
fi

# Apply database migrations
echo "[Entrypoint] Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "[Entrypoint] Collecting static files..."
python manage.py collectstatic --noinput || true

echo "[Entrypoint] Backend initialization complete. Executing command: $@"
exec "$@"
