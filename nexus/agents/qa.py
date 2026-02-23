from __future__ import annotations

from datetime import datetime

from nexus.agents.base import AgentOutput, BaseAgent, Task


class QAAgent(BaseAgent):
    SYSTEM_PROMPT = "Evaluate agent output quality, schema and criteria compliance."

    async def execute(self, task: Task) -> AgentOutput:
        started = datetime.utcnow()
        data = task.payload.get("output")
        criteria = task.payload.get("criteria", [])
        issues: list[str] = []
        for criterion in criteria:
            if criterion.lower() not in str(data).lower():
                issues.append(f"Missing criterion: {criterion}")
        score = max(0.0, 1.0 - 0.2 * len(issues))
        out = {"passed": score >= 0.6, "score": score, "issues": issues, "suggestions": ["Add clearer details", "Improve structure"] if issues else []}
        return AgentOutput(task_id=task.id, agent=self.name, success=True, output=out, reasoning_log=["QA evaluated output"], started_at=started, finished_at=datetime.utcnow())
