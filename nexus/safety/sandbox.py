from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SandboxPolicy:
    memory_limit_mb: int = 512
    cpu_limit: float = 1.0
    network_enabled: bool = False
    timeout_seconds: int = 30
