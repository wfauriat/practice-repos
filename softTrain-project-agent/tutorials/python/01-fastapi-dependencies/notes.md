# Notes — power-user tricks for FastAPI dependencies

(Read this only after you've finished the exercise.)

## 1. `Annotated` lets you reuse dependencies as types

The pre-`Annotated` form was:

```python
def whoami(user: User = Depends(current_user)) -> dict: ...
```

The modern form:

```python
CurrentUser = Annotated[User, Depends(current_user)]

def whoami(user: CurrentUser) -> dict: ...
```

This is **strictly better**: it works with mypy, plays nicely with `dataclass`-style code generation, and means you write `Depends(...)` once per dependency instead of once per route.

## 2. `@lru_cache` is the simplest way to make a singleton dependency

```python
@lru_cache
def get_settings() -> Settings: ...
```

FastAPI calls `get_settings()` on every request, but `lru_cache` returns the same instance. Don't reach for fancy DI containers for this; the language already gives you a singleton.

## 3. Dependencies compose naturally

`current_user` itself depends on `settings`. FastAPI builds the dependency graph and calls them in order. You can have N levels deep — DB session → repository → service → route — and FastAPI handles it.

The trade-off: too much depth and your stack traces become a forest. Keep it 2-3 deep typically.

## 4. `dependency_overrides` is the test seam

```python
app.dependency_overrides[current_user] = fake_user
```

This is FastAPI's built-in equivalent of "monkey-patching a `User` for the duration of a test." Cleaner than mocking `httpx.AsyncClient` or whatever your real `current_user` reaches into.

In `python-fastapi-crud/tests/conftest.py` you'll see the same pattern used to override `get_session` with an in-memory test DB.

## 5. Yield-based dependencies for setup/teardown

A dependency can be a generator that yields, then runs cleanup code:

```python
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

The `try/finally` runs **after** the response has been sent. This is how DB sessions, file handles, and span contexts are typically managed.

## 6. `Depends(...)` for "use side effects, ignore return"

If a dependency just needs to *run* (say, an auth gate that raises on bad input), you can use it without giving it a parameter name:

```python
@app.get("/admin", dependencies=[Depends(require_admin)])
def admin_panel(): ...
```

Useful for cross-cutting concerns where the route doesn't care about the dependency's return value.

## 7. Watch out for: lazy imports break dependency overrides

If you import `current_user` from one module in your tests but the app uses a re-exported version, `app.dependency_overrides[current_user]` won't match. **Always override using the same import path the app sees.**

## Further reading

- [FastAPI docs — Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI docs — Testing dependencies with overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
