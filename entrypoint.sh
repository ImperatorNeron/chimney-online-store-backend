#!/bin/sh
set -e

ENVIRONMENT="${APP_CONFIG__ENVIRONMENT:-dev}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-1}"
WAIT_FOR_DB="${WAIT_FOR_DB:-0}"

wait_for_port() {
    local host=$1
    local port=$2
    local timeout=10
    local start_time=$(date +%s)

    while ! (echo > /dev/tcp/"$host"/"$port") 2>/dev/null; do
        sleep 1
        local current_time=$(date +%s)
        local elapsed_time=$((current_time - start_time))
        echo "Waiting for $host:$port... ($elapsed_time/${timeout}s)"

        if [ $elapsed_time -ge $timeout ]; then
            echo "Unable to connect to $host:$port"
            exit 1
        fi
    done
}

if [ "$WAIT_FOR_DB" = "1" ]; then
    wait_for_port "${APP_CONFIG__DATABASE__host}" "${APP_CONFIG__DATABASE__port}"
fi

if [ "$ENVIRONMENT" = "prod" ] && [ "$RUN_MIGRATIONS" = "1" ]; then
    echo "Running migrations..."
    alembic upgrade head
fi

if [ "$ENVIRONMENT" = "prod" ]; then
    exec gunicorn -w "$WEB_CONCURRENCY" -k uvicorn.workers.UvicornWorker --bind "$HOST:$PORT" "app.main:create_app()"
else
    exec uvicorn --factory app.main:create_app --host "$HOST" --port "$PORT" --reload
fi
