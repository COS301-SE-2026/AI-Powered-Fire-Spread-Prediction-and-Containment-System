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

# Yarn commands

- Run the commands from the root of the repository to execute them in the correct context:

```bash
yarn dev
yarn build
yarn lint
```

- To run from app/backend/src:

```bash
yarn test # runs all test files in the tests folder
yarn start
yarn dev
```

- To run from app/frontend/src:

```bash
yarn dev
yarn build
yarn start
yarn lint
yarn test # runs all test files in the testing folder
```

# Just some notes for testing

## Backend testing
- The backend uses pytest for testing. Test files should be placed in the `app/backend/src/tests` directory and follow the naming convention `test_*.py`.
- To run the tests, navigate to the `app/backend/src` directory and execute `yarn test`. This will run all the test files in the `tests` folder.

## Frontend testing
- The frontend uses playwright for testing. Test files should be placed in the `app/frontend/src/testing` directory and follow the naming convention `*.spec.ts`.
- To run the tests, navigate to the `app/frontend/src` directory and execute `yarn test`. This will run all the test files in the `testing` folder.
- To run a specific test file, use the command `yarn test path/to/testfile.spec.ts`. For example, to run the `home.spec.ts` test file, execute `yarn test testing/home.spec.ts`.te