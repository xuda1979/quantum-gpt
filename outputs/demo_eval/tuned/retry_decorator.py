import time
import functools

def retry(max_attempts=3, base_delay=0.0, backoff_factor=2.0, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        if delay > 0:
                            time.sleep(delay)
                        delay *= backoff_factor
            raise last_exc
        return wrapper
    return decorator
