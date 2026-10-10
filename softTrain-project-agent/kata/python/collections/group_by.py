"""
Implement a generic `group_by(items, key)` that returns `dict[K, list[V]]`.

>>> group_by([1, 2, 3, 4], lambda n: n % 2)
{1: [1, 3], 0: [2, 4]}
>>> group_by(["apple", "ant", "bat"], lambda s: s[0])
{'a': ['apple', 'ant'], 'b': ['bat']}

Notes:
- Order of keys must follow first-encounter order.
- Within each list, items appear in their original input order.
"""

from collections.abc import Callable, Iterable
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def group_by(items: Iterable[V], key: Callable[[V], K]) -> dict[K, list[V]]:
    raise NotImplementedError


# --- tests ---
import pytest


def test_evens_and_odds():
    assert group_by([1, 2, 3, 4], lambda n: n % 2) == {1: [1, 3], 0: [2, 4]}


def test_first_letter():
    assert group_by(["apple", "ant", "bat"], lambda s: s[0]) == {
        "a": ["apple", "ant"],
        "b": ["bat"],
    }


def test_empty():
    assert group_by([], lambda x: x) == {}


def test_preserves_order_within_groups():
    items = [("a", 1), ("a", 2), ("b", 3), ("a", 4)]
    grouped = group_by(items, lambda t: t[0])
    assert grouped["a"] == [("a", 1), ("a", 2), ("a", 4)]


def test_works_with_iterators():
    grouped = group_by((n for n in range(5)), lambda n: n % 2)
    assert grouped == {0: [0, 2, 4], 1: [1, 3]}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
