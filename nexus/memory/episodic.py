"""Episodic memory for completed goals."""
from __future__ import annotations

from datetime import datetime
from typing import Any


class EpisodicMemoryStore:
    """Stores complete execution traces for re-use."""

    def __init__(self) -> None:
        self._episodes: list[dict[str, Any]] = []

    def add(self, goal: str, task_tree: dict[str, Any], outputs: dict[str, Any], quality_score: float, duration: float) -> None:
        self._episodes.append(
            {
                "goal": goal,
                "task_tree": task_tree,
                "outputs": outputs,
                "quality_score": quality_score,
                "timestamp": datetime.utcnow().isoformat(),
                "duration": duration,
            }
        )

    def query(self, keyword: str) -> list[dict[str, Any]]:
        return [e for e in self._episodes if keyword.lower() in e["goal"].lower()]
