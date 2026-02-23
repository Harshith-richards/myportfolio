from __future__ import annotations

import pytest

from nexus.api.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_api_task_route() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/tasks", json={"goal": "Summarize AI tools"})
    assert resp.status_code == 200
