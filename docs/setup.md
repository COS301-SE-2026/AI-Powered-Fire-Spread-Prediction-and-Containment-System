# Docker Setup

## Prerequisites

- Install Docker Engine and Docker Compose / Docker CLI with Compose support.
- Copy `.env.example` to `.env` at the repository root and fill in the required values:

```bash
cp .env.example .env
```

## Build the Docker containers

From the repository root, run:

```bash
docker compose build
```

This command builds the following services:

- `backend` – Python API server from `app/backend/src/Dockerfile`
- `frontend` – Next.js web app from `app/frontend/src/Dockerfile`
- `pwa` – React Native / Expo app from `app/pwa/Dockerfile`
- `postgres` – PostGIS database
- `pgadmin` – pgAdmin database management UI

## Start the application stack

Run the full stack in the foreground:

```bash
docker compose up
```

Or run it in detached mode:

```bash
docker compose up -d
```

## Verify the services

Once the stack is running, the default ports are:

- `http://localhost:3000` – frontend web app
- `http://localhost:8000` – backend API
- `http://localhost:19006` – PWA / Expo web interface
- `http://localhost:8080` – pgAdmin
- `localhost:5432` – PostgreSQL database

## Stop the containers

To stop and remove containers, networks, and volumes created by `docker compose up`:

```bash
docker compose down
```

## Useful commands

- Rebuild a single service (for example, backend):

```bash
docker compose build backend
```

- View logs for all services:

```bash
docker compose logs -f
```

- View logs for a specific service (for example, frontend):

```bash
docker compose logs -f frontend
```
