import time
import functools
from typing import Any, Callable


def retry(
    max_attempts: int = 3,
    base_delay: float = 0.0,
    backoff_factor: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable:
    """Decorator that retries a function on specified exceptions.

    - max_attempts: total attempts (1 = no retry)
    - base_delay: initial delay in seconds between retries
    - backoff_factor: multiply delay by this after each retry
    - exceptions: tuple of exception types to catch

    Raises the last exception if all attempts fail.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        if delay > 0:
                            time.sleep(delay)
                        delay *= backoff_factor
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorator
