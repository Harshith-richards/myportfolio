"""Tool registry."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

from nexus.tools.base import BaseTool, ToolResult


@dataclass(slots=True)
class ToolManifest:
    name: str
    description: str
    requires_permission: bool
    is_destructive: bool


class ToolRegistry:
    """Central registry for all tools."""

    def __init__(self) -> None:
        self.tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        self.tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        return self.tools[name]

    def list_available(self) -> list[ToolManifest]:
        return [ToolManifest(t.name, t.description, t.requires_permission, t.is_destructive) for t in self.tools.values()]

    async def execute(self, tool_name: str, params: dict[str, Any]) -> ToolResult:
        tool = self.get(tool_name)
        model: BaseModel = tool.input_schema(**params)
        return await tool.run(model)
