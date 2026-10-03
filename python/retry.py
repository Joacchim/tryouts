import time


def retry(call, attempts=3, delay=1):
    """Call `call`, retrying on failure."""
    for _ in range(attempts):
        try:
            return call()
        except Exception:
            time.sleep(delay)
    raise RuntimeError("gave up")
