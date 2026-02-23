from __future__ import annotations

import time
from collections import defaultdict, deque


class RateLimiter:
    """Token-bucket-like per-tool limiter."""

    def __init__(self) -> None:
        self.calls: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=100))

    def allow(self, tool: str, max_per_minute: int) -> bool:
        now = time.time()
        bucket = self.calls[tool]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= max_per_minute:
            return False
        bucket.append(now)
        return True
