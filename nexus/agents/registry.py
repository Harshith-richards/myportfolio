from __future__ import annotations

from typing import Any

from nexus.agents.api import APIAgent
from nexus.agents.base import AgentOutput, BaseAgent, Task
from nexus.agents.code import CodeAgent
from nexus.agents.data import DataAgent
from nexus.agents.file import FileAgent
from nexus.agents.memory import MemoryAgent
from nexus.agents.qa import QAAgent
from nexus.agents.reflection import ReflectionAgent
from nexus.agents.research import ResearchAgent


class AgentRegistry:
    """Maps task types to specific agent instances."""

    def __init__(self, tools, llm=None) -> None:
        self.agents: dict[str, BaseAgent] = {
            "research": ResearchAgent("research", tools, llm),
            "code": CodeAgent("code", tools, llm),
            "file": FileAgent("file", tools, llm),
            "data": DataAgent("data", tools, llm),
            "api": APIAgent("api", tools, llm),
            "qa": QAAgent("qa", tools, llm),
            "reflection": ReflectionAgent("reflection", tools, llm),
            "memory": MemoryAgent(tools, llm),
        }

    async def dispatch(self, task: Task, agent_type: str | None = None) -> AgentOutput:
        kind = agent_type or task.agent_type
        if kind not in self.agents:
            task.agent_type = "code"
            task.payload["task"] = f"Create plugin agent for {kind}: {task.description}"
            return await self.agents["code"].execute(task)
        return await self.agents[kind].execute(task)

    def list_agents(self) -> list[str]:
        return sorted(self.agents.keys())
