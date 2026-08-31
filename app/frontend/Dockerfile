FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32

WORKDIR /app

COPY package.json yarn.lock ./
COPY app/frontend/package.json app/frontend/package.json
COPY app/backend/package.json app/backend/package.json
COPY app/pwa/package.json app/pwa/package.json

RUN corepack enable \
	&& yarn install --frozen-lockfile

COPY app/frontend app/frontend

WORKDIR /repo/app/frontend

EXPOSE 3000

CMD ["yarn", "dev"]
