# Project Setup Guide

This guide will walk you through the configuration and running of FireAway's application stack using Docker.

> ** Note on PWA:** Instructions will be added later

## 1. Prerequisites

Ensure that the following tools are installed on your Linux or WSL environment before starting:

- Docker Engine and Docker Compose v2 (`docker compose version`)
- Git (`git --version`)
- Node.js and Yarn - required to run backend and frontend test scripts

```bash
corepack enable
```

- Python 3.10+ - **optional**, only needed if you want local editor autocomplete outside Docker.

## 2. Initial Configuration

Clone our repository and navigate into the repository root, then copy the environment template:

```bash
cp .env.example .env
```

## 3. Build and Start the Application Stack

Run all of these commands from your repository root, where `docker-compose.ylm` is.

Remove any stale containers, networksm or volumes for a clean start:

```bash
docker compose down -v --remove-orphans
```

Build all our images:

```bash
docker compose build
```

This builds:

- `nginx` - reverse proxy in front of the frontend/backend (`nginx:alpine`, config from `nginx/default.conf`)
- `backend` – FastAPI server (`app/backend/Dockerfile`, `python:3.12-slim`)
- `frontend` – Next.js app (`app/frontend/Dockerfile`, `node:22-alpine`)
- `pwa` – React Native / Expo app from `app/pwa/Dockerfile` (Janri will add the other instructions for the PWA)
- `postgres` – PostGIS database (`postgis/postgis:15-3.5`)
- `pgadmin` – Postgres admin GUI
- `minio` - S3-compatible object storage
- `valkey` - Redis-compatible cache (`valkey/valkey:latest`)

You can start everything in detached mode:

```bash
docker compose up -d
```

Or you can run the stack in the foreground:

```bash
docker compose up
```

Check the service health:

```bash
docker compose ps
```

## 4. Application Access Points

| Service | URL / Address | Notes|
|---|---|---|
| Frontend web app | http://localhost:3000 | Served **through nginx**, not the frontend container directly — the frontend only exposes port 3000 internally|
| Backend API docs (Swagger) | http://localhost:8000/docs | Published  directly, bypass nginx |
| pgAdmin | http://localhost:8080 | |
| MinIO Console | http://localhost:9001 | |
| PostgreSQL / PostGIS | localhost:5432 | |
| Valkey | localhost:6379 | |

## 5. Seeding the Database

The `reseed` service is gated behind the `tools` Compose profile, so the profile flag is required even with `run`:

```bash
docker compose --profile tools run --rm reseed
```

This executes in  `app/backend/seed.py --reseed` and removes the runner container on exit.

## 6. Dependency Management

### Frontend

Install packages inside the running frontend container (it uses an isolated named volume, `frontend_node_modules`):

```bash
docker compose exec frontend yarn add <package_name>
docker compose exec frontend yarn add -D <package_name>
```

### Backend

The production image (`app/backend/Dockerfile`) installs from `requirements.txt` using `pip install --require-hashes --only-binary :all:`. i.e.:

- `requirements.txt` must contain hashes for every package - compiled from `requirements.in`.
- Every dependency must have a prebuilt wheel available (no source builds in the image)

To add a new production dependency:

1. Add it to `app/backend/requirements.in`.
2. Regenerate the hashed lockfile:

```bash
pip-compile --generate-hashes`
```

3. Rebuild and restart the backend container:

```bash
docker compose build backend
docker compose up -d backend
```

Dev-only dependencies (`app/backend/requirements-dev.in` / `requirements-dev.txt`) - are only installed in the `test` build stage of the Dockerfile to keep production small.

## 7. Running the Test Suites

### Backend

Tests run inside a dedicated `backend-test` container, built from  a `test` stage of `app/backend/Dockerfile` that adds dev dependencies on top of the production base:

Run from `app/backend/` (or any subdirectory under it):

```bash 
yarn test
yarn lint
yarn shell
yarn clean
```

### Frontend

The `app/frontend/package.json` wraps the Playwright suite, run inside the already-running `frontend` container:

```bash
yarn dev
yarn build
yarn start
yarn lint
yarn test
yarn test:headed
yarn test:report
yarn test:install
yarn eslint . --ext .js,.jsx,.ts,.tsx
```

## 8. Maintenance Commands:

View logs for a specific service:
 
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

Stop the stack, keeping data:

```bash
docker compose down
```

Stop the stack and wipe all volumes:

```bash
docker compose down -v
```

