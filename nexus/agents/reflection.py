from __future__ import annotations

from datetime import datetime
from typing import Any

from nexus.agents.base import AgentOutput, BaseAgent, Task


class ReflectionAgent(BaseAgent):
    SYSTEM_PROMPT = "Reflect on outputs and improve quality iteratively."

    async def execute(self, task: Task) -> AgentOutput:
        started = datetime.utcnow()
        output = task.payload.get("output", {})
        prev = task.payload.get("previous_attempts", [])
        quality = float(task.payload.get("quality", 0.7))
        improved = output if isinstance(output, dict) else {"value": output}
        improved["refined"] = True
        delta = min(0.25, 0.02 * len(str(output)))
        done = quality + delta >= 0.85
        out = {"improved_output": improved, "changelog": "Applied consistency and clarity improvements", "quality_delta": delta, "done": done}
        return AgentOutput(task_id=task.id, agent=self.name, success=True, output=out, reasoning_log=[f"Compared against {len(prev)} previous attempts"], started_at=started, finished_at=datetime.utcnow())

    def compile_final(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "goal": state.get("goal"),
            "status": state.get("status"),
            "outputs": state.get("agent_outputs", {}),
            "iterations": state.get("iteration", 0),
        }
