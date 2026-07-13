"""Run coroutines with a per-task timeout and bounded retries.

Provides a single entry point `run_with_retry` that:
- awaits a coroutine factory up to `max_retries` times,
- applies a per-attempt `timeout`,
- retries on `asyncio.TimeoutError` and any exception in `retry_on`,
- uses exponential backoff `base_delay * 2**(attempt-1)` between retries,
- returns the result on success,
- raises the last exception after all retries are exhausted.
"""

import asyncio
from collections.abc import Awaitable, Callable


class RetryExhausted(Exception):
    def __init__(self, attempts: int, last_exc: BaseException):
        super().__init__(f"all {attempts} attempts failed: {last_exc!r}")
        self.attempts = attempts
        self.last_exc = last_exc


async def run_with_retry(
    coro_factory: Callable[[], Awaitable],
    *,
    timeout: float = 1.0,
    max_retries: int = 3,
    base_delay: float = 0.0,
    retry_on: tuple[type[BaseException], ...] = (asyncio.TimeoutError,),
) -> object:
    """Run `coro_factory()` with timeout and retries. Returns the result."""
    last_exc: BaseException | None = None
    for attempt in range(1, max_retries + 1):
        try:
            return await asyncio.wait_for(coro_factory(), timeout=timeout)
        except retry_on as e:  # noqa: PERF203
            last_exc = e
        except Exception:
            # Non-retryable: raise immediately
            raise
        if attempt < max_retries and base_delay > 0:
            await asyncio.sleep(base_delay * (2 ** (attempt - 1)))
    assert last_exc is not None
    raise RetryExhausted(max_retries, last_exc)


async def gather_with_retry(
    coro_factories: list[Callable[[], Awaitable]],
    **kwargs,
) -> list[object]:
    """Run many coro_factories concurrently with per-task retry. Returns results
    in input order; raises RetryExhausted is collected per task and re-raised
    as a combined `RuntimeError` listing the failed indices."""

    async def _one(factory):
        return await run_with_retry(factory, **kwargs)

    results = await asyncio.gather(*[_one(f) for f in coro_factories], return_exceptions=True)
    failed = [(i, r) for i, r in enumerate(results) if isinstance(r, BaseException)]
    if failed:
        idxs = [i for i, _ in failed]
        raise RuntimeError(
            f"gather_with_retry failed on tasks {idxs}; first error: {failed[0][1]!r}"
        )
    return list(results)
