from __future__ import annotations

from fastapi import APIRouter

from nexus.core.config import settings
from nexus.core.orchestrator import OrchestratorAgent

router = APIRouter()


@router.get("/agents")
async def list_agents() -> dict:
    orchestrator = OrchestratorAgent(settings)
    return {"agents": orchestrator.registry.list_agents()}


@router.post("/agents/run")
async def run_agent(payload: dict) -> dict:
    orchestrator = OrchestratorAgent(settings)
    goal = payload.get("goal", "demo")
    result = await orchestrator.run(goal)
    return result
