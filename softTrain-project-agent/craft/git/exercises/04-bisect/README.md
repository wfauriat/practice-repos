# Lab 04 — git bisect

## Setup

```bash
bash craft/git/exercises/04-bisect/setup.sh
cd craft/git/_sandbox/04-bisect
```

## Scenario

You have a small repo with **a series of 12 commits**. The very first commit (call it `A`) is known to be **good**. The latest commit on `main` is known to be **broken**: running `bash test.sh` exits with non-zero.

Somewhere in the 11 intermediate commits, somebody introduced a bug that broke `test.sh`.

## Goal

Use `git bisect` to find the **specific commit** that introduced the regression. Confirm by inspecting the commit's diff — you should be able to point at the line that broke things.

## Hints

- `git bisect start`, `git bisect bad`, `git bisect good <SHA>`. Then mark each commit good or bad as bisect checks them out.
- You can run `git bisect run bash test.sh` to make bisect drive the test for you. Try it both ways — manual first to feel the rhythm.
