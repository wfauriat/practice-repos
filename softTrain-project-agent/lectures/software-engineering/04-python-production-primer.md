# Python production primer

## Abstract

Most Python developers learn the language by writing scripts that work. Production Python requires a different standard: code that can be read six months later, debugged by someone else, composed into larger systems, and operated in an environment where `print` has no audience. The gap is not syntax — it's five habits that experienced Python developers apply automatically and beginners skip entirely: intentional project structure, type hints, proper logging, disciplined error handling, and context managers. This lecture covers each habit, why it exists, and the tradeoffs worth knowing.

## Motivation

A script that runs correctly on your machine is not the same thing as production code. The difference shows up when:

- A colleague tries to import your module and gets a circular import error
- A bug surfaces in production and `print` statements tell you nothing because stdout was captured
- An exception propagates ten frames up the stack and the catcher has no idea what kind of error to expect
- A file handle is left open because an exception was raised before `f.close()`

None of these failures are about knowing more syntax. They are about habits. The habits exist because production code lives in environments the author doesn't control: other people's machines, automated pipelines, long-running servers, containers with no TTY. Writing code that survives those environments is what "production-quality Python" means.

This lecture is not about advanced Python. It is about the minimum standard for code that other engineers — or future you — can work with safely.

## Core concepts

### 1. Project structure

A Python project is not a folder full of `.py` files. It has a shape that communicates intent and enables tooling.

**The `src/` layout:**

```
my_project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       ├── core.py
│       └── utils.py
├── tests/
│   └── test_core.py
├── pyproject.toml
└── README.md
```

Putting source code under `src/` prevents a subtle bug: if you run `python` from the project root, Python adds `.` to `sys.path`. Without `src/`, your installed package and your local source code are both importable simultaneously, and it is not obvious which one you are testing. The `src/` layout forces you to install the package before importing it, which means tests always run against the installed version.

**`__init__.py` is an interface declaration**, not just a marker. What you import in `__init__.py` is the public API of the package. What you leave out is an implementation detail. An empty `__init__.py` says "I have no opinion about my public API" — usually unintentional.

**`pyproject.toml`** is the modern single source of truth for project metadata, dependencies, and tool configuration (black, mypy, pytest). Avoid `setup.py`, `setup.cfg`, and `requirements.txt` as primary configuration. They are legacy.

### 2. Type hints

Type hints annotate function signatures and variable assignments with the types they expect or produce:

```python
def parse_user(raw: dict[str, str]) -> User | None:
    ...

def retry(fn: Callable[[], T], attempts: int = 3) -> T:
    ...
```

They do not change runtime behaviour. Python does not enforce them. Their value is entirely in tooling and communication:

- **mypy / pyright** catch type errors before runtime — the equivalent of a compiler for a dynamically typed language
- **IDE autocompletion** works correctly because the editor knows what `parse_user` returns
- **Readers** understand what a function expects without reading the body

**Practical rules:**
- Annotate all function signatures (parameters and return type). Skip internal variable annotations unless the type is non-obvious.
- Use `X | None` instead of `Optional[X]` (Python 3.10+). Use `list[str]` instead of `List[str]` (Python 3.9+).
- `Any` is a type hint that means "I give up." Use it sparingly. It disables all checking on that value.
- A function that returns nothing returns `None` — annotate it `-> None`. A function that never returns (raises unconditionally) annotates `-> NoReturn`.

### 3. Logging

`print` is not logging. In production:
- stdout may be captured, buffered, or discarded
- there is no timestamp, severity, or source location
- there is no way to turn it off without editing the code

The `logging` module fixes all of this:

```python
import logging

logger = logging.getLogger(__name__)

def process(record_id: int) -> None:
    logger.debug("processing record %s", record_id)
    try:
        result = expensive_operation(record_id)
        logger.info("processed record %s successfully", record_id)
    except ValueError as exc:
        logger.warning("skipping record %s: %s", record_id, exc)
    except Exception:
        logger.exception("unexpected error on record %s", record_id)
        raise
```

