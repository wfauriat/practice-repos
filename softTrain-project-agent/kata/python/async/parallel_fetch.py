"""
Implement `parallel_fetch(urls, fetcher, concurrency)` which calls `fetcher(url)` for each
URL with at most `concurrency` calls in flight at once. Return results in the same order
as the inputs.

`fetcher` is an async callable. Use this signature so tests can pass a fake.

>>> import asyncio
>>> async def fake(u): await asyncio.sleep(0.01); return u.upper()
>>> asyncio.run(parallel_fetch(["a", "b", "c"], fake, concurrency=2))
['A', 'B', 'C']
"""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def parallel_fetch(
    urls: list[str],
    fetcher: Callable[[str], Awaitable[T]],
    concurrency: int = 5,
) -> list[T]:
    raise NotImplementedError


# --- tests ---
import pytest


@pytest.mark.asyncio
async def test_preserves_order():
    async def fetch(u: str) -> str:
        return u.upper()

    out = await parallel_fetch(["a", "b", "c"], fetch, concurrency=2)
    assert out == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_respects_concurrency_limit():
    in_flight = 0
    max_in_flight = 0
    lock = asyncio.Lock()

    async def fetch(u: str) -> str:
        nonlocal in_flight, max_in_flight
        async with lock:
            in_flight += 1
            max_in_flight = max(max_in_flight, in_flight)
        await asyncio.sleep(0.02)
        async with lock:
            in_flight -= 1
        return u

    await parallel_fetch([f"u{i}" for i in range(10)], fetch, concurrency=3)
    assert max_in_flight <= 3


@pytest.mark.asyncio
async def test_empty():
    async def fetch(u: str) -> str:
        return u

    assert await parallel_fetch([], fetch, concurrency=5) == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
