# ts-node-api

A small but real Node API: Hono + TypeScript + Zod + Vitest. Mirrors the `Item` CRUD from `python-fastapi-crud` so you can compare the two implementations side-by-side.

## When to reach for this

- You need a Node HTTP service in TypeScript.
- You want **request validation, types, and tests** wired together.
- You want a Docker image to ship.
- You want to pair this with `ts-react-vite` for full-stack work.

If you'd rather have FastAPI: use `python-fastapi-crud` (same demo).

## Stack

- **Hono** — small, fast, ergonomic. Web Standards under the hood.
- **TypeScript** strict + ESM
- **Zod** for request body and query validation
- **Vitest** for tests; integration tests use `app.request()` (no live HTTP)
- **`tsx`** for dev mode; production runs the compiled JS

## Layout

```
src/
├── server.ts            # Hono app, exported (used by tests + index.ts)
├── index.ts             # Entry: starts the server
├── store.ts             # In-memory store
├── items.ts             # CRUD routes mounted at /items
├── schemas.ts           # Zod schemas
└── __tests__/
    └── items.test.ts    # Integration tests via app.request()
```

## Quick start

```bash
pnpm install
pnpm dev      # tsx watch mode
pnpm test     # vitest
pnpm build    # compile to dist/
pnpm start    # node dist/index.js
```

With `just`:

```bash
just install
just dev
just test
just build
just run-docker
```

## API

```
GET    /health
GET    /items?limit=&offset=
POST   /items                  body: { name, description? }
GET    /items/:id
PATCH  /items/:id              body: { name?, description? }
DELETE /items/:id
```

## Pairs with `python-fastapi-crud`

Run both via the included `compose.yml`:

```bash
docker compose -f compose.yml -f ../python-fastapi-crud/compose.yml up
# Hono on :3000, FastAPI on :8000
```

(The compose files merge — internal DNS lets each call the other by service name.)

## Design notes

- **Hono apps export the app object**, not a server. `app.request("/items")` runs the full handler chain in-memory — that's why tests are fast.
- **Zod schemas are split** between request shapes and "internal" item shapes. The `Item` returned to clients is constructed from validated input + a server-assigned id and timestamps.
- **The store is in-memory.** For real persistence reach for SQLite (`better-sqlite3`) or Postgres (`postgres`/`drizzle-orm`).
