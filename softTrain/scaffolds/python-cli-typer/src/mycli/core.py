"""Pure business logic. No Typer, no Rich — fully testable in isolation."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class Task:
    id: int
    title: str
    tag: str | None = None
    done: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Task":
        return cls(**d)


def add_task(tasks: list[Task], title: str, tag: str | None = None) -> Task:
    next_id = (max((t.id for t in tasks), default=0)) + 1
    new = Task(id=next_id, title=title, tag=tag)
    tasks.append(new)
    return new


def mark_done(tasks: list[Task], task_id: int) -> Task:
    for t in tasks:
        if t.id == task_id:
            t.done = True
            return t
    raise KeyError(f"task {task_id} not found")


def filter_tasks(tasks: list[Task], *, tag: str | None = None, done: bool | None = None) -> list[Task]:
    out = tasks
    if tag is not None:
        out = [t for t in out if t.tag == tag]
    if done is not None:
        out = [t for t in out if t.done == done]
    return out


def stats(tasks: list[Task]) -> dict[str, int]:
    return {
        "total": len(tasks),
        "done": sum(1 for t in tasks if t.done),
        "open": sum(1 for t in tasks if not t.done),
    }
