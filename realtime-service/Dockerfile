# syntax=docker/dockerfile:1
FROM node:20-alpine

WORKDIR /app

COPY package.json .

RUN npm install --omit=dev

COPY . .

EXPOSE 8007

CMD ["node", "index.js"]
