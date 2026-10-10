"""JSON-file persistence layer. One responsibility: load and save a list of tasks."""

import json
from pathlib import Path

from mycli.core import Task


def default_path() -> Path:
    return Path.home() / ".mycli-tasks.json"


def load(path: Path) -> list[Task]:
    if not path.exists():
        return []
    raw = json.loads(path.read_text())
    return [Task.from_dict(d) for d in raw]


def save(path: Path, tasks: list[Task]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([t.to_dict() for t in tasks], indent=2))
