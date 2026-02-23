from __future__ import annotations

import time

import httpx
from pydantic import BaseModel, Field

from nexus.tools.base import BaseTool, ToolResult


class APICallerInput(BaseModel):
    url: str
    method: str = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    body: dict | None = None
    auth_type: str = "none"
    timeout: int = 20


class APICallerTool(BaseTool):
    name = "api_caller"
    description = "Calls REST APIs"
    input_schema = APICallerInput

    async def run(self, params: APICallerInput) -> ToolResult:
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=params.timeout) as client:
                resp = await client.request(params.method.upper(), params.url, headers=params.headers, json=params.body)
            body = None
            try:
                body = resp.json()
            except ValueError:
                body = {"text": resp.text}
            duration = int((time.perf_counter() - started) * 1000)
            return ToolResult(success=resp.is_success, data={"status_code": resp.status_code, "headers": dict(resp.headers), "body": body, "duration_ms": duration})
        except httpx.HTTPError as exc:
            return ToolResult(success=False, error=str(exc))
