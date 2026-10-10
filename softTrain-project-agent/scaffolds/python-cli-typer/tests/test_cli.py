"""End-to-end tests via Typer's CliRunner."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from mycli.cli import app


@pytest.fixture
def store(tmp_path: Path) -> Path:
    return tmp_path / "tasks.json"


@pytest.fixture
def run(store: Path):
    runner = CliRunner()

    def invoke(*args: str):
        return runner.invoke(app, ["--store", str(store), *args])

    return invoke


def test_add_and_list(run):
    r = run("add", "first task")
    assert r.exit_code == 0
    assert "first task" in r.stdout

    r2 = run("list")
    assert r2.exit_code == 0
    assert "first task" in r2.stdout


def test_done_flow(run):
    run("add", "buy milk")
    r = run("done", "1")
    assert r.exit_code == 0
    r2 = run("list", "--done")
    assert "buy milk" in r2.stdout


def test_done_unknown_id_returns_1(run):
    r = run("done", "999")
    assert r.exit_code == 1
    assert "error" in r.stdout.lower()


def test_stats(run):
    run("add", "a")
    run("add", "b")
    run("done", "1")
    r = run("stats")
    assert "total: 2" in r.stdout
    assert "done: 1" in r.stdout


def test_filter_by_tag(run):
    run("add", "a", "--tag", "work")
    run("add", "b", "--tag", "home")
    r = run("list", "--tag", "work")
    assert "a" in r.stdout
    assert "b" not in r.stdout
