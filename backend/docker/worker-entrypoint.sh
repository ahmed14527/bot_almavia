#!/bin/bash
set -e

echo "[Worker Entrypoint] Initializing Celery Worker..."

# Wait for database if DATABASE_URL is set
if [ -n "$DATABASE_URL" ]; then
  echo "[Worker Entrypoint] Waiting for PostgreSQL database..."
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
        print("[Worker Entrypoint] Database is ready!")
        sys.exit(0)
    except Exception as e:
        retry += 1
        print(f"[Worker Entrypoint] Database not ready ({retry}/{max_retries})... Waiting 2s.")
        time.sleep(2)

print("[Worker Entrypoint] ERROR: Database connection failed.")
sys.exit(1)
EOF
fi

# Wait for Redis
echo "[Worker Entrypoint] Waiting for Redis broker..."
python - <<'EOF'
import os
import sys
import time
import redis

broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/0')
max_retries = 25
retry = 0

while retry < max_retries:
    try:
        r = redis.Redis.from_url(broker_url, socket_timeout=3)
        if r.ping():
            print("[Worker Entrypoint] Redis broker is ready!")
            sys.exit(0)
    except Exception as e:
        retry += 1
        print(f"[Worker Entrypoint] Redis not ready ({retry}/{max_retries})... Waiting 2s.")
        time.sleep(2)

print("[Worker Entrypoint] ERROR: Could not connect to Redis broker.")
sys.exit(1)
EOF

echo "[Worker Entrypoint] Environment ready. Starting Celery Worker: $@"
exec "$@"
