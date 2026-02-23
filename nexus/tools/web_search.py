from __future__ import annotations

import time
from collections import deque

import duckduckgo_search
from pydantic import BaseModel

from nexus.tools.base import BaseTool, ToolResult


class WebSearchInput(BaseModel):
    query: str
    num_results: int = 5
    search_type: str = "text"


class WebSearchTool(BaseTool):
    name = "web_search"
    description = "DuckDuckGo web search with lightweight rate limit"
    input_schema = WebSearchInput

    def __init__(self) -> None:
        self._calls: deque[float] = deque(maxlen=20)

    async def run(self, params: WebSearchInput) -> ToolResult:
        now = time.time()
        while self._calls and now - self._calls[0] > 60:
            self._calls.popleft()
        if len(self._calls) >= 10:
            return ToolResult(success=False, error="Rate limit exceeded")
        self._calls.append(now)
        try:
            with duckduckgo_search.DDGS() as ddgs:
                raw = list(ddgs.text(params.query, max_results=params.num_results))
            results = [{"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")} for r in raw]
            return ToolResult(success=True, data={"results": results})
        except (RuntimeError, ValueError) as exc:
            return ToolResult(success=False, error=str(exc))
