from __future__ import annotations

import pytest

from nexus.agents.base import Task
from nexus.agents.registry import AgentRegistry
from nexus.tools.file_manager import FileManagerTool
from nexus.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_research_agent_executes() -> None:
    tools = ToolRegistry()
    tools.register(FileManagerTool(["."]))
    registry = AgentRegistry(tools)
    task = Task(id="1", title="research", description="python", agent_type="research", payload={"query": "python programming", "depth": 1})
    out = await registry.dispatch(task)
    assert out.agent == "research"
