# <----------------------------------------------------------------------------------------->
#  Stage 1: Base Runtime & Lockfile Dependencies
# <----------------------------------------------------------------------------------------->
FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS base

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
FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32 AS prod

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