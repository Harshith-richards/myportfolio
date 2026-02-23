"""OpenAI provider implementation."""
from __future__ import annotations

import logging
from typing import Any

from openai import AsyncOpenAI

from nexus.llm.base import LLMProvider, Message

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI-backed LLM provider."""

    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini", embedding_model: str = "text-embedding-3-small") -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.embedding_model = embedding_model

    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        response = await self._client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=[{"role": m.role, "content": m.content} for m in messages],
            temperature=kwargs.get("temperature", 0.2),
        )
        return response.choices[0].message.content or ""

    async def embed(self, text: str) -> list[float]:
        embedding = await self._client.embeddings.create(model=self.embedding_model, input=text)
        return list(embedding.data[0].embedding)

    def count_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)
