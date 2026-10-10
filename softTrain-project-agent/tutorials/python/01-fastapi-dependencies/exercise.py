"""
Tutorial 01 — FastAPI dependencies (exercise).

Goal: build a tiny FastAPI app with three escalating uses of dependencies:
  1. A simple per-request dependency (request id).
  2. A cached dependency (settings loaded once).
  3. A composable dependency (current user, depending on settings).

Then write a test that overrides one of these dependencies.

You'll fill in the lines marked `# TUTOR: <hint>`.
"""

from functools import lru_cache
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, FastAPI, Header, HTTPException


# --- 1. Per-request dependency -------------------------------------------------

def request_id() -> str:
    # TUTOR: return a fresh UUID4 string. This dependency runs ONCE per request,
    # and FastAPI handles the lifecycle automatically.
    ...


# Use Annotated to give the dependency a reusable, typed alias.
# TUTOR: define `RequestId` as Annotated[str, Depends(request_id)].
# That alias is what you'll add as a parameter to your route.
RequestId = ...


# --- 2. Cached dependency -----------------------------------------------------

class Settings:
    def __init__(self, env: str, secret_key: str) -> None:
        self.env = env
        self.secret_key = secret_key


# TUTOR: write a `get_settings()` function decorated with @lru_cache so it's
# called only ONCE — the same Settings instance is reused for every request.
# Return a Settings(env="dev", secret_key="not-a-secret").
@lru_cache
def get_settings() -> Settings:
    ...


# TUTOR: define `SettingsDep = Annotated[Settings, Depends(get_settings)]`.
SettingsDep = ...


# --- 3. Composable dependency -------------------------------------------------

class User:
    def __init__(self, id: int, name: str) -> None:
        self.id = id
        self.name = name


def current_user(
    settings: SettingsDep,
    x_user_token: Annotated[str | None, Header()] = None,
) -> User:
    # TUTOR: if `x_user_token` is missing, raise HTTPException(401, "missing token").
    # Otherwise, "decode" it: in this toy example, the token is just "alice" or "bob".
    # If it's neither, raise HTTPException(401, "invalid token").
    # Return a User with id=1 for alice, id=2 for bob.
    ...


# TUTOR: define `CurrentUser = Annotated[User, Depends(current_user)]`.
CurrentUser = ...


# --- The app ------------------------------------------------------------------

app = FastAPI()


@app.get("/whoami")
def whoami(req_id: RequestId, user: CurrentUser, settings: SettingsDep) -> dict:
    # TUTOR: return a dict with keys: "request_id", "user_name", "env".
    ...
