from __future__ import annotations

from fastapi import APIRouter

from nexus.api.schemas import TaskRequest, TaskResponse
from nexus.core.config import settings
from nexus.core.orchestrator import OrchestratorAgent

router = APIRouter()


@router.post("/tasks", response_model=TaskResponse)
async def create_task(req: TaskRequest) -> TaskResponse:
    orchestrator = OrchestratorAgent(settings)
    out = await orchestrator.run(req.goal)
    return TaskResponse(session_id="local-session", status=out["status"], output=out)
