# Docker Setup

## Prerequisites

- Install Docker Engine and Docker Compose / Docker CLI with Compose support.
- Install Yarn globally or enable Corepack:

```bash
npm i -g yarn
```

```bash
corepack enable
```
- Copy `.env.example` to `.env` at the repository root and fill in the required values:

```bash
cp .env.example .env
```

## Frontend styling (Tailwind + DaisyUI)

The Next.js frontend uses Tailwind CSS with DaisyUI.

From `app/frontend/src`, install dependencies:

```bash
yarn add -D tailwindcss postcss autoprefixer daisyui
```

These files are expected in the frontend package:

- `tailwind.config.js`
- `postcss.config.js`
- `styles/globals.css`
- `pages/_app.js` (imports `styles/globals.css`)

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

## Notes on dependency installs

The frontend and PWA services mount `node_modules` as named volumes for development.
Their container commands run `yarn install` on startup to populate these volumes.

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

## Commands for yarn

- Run the commands from the root of the repository to execute them in the correct context:

```bash
yarn dev
yarn build
yarn lint
yarn test:e2e
yarn test:e2e:backend
yarn pwa:start
```

- To run from app/backend/src:

```bash
yarn start
yarn dev
yarn api
```

- To run from app/frontend/src:

```bash
yarn dev
yarn build
yarn start
yarn lint
yarn test:e2e
yarn test:e2e:headed
yarn test:e2e:report
yarn test:e2e:install
```