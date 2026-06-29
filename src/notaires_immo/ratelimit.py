"""Minimal token-bucket rate limiter (synchronous)."""

from __future__ import annotations

import time


class RateLimiter:
    """Enforce a minimum delay between calls.

    Default: 1.1 seconds between requests (≈ 54 req/min), which is polite for
    a daily-batch use case.  Pass ``min_delay=0`` to disable throttling.
    """

    def __init__(self, min_delay: float = 1.1) -> None:
        self._min_delay = min_delay
        self._last_call: float = 0.0

    def wait(self) -> None:
        if self._min_delay <= 0:
            return
        elapsed = time.monotonic() - self._last_call
        remaining = self._min_delay - elapsed
        if remaining > 0:
            time.sleep(remaining)
        self._last_call = time.monotonic()
