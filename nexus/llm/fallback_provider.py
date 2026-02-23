from __future__ import annotations

from nexus.llm.base import LLMProvider, Message


class FallbackProvider(LLMProvider):
    name = "fallback"

    def __init__(self, providers: list[LLMProvider]) -> None:
        self.providers = providers

    async def complete(self, messages: list[Message], **kwargs) -> str:
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                return await provider.complete(messages, **kwargs)
            except Exception as exc:  # intentional fallback boundary
                last_error = exc
        raise RuntimeError(f"All providers failed: {last_error}")

    async def embed(self, text: str) -> list[float]:
        for provider in self.providers:
            try:
                return await provider.embed(text)
            except Exception:
                continue
        return [0.0] * 16

    def count_tokens(self, text: str) -> int:
        if not self.providers:
            return max(1, len(text) // 4)
        return self.providers[0].count_tokens(text)
