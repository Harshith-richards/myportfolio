"""Memory compression utilities."""
from __future__ import annotations


def compress_text(text: str, max_chars: int = 500) -> str:
    """Naive compressor used when no summarizer model is configured."""

    return text if len(text) <= max_chars else text[:max_chars] + " ..."
