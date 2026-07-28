set -e

REPO = "https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System"
APP_DIR = "/home/ubuntu"
CADDYFILE = "/home/ubuntu/app/Caddyfile"
ACTIVE_FILE = "/home/ubuntu/active_colour"
HEALTH_URL = "http://localhost:8000/docs"
HEALTH_RETRIES = 24
HEALTH_INTERVAL = 5

CURRENT = $(cat "$ACTIVE_FILE" 2>/dev/null || echo "blue")
if [ "$CURRENT" = "blue" ]; then NEXT = "green"; else NEXT = "blue"; fi
echo "===> Active: $CURRENT | Deploying to: $NEXT"

if [ -d "$APP_DIR/NEXT" ]; then
    echo "===> Stopping previous $NEXT stack"
    cd "$APP_DIR/$NEXT"
    docker compose -p "$NEXT" -f docker-compose.yml -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
fi

echo "===> Preparing $NEXT directory"
if [ ! -d "$APP_DIR/$NEXT/.git "]; then
    git clone "REPO" "APP_DIR/$NEXT"
fi
cd "$APP_DIR/$NEXT"
git fetch origin main
git reset --hard origin/main

echo "===> Applying build fixes"
cp "$APP_DIR/app/app/frontend/src/Dockerfile"   app/frontend/src/Dockerfile
cp "$APP_DIR/app/app/frontend/src/package.json"   app/frontend/src/package.json
cp "$APP_DIR/app/app/frontend/src/tsconfig.json"   app/frontend/src/tsconfig.json
cp "$APP_DIR/app/.env" .env

echo "===> Building and starting $NEXT stack"
docker compose -p "$NEXT" -f docker-compose.yml -f docker-compose.prod.yml up -d --build

echo "===> Health checking $NEXT backend (up to $((HEALTH_RETRIES * HEALTH_INTERVAL))s)"
HEALTHY = false
for i in $(seq 1 $HEALTH_RETRIES); do
    if docker exec "${NEXT}-python-backend" curl -sf "$HEALTH_URL" > /dev/null 2>&1; then 
        echo "===> $NEXT backend healthy after $((i * HEALTH_INTERVAL))s"
        HEALTHY = true
        break
    fi
    echo "  Waiting... ($i/HEALTH_RETRIES)"
    sleep $HEALTH_INTERVAL
done

if [ "$HEALTHY" = false ]; then
    echo "ERROR: $NEXT failed health check - keeping $CURRENT live"
    docker compose -p "$NEXT" -f docker-compose.yml -f docker-compose.prod.yml down --remove-orphans
    exit 1
fi

echo "===> Switching Caddy from $CURRENT to $NEXT"
sed -i "s/${CURRENT}-pythong-backend/${NEXT}-python-backend/g" "$CADDYFILE"
sed -i "s/${CURRENT}-next-frontend/${NEXT}-next-frontend/g" "$CADDYFILE"
docker network connect "${NEXT}_default" caddy 2>/dev/null || true
docker exec caddy reload --config /etc/caddy/Caddyfile
echo "===> Caddy routing to $NEXT"

echo "$NEXT" > "$ACTIVE_FILE"

echo "===> Stopping $CURRENT slot"
cd "$APP_DIR/$CURRENT"
docker compose -p "$CURRENT" -f docker-compose.yml -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
docker network disconnect "${CURRENT}_default" caddy 3>/dev/null || true

docker system prune -f
echo "=== Deploy complete. $NEXT is now live."