**`getLogger(__name__)`** creates a logger named after the current module (`my_package.core`, not a hardcoded string). This lets callers configure logging at any level of the hierarchy.

**Log levels as design decisions, not severity feelings:**
- `DEBUG` — internal state useful during development. Off in production.
- `INFO` — coarse-grained confirmation that things are working as expected. Operational checkpoints.
- `WARNING` — something unexpected happened, but the system recovered. Worth investigating.
- `ERROR` — something failed and the system could not recover. Requires attention.
- `CRITICAL` — the system cannot continue operating.

The instinct to log at `DEBUG` because "it's just a detail" and `WARNING` because "it's not really an error" produces logs nobody trusts. Design your levels: decide what an operator needs to see in production (`INFO` and above), and what you need to debug a problem (`DEBUG`).

**`logger.exception()`** logs at ERROR and automatically appends the current exception traceback. Always use this instead of `logger.error()` inside an `except` block.

**Libraries should never call `logging.basicConfig()`** — that is the application's job. Libraries configure nothing; they emit. Applications configure the handlers, formatters, and levels.

### 4. Error handling

The goal of error handling is to fail clearly at the right level, not to suppress exceptions.

**Define custom exception classes for expected failure modes:**

```python
class ConfigError(Exception):
    """Raised when configuration is missing or invalid."""

class UpstreamError(Exception):
    """Raised when an external service returns an unexpected response."""
    def __init__(self, service: str, status: int) -> None:
        self.service = service
        self.status = status
        super().__init__(f"{service} returned {status}")
```

Custom exceptions let callers catch *your* errors specifically without accidentally catching unrelated `ValueError` or `RuntimeError` from deeper in the stack. They are part of your module's public interface.

**The exception hierarchy matters.** Custom exceptions should inherit from `Exception`, not `BaseException`. `BaseException` includes `KeyboardInterrupt` and `SystemExit` — catching `BaseException` prevents Ctrl-C from working.

**Catch specifically, not broadly:**

```python
# Bad — catches everything, masks real bugs
try:
    result = parse(data)
except Exception:
    return None

# Good — catches only what you know how to handle
try:
    result = parse(data)
except (ValueError, KeyError) as exc:
    logger.warning("parse failed: %s", exc)
    return None
```

**Re-raise to preserve context:**

```python
try:
    connect(host)
except OSError as exc:
    raise UpstreamError("database", 503) from exc
```

`raise X from Y` chains exceptions: the original `OSError` is preserved as `__cause__`. The traceback shows both. Without `from exc`, the original error disappears.

**`finally` is for cleanup, not control flow.** Code in `finally` runs whether or not an exception occurred. Use it to release resources. Do not use it to return values or suppress exceptions — the behaviour becomes non-obvious quickly.

### 5. Context managers

A context manager guarantees that cleanup code runs, even if an exception is raised. The `with` statement is the interface:

```python
with open("data.csv") as f:
    contents = f.read()
# f is closed here — guaranteed, even if f.read() raised
```

Behind the scenes, `with` calls `__enter__` on entry and `__exit__` on exit. `__exit__` receives the exception information if one occurred, and can suppress it (by returning a truthy value) or let it propagate (by returning `None` or `False`).

**Write your own with `contextlib.contextmanager`:**

```python
from contextlib import contextmanager

@contextmanager
def temporary_directory() -> Generator[Path, None, None]:
    path = Path(tempfile.mkdtemp())
    try:
        yield path
    finally:
        shutil.rmtree(path)
```

Everything before `yield` is `__enter__`. Everything after (in `finally`) is `__exit__`. The `finally` ensures cleanup even if the caller raises inside the `with` block.

