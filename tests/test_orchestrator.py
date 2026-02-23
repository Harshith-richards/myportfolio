from __future__ import annotations

import pytest

from nexus.core.config import AgentConfig
from nexus.core.orchestrator import OrchestratorAgent


@pytest.mark.asyncio
async def test_orchestrator_runs() -> None:
    orchestrator = OrchestratorAgent(AgentConfig())
    result = await orchestrator.run("Create a simple summary")
    assert result["status"] in {"done", "failed"}
    assert "outputs" in result
