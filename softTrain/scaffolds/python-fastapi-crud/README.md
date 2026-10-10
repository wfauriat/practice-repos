# python-fastapi-crud

A minimal but real FastAPI service: HTTP, validation (Pydantic v2), DB (SQLAlchemy 2.x + SQLite), tests (pytest + httpx), Docker, and a Justfile of canonical commands.

## When to reach for this

- You need a small Python web service with a real DB, not a toy in-memory one.
- You want **validation, persistence, and tests** wired together from the start.
- You'd like a Docker image to ship.

If you only need a CLI: use `python-cli-typer` instead. If you need notebooks: `python-data-notebook`.

## Layout

```
.
├── app/
│   ├── main.py        # FastAPI app + routers
│   ├── db.py          # Engine, sessionmaker, Base, get_session dependency
│   ├── models.py      # SQLAlchemy ORM models
│   ├── schemas.py     # Pydantic request/response models
│   └── routes/
│       └── items.py   # /items CRUD endpoints
├── tests/
│   ├── conftest.py    # In-memory test DB fixture
│   └── test_items.py  # End-to-end via httpx.AsyncClient
├── alembic/           # Migrations (dev-only convenience uses create_all)
├── Dockerfile         # Multi-stage build
├── compose.yml        # Local-stack: just this service
├── Justfile           # `just --list` for canonical commands
├── pyproject.toml     # Package metadata
├── requirements.txt   # Runtime deps
└── requirements-dev.txt
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# Run tests
pytest

# Run the dev server
uvicorn app.main:app --reload

# Hit the API
curl http://localhost:8000/items
curl -X POST http://localhost:8000/items \
  -H 'content-type: application/json' \
  -d '{"name":"first","description":"hello"}'
```

With `just`:

```bash
just install   # create venv, install deps
just test
just dev       # uvicorn --reload
just lint
just run-docker
```

## Database mode

By default the app uses **`Base.metadata.create_all()` on startup** to create the SQLite schema. This keeps the scaffold simple to run.

For real-world projects, use Alembic:

```bash
# Generate a new migration after editing models.py
alembic revision --autogenerate -m "add foo to items"

# Apply migrations
alembic upgrade head
```

The `alembic/` directory is configured against `app.db.Base.metadata`. Disable the `create_all` line in `app/main.py` once you're using migrations.

## Design notes (for future-you)

- **Pydantic v2 + SQLAlchemy 2.x**: kept separate. ORM models live in `models.py`, request/response shapes in `schemas.py`. Don't conflate them.
- **`Annotated[Session, Depends(get_session)]`** is the modern dependency-injection idiom. Each request gets its own session; the dependency closes it.
- **Tests use `httpx.AsyncClient` against `app=app`** (no live HTTP — much faster) and an in-memory SQLite per test.
- **Pagination**: `GET /items?limit=50&offset=0`. Cursor pagination is better for large data; for this scaffold offset is sufficient.
