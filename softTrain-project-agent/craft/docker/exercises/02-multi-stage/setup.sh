#!/usr/bin/env bash
# Build a tiny TS Node app and a naive single-stage Dockerfile to compare against.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"
SANDBOX="$REPO_ROOT/craft/docker/_sandbox/02-multi-stage"

rm -rf "$SANDBOX"
mkdir -p "$SANDBOX/src"

cat > "$SANDBOX/package.json" <<'JSON'
{
  "name": "lab02",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "scripts": {
    "build": "tsc -p tsconfig.json",
    "start": "node dist/index.js"
  },
  "dependencies": {
    "hono": "^4.5.0",
    "@hono/node-server": "^1.12.0"
  },
  "devDependencies": {
    "typescript": "^5.5.4",
    "@types/node": "^20.14.10"
  }
}
JSON

cat > "$SANDBOX/tsconfig.json" <<'JSON'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "outDir": "dist",
    "rootDir": "src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
JSON

cat > "$SANDBOX/src/index.ts" <<'TS'
import { serve } from "@hono/node-server";
import { Hono } from "hono";

const app = new Hono();
app.get("/", (c) => c.json({ msg: "Hello from a multi-stage build", node: process.version }));

const port = Number(process.env.PORT ?? 3000);
serve({ fetch: app.fetch, port }, (info) => {
    console.log(`listening on http://localhost:${info.port}`);
});
TS

# Naive single-stage Dockerfile for comparison.
cat > "$SANDBOX/Dockerfile.naive" <<'DOCKER'
# A deliberately bad single-stage Dockerfile — for comparison.
FROM node:20-alpine
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
DOCKER

cat > "$SANDBOX/.dockerignore" <<'IG'
node_modules
dist
.git
*.log
IG

cat <<EOF

✓ Sandbox built at: $SANDBOX

The naive single-stage Dockerfile is at: Dockerfile.naive
Your job is to write a multi-stage Dockerfile (just "Dockerfile") and compare.

Build both, compare sizes:
  docker build -f Dockerfile.naive -t lab02-single "$SANDBOX"
  docker build -t lab02 "$SANDBOX"
  docker images | grep lab02

EOF
