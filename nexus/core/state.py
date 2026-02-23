"""Global state and session tracking."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, TypedDict
from uuid import uuid4


class GlobalState(TypedDict):
    goal: str
    task_tree: dict[str, Any]
    execution_log: list[dict[str, Any]]
    agent_outputs: dict[str, dict[str, Any]]
    memory_context: list[dict[str, Any]]
    status: Literal["planning", "executing", "reflecting", "done", "failed"]
    iteration: int
    start_time: datetime
    metadata: dict[str, Any]


class Session:
    """Execution session wrapper."""

    def __init__(self, goal: str) -> None:
        self.id = str(uuid4())
        self.state: GlobalState = {
            "goal": goal,
            "task_tree": {},
            "execution_log": [],
            "agent_outputs": {},
            "memory_context": [],
            "status": "planning",
            "iteration": 0,
            "start_time": datetime.utcnow(),
            "metadata": {},
        }

    @classmethod
    def create(cls, goal: str) -> "Session":
        return cls(goal)
