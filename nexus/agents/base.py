"""Base agent class."""
from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Task(BaseModel):
    """Task descriptor used by orchestrator and agents."""

    id: str
    title: str
    description: str
    agent_type: str
    dependencies: list[str] = Field(default_factory=list)
    parallel: bool = False
    priority: int = 5
    estimated_steps: int = 1
    tools_needed: list[str] = Field(default_factory=list)
    success_criteria: str = ""
    payload: dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    """Standardized agent output envelope."""

    task_id: str
    agent: str
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    reasoning_log: list[str] = Field(default_factory=list)
    error: str | None = None
    started_at: datetime
    finished_at: datetime
    attempts: int = 1


class BaseAgent(ABC):
    """Common base class for all specialized agents."""

    SYSTEM_PROMPT = "You are a specialized autonomous agent."
    max_retries = 3

    def __init__(self, name: str, tools: Any, llm: Any | None = None) -> None:
        self.name = name
        self.tools = tools
        self.llm = llm

    @abstractmethod
    async def execute(self, task: Task) -> AgentOutput:
        """Execute task and return structured output."""

    async def _retry(self, op, *args, **kwargs):
        last_exc: Exception | None = None
        for _ in range(self.max_retries):
            try:
                return await op(*args, **kwargs)
            except (ValueError, RuntimeError, OSError) as exc:
                last_exc = exc
                logger.warning("Retrying %s due to %s", self.name, exc)
                await asyncio.sleep(0.5)
        if last_exc:
            raise last_exc
        raise RuntimeError("Unknown retry failure")
