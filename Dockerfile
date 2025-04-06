# Etapa para Node.js
FROM node:18-slim AS node-builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Etapa para Python
FROM python:3.11-slim AS python-builder
RUN apt-get update && apt-get install -y libzmq3-dev && \
    pip install pyzmq prometheus_client protobuf circuitbreaker
WORKDIR /app
COPY . /app
