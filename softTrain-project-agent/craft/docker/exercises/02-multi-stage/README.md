# Lab 02 — multi-stage builds

## Setup

```bash
bash craft/docker/exercises/02-multi-stage/setup.sh
cd craft/docker/_sandbox/02-multi-stage
```

You'll find a Node.js project (a tiny TypeScript HTTP server). It needs to be **built** (TypeScript → JavaScript) before it can run, and the build tooling (typescript, tsc) is a lot of bytes that **don't need to be in the production image**.

## Goal

Write a **multi-stage Dockerfile** that:

1. In a `build` stage, installs all dependencies (including dev) and runs `npm run build`.
2. In a `runtime` stage, copies only the compiled output (`dist/`) and the production-only deps.
3. Runs `node dist/index.js` on container start.

Build it with:

```bash
docker build -t lab02 .
docker run --rm -p 3000:3000 lab02
# In another terminal:
curl http://localhost:3000
```

## Why this matters

Compare image sizes before and after:

```bash
# Single-stage (build everything in one image):
docker build -t lab02-single -f Dockerfile.naive .
docker images lab02-single

# Multi-stage (final image is leaner):
docker build -t lab02 .
docker images lab02
```

The multi-stage image should be ~50% smaller because typescript, @types/*, build tooling, and source files don't ship.

## Hints

- `FROM node:20-alpine AS build` — name a stage with `AS`.
- `COPY --from=build /app/dist ./dist` — pull artifacts from a previous stage.
- In runtime, do `npm ci --omit=dev` (or `pnpm install --prod`) to skip dev deps.
