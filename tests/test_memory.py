from __future__ import annotations

from nexus.memory.short_term import ShortTermMemory


def test_short_term_memory_set_get() -> None:
    mem = ShortTermMemory(max_entries=5, ttl_seconds=60)
    mem.set("k", {"v": 1})
    assert mem.get("k") == {"v": 1}
