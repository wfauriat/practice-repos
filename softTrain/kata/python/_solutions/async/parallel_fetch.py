"""Reference solution for async/parallel_fetch."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


async def parallel_fetch(
    urls: list[str],
    fetcher: Callable[[str], Awaitable[T]],
    concurrency: int = 5,
) -> list[T]:
    sem = asyncio.Semaphore(concurrency)

    async def bounded(u: str) -> T:
        async with sem:
            return await fetcher(u)

    return await asyncio.gather(*(bounded(u) for u in urls))
