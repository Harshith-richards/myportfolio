from __future__ import annotations

from datetime import datetime

from nexus.agents.base import AgentOutput, BaseAgent, Task


class FileAgent(BaseAgent):
    SYSTEM_PROMPT = "Perform secure file operations and format conversion."

    async def execute(self, task: Task) -> AgentOutput:
        started = datetime.utcnow()
        p = task.payload
        try:
            res = await self.tools.execute(
                "file_manager",
                {
                    "action": p.get("action", "read"),
                    "path": p.get("path", "."),
                    "content": p.get("content", ""),
                    "encoding": "utf-8",
                    "target": p.get("target"),
                },
            )
            out = {"success": res.success, "path": p.get("path"), "content": res.data.get("data") if res.data else None, "metadata": res.data.get("metadata", {}) if res.data else {}}
            return AgentOutput(task_id=task.id, agent=self.name, success=res.success, output=out, error=res.error, reasoning_log=["File operation executed"], started_at=started, finished_at=datetime.utcnow())
        except (ValueError, RuntimeError) as exc:
            return AgentOutput(task_id=task.id, agent=self.name, success=False, error=str(exc), reasoning_log=["File operation failed"], started_at=started, finished_at=datetime.utcnow())
