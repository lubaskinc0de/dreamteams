# syntax=docker/dockerfile:1.7

FROM node:24-bookworm-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run postinstall
RUN npm run generate

FROM nginxinc/nginx-unprivileged:1.29-alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build --chown=101:101 /app/.output/public /usr/share/nginx/html

EXPOSE 8080
