# Please refrain from changing this file

FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS base

WORKDIR /app

COPY package*.json yarn.lock .yarnrc.yml ./
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
