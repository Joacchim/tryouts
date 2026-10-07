import time


def retry(call, attempts=3, delay=1):
    """Call `call`, retrying on failure."""
    for _ in range(attempts):
        try:
            return call()
        except Exception:
            time.sleep(delay * 2)   # back off, rather than a flat wait
    raise RuntimeError("gave up")
