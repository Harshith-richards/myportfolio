"""Base abstractions for LLM providers."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class Message:
    """Chat message passed to providers."""

    role: str
    content: str


class LLMProvider(ABC):
    """Abstract provider with completion and embedding support."""

    name: str

    @abstractmethod
    async def complete(self, messages: list[Message], **kwargs: Any) -> str:
        """Return a completion string."""

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Return embedding vector for text."""

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Rough token count estimate."""
