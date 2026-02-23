"""Short-term memory with TTL and LRU eviction."""
from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ShortTermEntry:
    value: Any
    expires_at: float


class ShortTermMemory:
    """In-memory TTL key-value store shared by all agents."""

    def __init__(self, max_entries: int = 50, ttl_seconds: int = 3600) -> None:
        self.max_entries = max_entries
        self.ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, ShortTermEntry] = OrderedDict()

    def set(self, key: str, value: Any) -> None:
        self._cleanup()
        if key in self._store:
            self._store.pop(key)
        self._store[key] = ShortTermEntry(value=value, expires_at=time.time() + self.ttl_seconds)
        self._evict_if_needed()

    def get(self, key: str) -> Any | None:
        self._cleanup()
        entry = self._store.get(key)
        if not entry:
            return None
        self._store.move_to_end(key)
        return entry.value

    def stats(self) -> dict[str, int]:
        self._cleanup()
        return {"size": len(self._store), "capacity": self.max_entries}

    def _cleanup(self) -> None:
        now = time.time()
        expired = [k for k, v in self._store.items() if v.expires_at < now]
        for key in expired:
            self._store.pop(key, None)

    def _evict_if_needed(self) -> None:
        if len(self._store) > int(self.max_entries * 0.8):
            # lightweight compression: keep only latest half of entries
            while len(self._store) > self.max_entries // 2:
                self._store.popitem(last=False)
        while len(self._store) > self.max_entries:
            self._store.popitem(last=False)
