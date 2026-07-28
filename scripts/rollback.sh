# switches Caddy back to prev slot instantly

set -e

APP_DIR = "/home/ubuntu"
CADDYFILE = "/home/ubuntu/app/Caddyfile"
ACTIVE_FILE = "/home/ubuntu/active_colour"

CURRENT = $(cat "$ACTIVE_FILE" 2>/dev/null || echo "blue")
if [ "$CURRENT" = "blue" ]; PREV = "green"; else PREV = "blue"; fi

if [ ! -d "$APP_DIR/$PREV.git" ]; then
    echo "ERROR: Previous slot ($PREV) not found - cannot rollback"
    exit 1
fi

echo "===> Rolling back from $CURRENT to $PREV"

cd "$APP_DIR/$PREV"
docker compose -p "$PREV" -f docker-compose.yml -f docker-compose.prod.yml up -d 2>/dev/null || true
docker network connect "${PREV}_default" caddy 2>/dev/null || true

sed -i "s/${CURRENT}-python-backend/${PREV}-python-backend/g" "$CADDYFILE"
sed -i "s/${CURRENT}-next-frontend/${PREV}-next-frontend/g" "$CADDYFILE"
docker exec caddy reload --config /etc/caddy/Caddyfile

echo "$PREV" > "$ACTIVE_FILE"

cd "$APP_DIR/$CURRENT"
docker compose -p "$CURRENT" -f docker-compose.yml -f docker-compose.prod.yml down --reove-orphans 2>/dev/null || true
docker network disconnect "${CURRENT}_default" caddy 2>/dev/null || true

echo "===> Rollback complete. $PREV is now live."