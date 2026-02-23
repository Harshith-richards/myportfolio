from __future__ import annotations

from fastapi import FastAPI

from nexus.api.routes.agents import router as agent_router
from nexus.api.routes.memory import router as memory_router
from nexus.api.routes.tasks import router as task_router

app = FastAPI(title="NEXUS API", version="1.0.0")
app.include_router(task_router)
app.include_router(memory_router)
app.include_router(agent_router)
