from __future__ import annotations

import httpx

from nexus.llm.base import LLMProvider, Message


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3") -> None:
        self.base_url = base_url
        self.model = model

    async def complete(self, messages: list[Message], **kwargs) -> str:
        prompt = "\n".join(m.content for m in messages)
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json={"model": kwargs.get("model", self.model), "prompt": prompt, "stream": False})
            resp.raise_for_status()
            return resp.json().get("response", "")

    async def embed(self, text: str) -> list[float]:
        return [float((i % 7) / 7) for i, _ in enumerate(text[:256])]

    def count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
