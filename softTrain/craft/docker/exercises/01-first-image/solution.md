# Solution — first Dockerfile

```dockerfile
# Dockerfile

FROM python:3.12-slim

WORKDIR /app

# Install deps first, with their own COPY, so the layer is cached
# unless requirements.txt itself changes.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the app code. Edits to app.py will only invalidate this layer
# and the layers after, NOT the pip install layer.
COPY . .

CMD ["python", "app.py"]
```

```bash
docker build -t lab01 .
docker run --rm lab01
```

## Power-user notes

### The two-step COPY trick

```dockerfile
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . .
```

is *not* equivalent to:

```dockerfile
COPY . .
RUN pip install -r requirements.txt
```

Layer caching keys on file changes. With the first version, editing `app.py` does NOT re-trigger pip install. With the second, every code change re-installs all your Python deps. The first version saves you minutes per build cycle.

### `--no-cache-dir`

`pip install --no-cache-dir` skips writing the wheel cache to `/root/.cache`. This shaves megabytes off the image. (For a build cache that survives between *images*, see [BuildKit cache mounts](https://docs.docker.com/build/cache/) — `RUN --mount=type=cache,target=/root/.cache/pip pip install ...`.)

### `python:3.12-slim` vs `python:3.12` vs `python:3.12-alpine`

- **`python:3.12`** — Debian-based, full toolchain. Big (~1GB) but compatible with everything.
- **`python:3.12-slim`** — Debian, no build tools. Smaller (~150MB). Good default.
- **`python:3.12-alpine`** — musl libc. Smallest (~50MB) but some Python wheels (esp. pandas, scipy) don't ship for musl, so you end up compiling from source. Often a net loss.

Default to slim. Reach for alpine only if you've measured the size win is real and you've confirmed your deps work.

### Non-root user

```dockerfile
RUN useradd --create-home --uid 1000 app
USER app
```

Reduces blast radius if the container is compromised. The FastAPI scaffold's Dockerfile has this.

### `.dockerignore` saves you

Without one, `COPY . .` includes `.git`, `node_modules`, `.venv`, `__pycache__`, all your build artifacts. A minimal `.dockerignore`:

```
.git
.gitignore
**/__pycache__
**/*.pyc
.venv
node_modules
.env
.env.*
```

Without this, you'll bake secrets, cruft, and gigabytes of noise into your image.
