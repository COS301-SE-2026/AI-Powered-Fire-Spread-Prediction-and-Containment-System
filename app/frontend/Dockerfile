FROM node:22-alpine@sha256:c610fcdfb1d5b4740dd70c284ed3cb16bb857e0f7166196e36a5501df7a3aa32

WORKDIR /app

COPY package*.json yarn.lock ./
RUN corepack enable \
	&& yarn install --ignore-workspaces --frozen-lockfile

COPY . .

EXPOSE 3000

CMD ["yarn", "dev"]