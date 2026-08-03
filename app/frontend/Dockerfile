FROM node:22-alpine

WORKDIR /app

COPY package*.json ./
RUN corepack enable \
	&& yarn install --ignore-workspaces

COPY . .

EXPOSE 3000

CMD ["yarn", "dev"]
