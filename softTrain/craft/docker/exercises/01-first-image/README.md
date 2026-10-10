# Lab 01 — your first Dockerfile

## Setup

```bash
bash craft/docker/exercises/01-first-image/setup.sh
cd craft/docker/_sandbox/01-first-image
```

You'll find a tiny Python script (`app.py`) and a `requirements.txt`. **There is no Dockerfile.**

## Goal

Write a `Dockerfile` such that:

```bash
docker build -t lab01 .
docker run --rm lab01
```

prints the expected output (run `python3 app.py` directly to see what it should be).

## Hints

- Start `FROM python:3.12-slim`.
- Use `WORKDIR` to set the working directory inside the image.
- `COPY requirements.txt ./` then `pip install -r requirements.txt` *before* copying the rest of the code — this is the layer-caching trick. (You'll feel the value of this in lab 03.)
- `CMD ["python", "app.py"]` is the entrypoint.

## Stretch

- Switch the base image from `python:3.12-slim` to `python:3.12-alpine` and see how much smaller the image gets. Note any breakage (alpine uses musl libc, not glibc — some pip wheels won't work).
- Add a non-root `USER` for safety.
