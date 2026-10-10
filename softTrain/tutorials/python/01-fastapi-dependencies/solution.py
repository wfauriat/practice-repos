"""Tutorial 01 — FastAPI dependencies (reference solution)."""

from functools import lru_cache
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException


# --- 1. Per-request dependency ------------------------------------------------

def request_id() -> str:
    return str(uuid4())


RequestId = Annotated[str, Depends(request_id)]


# --- 2. Cached dependency -----------------------------------------------------

class Settings:
    def __init__(self, env: str, secret_key: str) -> None:
        self.env = env
        self.secret_key = secret_key


@lru_cache
def get_settings() -> Settings:
    return Settings(env="dev", secret_key="not-a-secret")


SettingsDep = Annotated[Settings, Depends(get_settings)]


# --- 3. Composable dependency -------------------------------------------------

class User:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name


_USERS = {"alice": User(1, "alice"), "bob": User(2, "bob")}


def current_user(
    settings: SettingsDep,
    x_user_token: Annotated[str | None, Header()] = None,
) -> User:
    if x_user_token is None:
        raise HTTPException(status_code=401, detail="missing token")
    user = _USERS.get(x_user_token)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid token")
    return user


CurrentUser = Annotated[User, Depends(current_user)]


# --- The app ------------------------------------------------------------------

app = FastAPI()


@app.get("/whoami")
def whoami(req_id: RequestId, user: CurrentUser, settings: SettingsDep) -> dict:
    return {"request_id": req_id, "user_name": user.name, "env": settings.env}


# --- Test override demo (read this AFTER you finish) --------------------------

def example_override():
    """How you'd override `current_user` in a test, returning a fixed user."""
    from fastapi.testclient import TestClient

    def fake_user() -> User:
        return User(99, "test-user")

    app.dependency_overrides[current_user] = fake_user
    client = TestClient(app)
    r = client.get("/whoami")  # no token needed; the override runs instead
    assert r.json()["user_name"] == "test-user"
    app.dependency_overrides.clear()
