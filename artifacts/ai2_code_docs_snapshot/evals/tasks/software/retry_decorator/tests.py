import importlib.util


def _load(candidate_path: str):
    spec = importlib.util.spec_from_file_location("candidate", candidate_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_tests(candidate_path: str) -> dict:
    module = _load(candidate_path)
    failures = []

    # Test 1: succeeds on first try
    call_count = {"n": 0}

    @module.retry(max_attempts=3)
    def always_ok():
        call_count["n"] += 1
        return "ok"

    result = always_ok()
    if result != "ok":
        failures.append(f"always_ok returned {result!r}, expected 'ok'")
    if call_count["n"] != 1:
        failures.append(f"always_ok called {call_count['n']} times, expected 1")

    # Test 2: fails twice then succeeds
    counter = {"n": 0}

    @module.retry(max_attempts=3, base_delay=0.0)
    def flaky():
        counter["n"] += 1
        if counter["n"] < 3:
            raise ValueError("not yet")
        return "done"

    result = flaky()
    if result != "done":
        failures.append(f"flaky returned {result!r}, expected 'done'")
    if counter["n"] != 3:
        failures.append(f"flaky called {counter['n']} times, expected 3")

    # Test 3: exhausts all attempts
    @module.retry(max_attempts=2, base_delay=0.0)
    def always_fail():
        raise RuntimeError("boom")

    try:
        always_fail()
        failures.append("always_fail did not raise")
    except RuntimeError as e:
        if str(e) != "boom":
            failures.append(f"always_fail raised RuntimeError({e!r}), expected 'boom'")
    except Exception as e:
        failures.append(f"always_fail raised {type(e).__name__}, expected RuntimeError")

    # Test 4: only catches specified exceptions
    counter2 = {"n": 0}

    @module.retry(max_attempts=3, base_delay=0.0, exceptions=(ValueError,))
    def wrong_exc():
        counter2["n"] += 1
        raise TypeError("wrong type")

    try:
        wrong_exc()
        failures.append("wrong_exc did not raise")
    except TypeError:
        if counter2["n"] != 1:
            failures.append(f"wrong_exc called {counter2['n']} times, expected 1 (no retry on TypeError)")
    except Exception as e:
        failures.append(f"wrong_exc raised {type(e).__name__}, expected TypeError")

    # Test 5: preserves function name (functools.wraps)
    @module.retry(max_attempts=1)
    def named_func():
        """A docstring."""
        return 42

    if named_func.__name__ != "named_func":
        failures.append(f"__name__={named_func.__name__!r}, expected 'named_func'")
    if named_func.__doc__ != "A docstring.":
        failures.append(f"__doc__ not preserved")

    # Test 6: max_attempts=1 means no retry
    counter3 = {"n": 0}

    @module.retry(max_attempts=1, base_delay=0.0)
    def once():
        counter3["n"] += 1
        raise ValueError("fail")

    try:
        once()
    except ValueError:
        pass
    if counter3["n"] != 1:
        failures.append(f"max_attempts=1 called {counter3['n']} times, expected 1")

    return {
        "passed": not failures,
        "details": failures or ["Retry decorator handles all cases correctly"],
    }
