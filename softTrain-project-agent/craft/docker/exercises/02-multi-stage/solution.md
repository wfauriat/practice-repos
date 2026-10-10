# Solution — multi-stage build

```dockerfile
# Dockerfile

# --- build stage ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# --- runtime stage ---
FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY package.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist ./dist

USER node
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## Power-user notes

### Why two `npm install` runs?

In `build`, you install **everything** (typescript, @types, etc.) so `tsc` can compile. In `runtime`, you start fresh with `npm ci --omit=dev` so only runtime deps end up in the final image. The cost is 30 seconds extra during build; the win is ~200MB shaved off the image.

### `npm ci` vs `npm install`

- `npm install` resolves the dep tree. May update `package-lock.json`.
- `npm ci` strictly installs from `package-lock.json`. Fails if the lock is stale. Faster. **Use this in CI and Docker builds.**

### `COPY --from=<stage>` to skip stages

You can `COPY --from=node:20` to grab files from any image, not just a previously-named stage. Useful for snagging a binary from a tooling image without making it your base.

### `ARG` for pinned versions

```dockerfile
ARG NODE_VERSION=20.15.0
FROM node:${NODE_VERSION}-alpine AS build
```

Lets your build script override the Node version: `docker build --build-arg NODE_VERSION=22 .`. Better than hard-coding.

### `--target` to build a specific stage

```bash
docker build --target=build -t lab02-build .
```

Only builds up to the named stage. Useful for CI where you want to *test* in the build image (with all deps available) but *ship* the runtime image.

### Distroless / scratch for the truly minimal

For a pure-binary deploy:

```dockerfile
FROM gcr.io/distroless/nodejs20-debian12
COPY --from=build /app/dist /app
COPY --from=build /app/node_modules /app/node_modules
WORKDIR /app
CMD ["index.js"]
```

Distroless images contain only your runtime — no shell, no package manager, no apt. Much harder to compromise; also harder to debug. Worth it for prod, painful for "let me exec in and check what's wrong."

### A test you should run

Build both versions and compare:

```bash
docker images | grep lab02
```

Expect the multi-stage image to be ~half the size. The actual ratio depends on how much dev tooling you have.
