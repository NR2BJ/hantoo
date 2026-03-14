FROM node:20-alpine

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install || npm install

COPY . .

CMD ["npx", "next", "dev", "--hostname", "0.0.0.0"]
