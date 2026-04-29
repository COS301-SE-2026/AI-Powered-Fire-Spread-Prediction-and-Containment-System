FROM node:20-bullseye-slim

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends python3 build-essential \
  && rm -rf /var/lib/apt/lists/*

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 19006
ENV EXPO_DEVTOOLS_LISTEN_ADDRESS=0.0.0.0
CMD ["npx", "expo", "start", "--web", "--host", "0.0.0.0"]
