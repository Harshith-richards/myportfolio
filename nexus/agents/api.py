from __future__ import annotations

import asyncio
from datetime import datetime

from nexus.agents.base import AgentOutput, BaseAgent, Task


class APIAgent(BaseAgent):
    SYSTEM_PROMPT = "Call external APIs reliably with retries and schema checks."

    async def execute(self, task: Task) -> AgentOutput:
        started = datetime.utcnow()
        payload = task.payload
        retry = 0
        while retry < 3:
            res = await self.tools.execute(
                "api_caller",
                {
                    "url": payload["url"],
                    "method": payload.get("method", "GET"),
                    "headers": payload.get("headers", {}),
                    "body": payload.get("body"),
                    "auth_type": payload.get("auth", {}).get("type", "none") if payload.get("auth") else "none",
                    "timeout": 20,
                },
            )
            if res.success:
                parsed = res.data.get("body")
                return AgentOutput(task_id=task.id, agent=self.name, success=True, output={"status_code": res.data.get("status_code"), "response": res.data.get("body"), "parsed_data": parsed, "error": None}, reasoning_log=["API call succeeded"], started_at=started, finished_at=datetime.utcnow(), attempts=retry + 1)
            if "429" not in (res.error or ""):
                break
            retry += 1
            await asyncio.sleep(2**retry)
        return AgentOutput(task_id=task.id, agent=self.name, success=False, error=res.error if 'res' in locals() else "API call failed", output={"status_code": 0, "response": {}, "parsed_data": None, "error": "failed"}, reasoning_log=["API call failed"], started_at=started, finished_at=datetime.utcnow(), attempts=retry + 1)
