from __future__ import annotations

import re

import httpx
from pydantic import BaseModel

from nexus.tools.base import BaseTool, ToolResult


class WebScraperInput(BaseModel):
    url: str
    extract: str = "text"
    screenshot: bool = False


class WebScraperTool(BaseTool):
    name = "web_scrape"
    description = "Simple HTTP scraper"
    input_schema = WebScraperInput

    async def run(self, params: WebScraperInput) -> ToolResult:
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(params.url)
            html = response.text
            text = re.sub(r"<[^>]+>", " ", html)
            links = re.findall(r'href=["\'](.*?)["\']', html)
            return ToolResult(success=True, data={"html": html, "text": text[:5000], "links": links[:100], "screenshot_path": ""})
        except httpx.HTTPError as exc:
            return ToolResult(success=False, error=str(exc))
