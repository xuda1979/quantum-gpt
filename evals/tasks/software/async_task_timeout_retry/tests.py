import asyncio
import importlib.util


def _load(path: str):
    spec = importlib.util.spec_from_file_location("candidate", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def run_tests(candidate_path: str) -> dict:
    failures: list[str] = []
    try:
        mod = _load(candidate_path)
    except Exception as e:  # noqa: BLE001
        return {"passed": False, "details": [f"import failed: {e}"]}

    async def fast_ok():
        await asyncio.sleep(0.01)
        return "ok"

    async def slow():
        await asyncio.sleep(5.0)
        return "never"

    async def flaky(tries_needed: int, state={"n": 0}):
        state["n"] += 1
        if state["n"] < tries_needed:
            raise asyncio.TimeoutError()
        return f"ok-after-{state['n']}"

    # 1. Fast successful call returns the result
    try:
        r = asyncio.run(mod.run_with_retry(fast_ok, timeout=1.0, max_retries=1))
        if r != "ok":
            failures.append(f"fast_ok returned {r!r}")
    except Exception as e:  # noqa: BLE001
        failures.append(f"fast_ok raised: {e}")

    # 2. Timeout raises RetryExhausted after retries
    try:
        asyncio.run(mod.run_with_retry(slow, timeout=0.05, max_retries=2, base_delay=0.0))
        failures.append("slow task did not raise RetryExhausted")
    except mod.RetryExhausted as e:
        if e.attempts != 2:
            failures.append(f"RetryExhausted attempts = {e.attempts}, expected 2")
    except Exception as e:  # noqa: BLE001
        failures.append(f"slow task raised unexpected: {e!r}")

    # 3. Retry-then-success on TimeoutError
    try:
        # Need a fresh closure per run because `flaky` mutates shared state.
        state = {"n": 0}

        async def flaky2(tries_needed=2, state=state):
            state["n"] += 1
            if state["n"] < tries_needed:
                raise asyncio.TimeoutError()
            return f"ok-after-{state['n']}"

        r = asyncio.run(mod.run_with_retry(flaky2, timeout=1.0, max_retries=3, base_delay=0.0))
        if r != "ok-after-2":
            failures.append(f"flaky2 returned {r!r}, expected 'ok-after-2'")
    except Exception as e:  # noqa: BLE001
        failures.append(f"flaky2 raised: {e!r}")

    # 4. Non-retryable exception is raised immediately, not retried
    counter = {"n": 0}

    async def boom():
        counter["n"] += 1
        raise ValueError("boom")

    try:
        asyncio.run(
            mod.run_with_retry(boom, timeout=1.0, max_retries=3, retry_on=(asyncio.TimeoutError,))
        )
        failures.append("non-retryable ValueError was swallowed")
    except ValueError:
        if counter["n"] != 1:
            failures.append(f"non-retryable was attempted {counter['n']} times, expected 1")
    except Exception as e:  # noqa: BLE001
        failures.append(f"non-retryable raised unexpected: {e!r}")

    # 5. gather_with_retry runs concurrently
    try:

        async def make(i):
            async def f():
                await asyncio.sleep(0.01)
                return i

            return f

        async def main():
            factories = [await make(i) for i in range(4)]
            return await mod.gather_with_retry(factories, timeout=1.0, max_retries=1)

        out = asyncio.run(main())
        if out != [0, 1, 2, 3]:
            failures.append(f"gather_with_retry returned {out!r}, expected [0,1,2,3]")
    except Exception as e:  # noqa: BLE001
        failures.append(f"gather_with_retry raised: {e!r}")

    return {
        "passed": not failures,
        "details": failures or ["async timeout + retry + exponential backoff + gather all correct"],
    }