**Context managers are the correct solution for any resource that has an acquire/release lifecycle**: files, database connections, locks, temporary directories, HTTP sessions, GPU memory. If you find yourself writing `try/finally` to release a resource, consider whether a context manager would be clearer.

## Tradeoffs / counterpoints

### Type hints add friction — is it worth it?

On a 50-line script you run once: no. On a module that three people will import and extend over two years: yes, unambiguously. The cost is annotation time (modest) and occasionally fighting the type checker on genuinely dynamic code. The return is a class of bugs — wrong argument types, missing `None` checks, incorrect return assumptions — caught before runtime, which in a long-running service means before a production incident.

The real cost is partial adoption. A codebase with type hints on 60% of functions gives you the friction without the safety. The type checker cannot reason across the untyped gap. Either annotate consistently or don't bother.

`mypy --strict` is the useful target; it flags unannotated functions and disables implicit `Any`. Running it in CI makes the standard enforceable.

### Logging is verbose — when is `print` acceptable?

In a CLI tool that outputs to a user: `print` is correct. That's communication, not instrumentation. In a script that runs in a pipeline, a container, or a scheduled job: never `print` for internal state. The question to ask: "will a human read this interactively, or will a system need to filter, timestamp, and route it?" If the latter, use logging.

The cost of adding logging from the start is low. Retrofitting it into a script that has grown into a service is painful and often incomplete.

### Custom exceptions vs. built-in exceptions

Built-in exceptions (`ValueError`, `KeyError`, `TypeError`) communicate *what went wrong mechanically*. Custom exceptions communicate *what went wrong in your domain*. `ValueError: invalid configuration` forces callers to catch `ValueError`, which they may also need to catch for completely unrelated reasons elsewhere. `ConfigError` is unambiguous.

The counter-argument: custom exceptions add API surface. Callers must import your exception class to catch it. For small internal modules, built-in exceptions with clear messages are often sufficient. The rule of thumb: if you expect callers in other modules to specifically handle this failure mode, give it a custom class.

### "Easier to ask forgiveness than permission" (EAFP) vs. defensive checks

Python culture favours EAFP: attempt the operation, catch the exception, handle it. This is idiomatic and often cleaner than checking preconditions first. But EAFP applied carelessly produces exception-driven control flow that obscures intent. `try/except` should represent *exceptional* conditions, not ordinary branching logic. If you find yourself writing `try/except` to handle a case that occurs 30% of the time, consider whether an explicit conditional is clearer.

## Further reading

- **Fluent Python** by Luciano Ramalho — Chapters 7 (functions), 11 (interfaces), 14 (iterables/generators), 18 (context managers). The standard reference for idiomatic Python.
- **Python Logging HOWTO** — the official docs are genuinely good here. Read the section on logger hierarchy.
- **mypy documentation** — the `--strict` flag and the "common issues" section cover 80% of the friction you will encounter.
- **`pyproject.toml` specification** — PEP 518 and PEP 621. Short and worth reading once to understand what the file actually does.
- **"Hypermodern Python" by Claudio Jolowicz** — a blog series on modern Python project setup. Opinionated and practical.

## Discussion prompts

1. A colleague says type hints are redundant because "Python's dynamic typing is a feature — I can pass anything and the function will figure it out." What's the strongest version of their argument, and where does it break down in practice?

2. You have a function that reads a config file and raises `FileNotFoundError` if it doesn't exist. A caller wraps it in `try/except Exception` and returns a default config silently. What's wrong with this pattern, and how would you restructure it?

3. A library you depend on calls `logging.basicConfig()` at import time. What does this do to your application's logging configuration, and why is it a problem?

4. You have two options for handling a database connection in a long-running worker: (a) open the connection once at startup and reuse it, or (b) open and close a connection per task using a context manager. What are the tradeoffs? Under what conditions does each approach break?

5. A codebase uses `print` throughout for internal state. You're asked to "add logging." What's the right migration strategy, and what's the risk of doing it wrong?
