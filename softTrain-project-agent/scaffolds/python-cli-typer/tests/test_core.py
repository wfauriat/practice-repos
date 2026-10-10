"""Unit tests on pure business logic. No CLI imports."""

import pytest

from mycli.core import Task, add_task, filter_tasks, mark_done, stats


def test_add_task_assigns_sequential_ids():
    tasks: list[Task] = []
    a = add_task(tasks, "first")
    b = add_task(tasks, "second")
    c = add_task(tasks, "third")
    assert [t.id for t in tasks] == [a.id, b.id, c.id]
    assert a.id < b.id < c.id


def test_add_task_with_tag():
    tasks: list[Task] = []
    t = add_task(tasks, "buy milk", tag="errands")
    assert t.tag == "errands"


def test_mark_done_changes_state():
    tasks: list[Task] = []
    t = add_task(tasks, "x")
    mark_done(tasks, t.id)
    assert tasks[0].done is True


def test_mark_done_missing_id_raises():
    with pytest.raises(KeyError):
        mark_done([], 99)


def test_filter_by_tag_and_done():
    tasks: list[Task] = []
    add_task(tasks, "a", tag="work")
    b = add_task(tasks, "b", tag="home")
    add_task(tasks, "c", tag="work")
    mark_done(tasks, b.id)

    assert [t.title for t in filter_tasks(tasks, tag="work")] == ["a", "c"]
    assert [t.title for t in filter_tasks(tasks, done=True)] == ["b"]
    assert filter_tasks(tasks, tag="home", done=False) == []


def test_stats():
    tasks: list[Task] = []
    add_task(tasks, "a")
    b = add_task(tasks, "b")
    mark_done(tasks, b.id)
    assert stats(tasks) == {"total": 2, "done": 1, "open": 1}
