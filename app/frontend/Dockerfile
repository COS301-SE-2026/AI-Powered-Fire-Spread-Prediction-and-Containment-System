# <----------------------------------------------------------------------------------------->
#  Stage 1: Base Runtime & Lockfile Dependencies
# <----------------------------------------------------------------------------------------->
FROM node:25-alpine@sha256:bdf2cca6fe3dabd014ea60163eca3f0f7015fbd5c7ee1b0e9ccb4ced6eb02ef4 AS base

WORKDIR /app

#Enable libc6 compatibility for alphine if any native bindings exists
RUN apk add --no-cache libc6-compat 

# Install dependencies based on yarn.lock
COPY app/frontend/package.json app/frontend/yarn.lock ./
RUN yarn install --frozen-lockfile --prefer-offline

# <----------------------------------------------------------------------------------------->
#  Stage 2: Devlepment (Hot reload + bind mount target)
# <----------------------------------------------------------------------------------------->
FROM base AS dev

WORKDIR /app

ENV	PORT=3000 \
	HOSTNAME="0.0.0.0" \
	NEXT_TELEMETRY_DISABLED=1

# copy source as fallback (local bind mounts override this in compose)
COPY app/frontend ./

CMD ["yarn", "dev"]

# <----------------------------------------------------------------------------------------->
#  Stage 3: Production Builder
# <----------------------------------------------------------------------------------------->
FROM base AS builder

ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_MAPBOX_TOKEN

ENV NODE_ENV=production \
	NEXT_TELEMETRY_DISABLED=1 \
	NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
	NEXT_PUBLIC_MAPBOX_TOKEN=$NEXT_PUBLIC_MAPBOX_TOKEN

COPY app/frontend ./

RUN yarn build

# <----------------------------------------------------------------------------------------->
#  Stage 4: Production Runner {Ultra-lean standalone output}
# <----------------------------------------------------------------------------------------->
# copy source as fallback (local bind mounts override this in compose)
FROM node:25-alpine@sha256:bdf2cca6fe3dabd014ea60163eca3f0f7015fbd5c7ee1b0e9ccb4ced6eb02ef4 AS prod

WORKDIR /app

ENV NODE_ENV=production \
	NEXT_TELEMETRY_DISABLED=1 \
	PORT=3000 \
	HOSTNAME="0.0.0.0"

RUN addgroup --system --gid 1001 nodejs && \
	adduser --system --uid 1001 --ingroup nodejs nextjs

COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

CMD ["node", "server.js"]