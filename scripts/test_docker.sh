#!/usr/bin/env bash
#
# Smoke test for the production Docker image: build it, check its contents,
# start it in dry-run mode and wait for the Docker HEALTHCHECK to pass, then
# check that a stalled command queue gets the container restarted.
#
set -euo pipefail

IMAGE="goal-bot:test"
CONTAINER="goal-bot-test"
HEALTH_TIMEOUT_SECONDS=120
RESTART_TIMEOUT_SECONDS=120
RESTART_PROJECT="goal-bot-restart-test"

cd "$(dirname "$0")/.."

cleanup() {
    docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
    docker compose -p "$RESTART_PROJECT" down --rmi local >/dev/null 2>&1 || true
    if [ -n "${COMPOSE_DIR:-}" ]; then
        rm -rf "$COMPOSE_DIR"
    fi
}
trap cleanup EXIT

run_in_image() {
    docker run --rm --entrypoint sh "$IMAGE" -c "$1"
}

echo "==> Building image"
docker build -t "$IMAGE" .

echo "==> Checking that no secrets are baked into the image"
if ! run_in_image 'test ! -e /bot/config'; then
    echo "FAIL: /bot/config exists in the image; check .dockerignore" >&2
    exit 1
fi

echo "==> Checking native dependencies"
run_in_image 'ffmpeg -version >/dev/null'
run_in_image 'python -c "import pymediainfo, sys; sys.exit(0 if pymediainfo.MediaInfo.can_parse() else 1)"'

echo "==> Starting container in dry-run mode"
docker rm -f "$CONTAINER" >/dev/null 2>&1 || true
docker run -d --name "$CONTAINER" "$IMAGE" python ./main.py --dry-run >/dev/null

echo "==> Waiting for HEALTHCHECK to report healthy (up to ${HEALTH_TIMEOUT_SECONDS}s)"
deadline=$((SECONDS + HEALTH_TIMEOUT_SECONDS))
while true; do
    running=$(docker inspect -f '{{.State.Running}}' "$CONTAINER")
    status=$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER")

    if [ "$running" != "true" ]; then
        echo "FAIL: container exited" >&2
        docker logs "$CONTAINER" >&2
        exit 1
    fi

    if [ "$status" = "healthy" ]; then
        break
    fi

    if [ "$status" = "unhealthy" ] || [ "$SECONDS" -ge "$deadline" ]; then
        echo "FAIL: health status is '$status'" >&2
        docker inspect -f '{{json .State.Health}}' "$CONTAINER" >&2
        docker logs "$CONTAINER" >&2
        exit 1
    fi

    sleep 5
done

echo "==> Validating docker-compose.yml"
# Elastic Beanstalk supplies .env at deploy time; use an empty one here.
COMPOSE_DIR=$(mktemp -d)
cp docker-compose.yml "$COMPOSE_DIR/"
touch "$COMPOSE_DIR/.env"
docker compose -f "$COMPOSE_DIR/docker-compose.yml" config --quiet

echo "==> Checking that a stalled command queue restarts the container"
compose=(docker compose -p "$RESTART_PROJECT"
         -f docker-compose.yml -f scripts/docker-compose.stall.yml)
"${compose[@]}" up -d --build
container_id=$("${compose[@]}" ps -q goal-bot)

deadline=$((SECONDS + RESTART_TIMEOUT_SECONDS))
while true; do
    restarts=$(docker inspect -f '{{.RestartCount}}' "$container_id")
    if [ "$restarts" -ge 1 ]; then
        break
    fi

    if [ "$SECONDS" -ge "$deadline" ]; then
        echo "FAIL: container did not restart after the queue stalled" >&2
        docker logs "$container_id" >&2
        exit 1
    fi

    sleep 2
done

logs=$(docker logs "$container_id" 2>&1)
if [[ "$logs" != *"Health watchdog forcing process exit"* ]]; then
    echo "FAIL: container restarted, but not because of the health watchdog" >&2
    echo "$logs" >&2
    exit 1
fi

echo "PASS: Docker smoke test"
