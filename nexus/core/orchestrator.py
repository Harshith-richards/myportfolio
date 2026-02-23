"""Orchestrator agent and autonomous run loop."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any

from nexus.agents.base import Task
from nexus.agents.registry import AgentRegistry
from nexus.core.config import AgentConfig
from nexus.core.planning import PlanningEngine
from nexus.core.state import Session
from nexus.tools.api_caller import APICallerTool
from nexus.tools.code_executor import CodeExecutorTool
from nexus.tools.email import EmailTool
from nexus.tools.file_manager import FileManagerTool
from nexus.tools.registry import ToolRegistry
from nexus.tools.scheduler import SchedulerTool
from nexus.tools.sql import SQLTool
from nexus.tools.web_scraper import WebScraperTool
from nexus.tools.web_search import WebSearchTool

logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """CEO agent that plans, dispatches, monitors, and replans."""

    def __init__(self, config: AgentConfig, llm=None) -> None:
        self.config = config
        self.tools = ToolRegistry()
        self._register_default_tools(config.allowed_file_roots)
        self.registry = AgentRegistry(self.tools, llm)
        self.planning = PlanningEngine()

    def _register_default_tools(self, roots: list[str]) -> None:
        for tool in [
            WebSearchTool(),
            WebScraperTool(),
            CodeExecutorTool(),
            FileManagerTool(roots),
            SQLTool(),
            APICallerTool(),
            EmailTool(),
            SchedulerTool(),
        ]:
            self.tools.register(tool)

    async def run(self, goal: str) -> dict[str, Any]:
        session = Session.create(goal)
        session.state["status"] = "planning"

        memory_task = Task(id="memory-bootstrap", title="Retrieve memory", description=goal, agent_type="memory", payload={"action": "retrieve", "query": goal})
        memory_context = await self.registry.dispatch(memory_task)
        session.state["memory_context"] = memory_context.output.get("memories", [])

        task_tree = self.planning.decompose(goal, {"memory": session.state["memory_context"]})
        session.state["task_tree"] = task_tree.model_dump()

        session.state["status"] = "executing"
        reflection_agent = self.registry.agents["reflection"]
        qa_agent = self.registry.agents["qa"]

        for iteration in range(self.config.max_iterations):
            session.state["iteration"] = iteration + 1
            ready_tasks = task_tree.get_ready_tasks()
            if not ready_tasks:
                break
            results = await asyncio.gather(*[self.registry.dispatch(task) for task in ready_tasks])
            for task, result in zip(ready_tasks, results):
                if result.success:
                    session.state["agent_outputs"][task.id] = result.output
                    task_tree.mark_complete(task.id, result.output)
                    qa = await qa_agent.execute(Task(id=f"qa-{task.id}", title="QA", description="qa", agent_type="qa", payload={"output": result.output, "criteria": [task.success_criteria]}))
                    if not qa.output.get("passed", False):
                        improved = await reflection_agent.execute(Task(id=f"reflect-{task.id}", title="Reflect", description="improve", agent_type="reflection", payload={"task": task.model_dump(), "output": result.output, "previous_attempts": [], "quality": qa.output.get("score", 0.0)}))
                        if improved.output.get("done"):
                            session.state["agent_outputs"][task.id] = improved.output.get("improved_output", result.output)
                        else:
                            task_tree.mark_failed(task.id, "Reflection could not improve")
                else:
                    task_tree.mark_failed(task.id, result.error or "unknown error")

            if task_tree.is_complete():
                break

            failed_ids = task_tree.get_failed_tasks()
            if failed_ids:
                fail_id = failed_ids[0]
                fail_task = next(t for t in task_tree.tasks if t.id == fail_id)
                new_plan = self.planning.replan(fail_task, task_tree.failed[fail_id], iteration + 1)
                task_tree.merge(new_plan)

        session.state["status"] = "reflecting"
        final_output = reflection_agent.compile_final(session.state)

        store_task = Task(id="memory-store", title="Store final", description="store", agent_type="memory", payload={"action": "store", "content": str(final_output)})
        await self.registry.dispatch(store_task)

        session.state["status"] = "done" if task_tree.is_complete() else "failed"
        final_output["status"] = session.state["status"]
        final_output["completed_at"] = datetime.utcnow().isoformat()
        return final_output
