# python-cli-typer

A small but real Python CLI: subcommands, typed flags, JSON-file persistence, pretty output, and tests.

## When to reach for this

- You need a script with **subcommands and options**, not just `argparse` glue.
- You want a CLI you can ship: tested, typed, with a help screen that's pleasant to read.
- You want to see how to make business logic **testable** when wrapped in a CLI.

If you need a web service: use `python-fastapi-crud`. If you need notebooks: `python-data-notebook`.

## Demo

A simple task tracker stored in a JSON file:

```bash
mycli add "buy milk"                  # add a task
mycli add "write blog post" --tag work
mycli list                            # show all
mycli list --tag work                 # filter
mycli done 1                          # mark complete
mycli stats                           # summary
```

## Layout

```
src/mycli/
├── __init__.py
├── __main__.py     # so `python -m mycli` works
├── cli.py          # Typer app + subcommand wiring
├── core.py         # Pure business logic (no CLI imports)
└── store.py        # JSON-file storage layer
tests/
├── test_core.py    # Unit tests on pure logic
└── test_cli.py     # End-to-end via Typer's CliRunner
```

The split between `core.py` (pure) and `cli.py` (Typer-decorated) is deliberate — *the CLI is a thin wrapper over a real API.* Test core directly; test CLI only for argument parsing + exit codes.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .

mycli --help
mycli add "first task"
mycli list

pytest
```

With `just`:

```bash
just install   # venv + dev install
just test
just lint
just run -- add "from just"
```

## Design notes

- **`Annotated[..., typer.Option(...)]`** is the recommended idiom; it works with mypy and with Pydantic-style type help.
- The store is just a JSON file. For real apps reach for SQLite (see `python-fastapi-crud`). The point here is shape, not scale.
- **Exit codes**: 0 = success, 1 = expected failure (e.g. task not found), 2 = bad usage (Typer handles this).
- Output uses `rich` for tables. If you pipe to `grep`, Rich detects no-TTY and outputs plain text — you don't need to special-case it.
