"""Base tool abstractions."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Normalized tool result envelope."""

    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    duration_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BaseTool(ABC):
    """Base class for every tool."""

    name: str
    description: str
    input_schema: type[BaseModel]
    output_schema: type[BaseModel] | None = None
    requires_permission: bool = False
    is_destructive: bool = False

    @abstractmethod
    async def run(self, params: BaseModel) -> ToolResult:
        """Execute tool."""
