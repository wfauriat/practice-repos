"""Reference solution for collections/group_by."""

from collections.abc import Callable, Iterable
from typing import TypeVar

K = TypeVar("K")
V = TypeVar("V")


def group_by(items: Iterable[V], key: Callable[[V], K]) -> dict[K, list[V]]:
    out: dict[K, list[V]] = {}
    for item in items:
        out.setdefault(key(item), []).append(item)
    return out
