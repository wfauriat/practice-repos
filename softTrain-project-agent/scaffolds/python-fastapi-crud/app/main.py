"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import Base, engine
from app.routes import items


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Dev-mode convenience: build the schema if it isn't there yet.
    # Switch to Alembic migrations for real deployments.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="python-fastapi-crud", version="0.1.0", lifespan=lifespan)
app.include_router(items.router)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}
