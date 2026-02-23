from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel

from nexus.tools.base import BaseTool, ToolResult

scheduler = BackgroundScheduler()
scheduler.start()


class SchedulerInput(BaseModel):
    task_description: str
    schedule_type: str = "date"
    cron_expr: str = ""
    run_at: datetime | None = None


class SchedulerTool(BaseTool):
    name = "scheduler"
    description = "Schedules background jobs"
    input_schema = SchedulerInput

    async def run(self, params: SchedulerInput) -> ToolResult:
        job_id = str(uuid4())
        run_at = params.run_at or datetime.utcnow()
        scheduler.add_job(lambda: None, "date", id=job_id, run_date=run_at)
        return ToolResult(success=True, data={"job_id": job_id, "next_run": run_at.isoformat()})
