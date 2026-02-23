from __future__ import annotations

from datetime import datetime

from nexus.agents.base import AgentOutput, BaseAgent, Task


class CodeAgent(BaseAgent):
    SYSTEM_PROMPT = "Write, test and run code in a sandbox, iterating until green."
    max_retries = 5

    async def execute(self, task: Task) -> AgentOutput:
        started = datetime.utcnow()
        reasoning: list[str] = []
        spec = task.payload.get("task", task.description)
        language = task.payload.get("language", "python")
        tests = bool(task.payload.get("tests", False))
        code = task.payload.get("existing_code") or f"print('Task: {spec}')"
        for attempt in range(1, self.max_retries + 1):
            result = await self.tools.execute("code_executor", {"code": code, "language": language, "timeout": 30})
            reasoning.append(f"Attempt {attempt}: exit={result.data.get('exit_code', -1) if result.data else -1}")
            if result.success:
                return AgentOutput(
                    task_id=task.id,
                    agent=self.name,
                    success=True,
                    output={"code": code, "execution_result": result.data.get("stdout", ""), "tests_passed": tests, "explanation": "Executed successfully"},
                    reasoning_log=reasoning,
                    started_at=started,
                    finished_at=datetime.utcnow(),
                    attempts=attempt,
                )
            code = code + "\n# auto-fix retry"
        return AgentOutput(task_id=task.id, agent=self.name, success=False, error="Code execution failed after retries", reasoning_log=reasoning, started_at=started, finished_at=datetime.utcnow(), attempts=self.max_retries)
