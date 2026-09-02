# Please refrain from changing this file

FROM node:26-alpine@sha256:2d984a15c9b54fd0aeb608b8e0d0d83529eb34d2966db27a1fb4f1edc3d298a3 AS base

WORKDIR /app

COPY package*.json yarn.lock ./
RUN corepack enable \
	&& yarn install --ignore-workspaces --frozen-lockfile

COPY . .

FROM base AS dev
CMD ["yarn", "dev"]

FROM base AS build
ARG NEXT_PUBLIC_MAPBOX_TOKEN
ENV NEXT_PUBLIC_MAPBOX_TOKEN=$NEXT_PUBLIC_MAPBOX_TOKEN
RUN yarn build

FROM build AS production
EXPOSE 3000
CMD ["yarn", "start"]
