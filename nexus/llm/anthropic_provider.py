from __future__ import annotations

from anthropic import AsyncAnthropic

from nexus.llm.base import LLMProvider, Message


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307") -> None:
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model

    async def complete(self, messages: list[Message], **kwargs) -> str:
        prompt = "\n".join(f"{m.role}: {m.content}" for m in messages)
        resp = await self.client.messages.create(model=kwargs.get("model", self.model), max_tokens=kwargs.get("max_tokens", 1024), messages=[{"role": "user", "content": prompt}])
        return resp.content[0].text if resp.content else ""

    async def embed(self, text: str) -> list[float]:
        return [float((i % 10) / 10) for i, _ in enumerate(text[:256])]

    def count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
