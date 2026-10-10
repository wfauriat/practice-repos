"""Typer-decorated CLI surface. Stays thin — business logic lives in core.py."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from mycli import core, store

app = typer.Typer(help="A tiny task tracker.", no_args_is_help=True)
console = Console()


def _store_path(ctx: typer.Context) -> Path:
    return ctx.obj["store_path"] if ctx.obj else store.default_path()


@app.callback()
def _root(
    ctx: typer.Context,
    store_path: Annotated[
        Path | None,
        typer.Option("--store", help="Path to the tasks JSON file."),
    ] = None,
):
    ctx.obj = {"store_path": store_path or store.default_path()}


@app.command()
def add(
    ctx: typer.Context,
    title: Annotated[str, typer.Argument(help="Task title.")],
    tag: Annotated[str | None, typer.Option("--tag", "-t", help="Optional tag.")] = None,
) -> None:
    """Add a new task."""
    path = _store_path(ctx)
    tasks = store.load(path)
    new = core.add_task(tasks, title=title, tag=tag)
    store.save(path, tasks)
    console.print(f"[green]+[/green] [{new.id}] {new.title}")


@app.command(name="list")
def list_cmd(
    ctx: typer.Context,
    tag: Annotated[str | None, typer.Option("--tag", "-t")] = None,
    done: Annotated[bool | None, typer.Option("--done/--open")] = None,
) -> None:
    """List tasks, optionally filtered."""
    path = _store_path(ctx)
    tasks = core.filter_tasks(store.load(path), tag=tag, done=done)
    if not tasks:
        console.print("[dim]no tasks[/dim]")
        return
    table = Table(show_header=True, header_style="bold")
    table.add_column("id", justify="right")
    table.add_column("title")
    table.add_column("tag")
    table.add_column("done", justify="center")
    for t in tasks:
        table.add_row(str(t.id), t.title, t.tag or "", "✓" if t.done else "")
    console.print(table)


@app.command()
def done(
    ctx: typer.Context,
    task_id: Annotated[int, typer.Argument(help="Task ID to mark done.")],
) -> None:
    """Mark a task as done."""
    path = _store_path(ctx)
    tasks = store.load(path)
    try:
        t = core.mark_done(tasks, task_id)
    except KeyError as e:
        console.print(f"[red]error:[/red] {e}")
        raise typer.Exit(code=1) from None
    store.save(path, tasks)
    console.print(f"[green]✓[/green] [{t.id}] {t.title}")


@app.command()
def stats(ctx: typer.Context) -> None:
    """Show task counts."""
    path = _store_path(ctx)
    s = core.stats(store.load(path))
    console.print(f"total: {s['total']}  done: {s['done']}  open: {s['open']}")


if __name__ == "__main__":
    app()
