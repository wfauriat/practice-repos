# scaffolds/

The pattern dictionary. Each subdirectory is a **complete, tested, runnable** mini-project intended to be copied as the start of something new.

## Index

| Scaffold                | Stack                                                    | Reach for it when…                                  |
|-------------------------|----------------------------------------------------------|-----------------------------------------------------|
| `python-fastapi-crud/`  | FastAPI · Pydantic v2 · SQLAlchemy · SQLite · pytest     | You need a Python web service with a real DB       |
| `python-cli-typer/`     | Typer · Rich · pytest                                    | You need a CLI with subcommands and typed flags    |
| `python-data-notebook/` | Jupyter · pandas · papermill                             | You're starting a reproducible data analysis       |
| `ts-react-vite/`        | Vite · React 18 · TS · Tailwind v4 · TanStack Query · Vitest | You're starting a SPA frontend                |
| `ts-node-api/`          | Hono · TS · Zod · Vitest                                 | You need a Node HTTP service in TypeScript         |

## How to use a scaffold

```bash
# Copy and prep
tools/from-scaffold.sh python-fastapi-crud ~/code/my-new-api

# That's it — the script renames the package, drops stale .venv/node_modules,
# re-inits git, and prints next steps.
```

The new project's `README.md` has the per-stack setup commands.

## Adding a new scaffold

1. Pick a deliberately small but **realistic** demo (CRUD, a form, a typed CLI). Avoid toys.
2. Wire up: source, tests, lockfile, `Justfile`, `README.md` with a "When to reach for this" section.
3. Add an entry to the table above.
4. If it's worth it, add `Dockerfile` + `compose.yml`.
5. Verify a fresh `tools/from-scaffold.sh <new-scaffold> /tmp/test` produces something that runs out of the box.
