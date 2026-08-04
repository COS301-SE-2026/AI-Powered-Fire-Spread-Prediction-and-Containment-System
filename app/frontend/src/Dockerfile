FROM node:22-alpine

WORKDIR /app

COPY . .

ARG NEXT_PUBLIC_MAPBOX_TOKEN
ENV NEXT_PUBLIC_MAPBOX_TOKEN=$NEXT_PUBLIC_MAPBOX_TOKEN
RUN corepack enable \
        && yarn install --no-lockfile \
        && npm install --save typescript@5.7.3 @types/react @types/node @types/geojson @turf/circle @mapbox/mapbox-gl-draw \
        && yarn build

EXPOSE 3000

CMD ["yarn", "start"]
