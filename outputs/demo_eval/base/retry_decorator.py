def retry(max_attempts=3, base_delay=0.0, backoff_factor=2.0, exceptions=(Exception,)):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    attempts += 1
            return fn(*args, **kwargs)
        return wrapper
    return decorator
