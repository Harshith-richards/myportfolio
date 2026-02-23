"""Long-term vector memory built on ChromaDB."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any
from uuid import uuid4

import chromadb
from pydantic import BaseModel, Field


class MemoryChunk(BaseModel):
    id: str
    content: str
    embedding: list[float] = Field(default_factory=list)
    memory_type: str
    source_agent: str
    task_id: str
    relevance_score: float = 0.0
    created_at: datetime
    tags: list[str] = Field(default_factory=list)
    compressed: bool = False


class LongTermMemory:
    """Persistent semantic store for agent memories."""

    def __init__(self, path: str = ".nexus/chroma") -> None:
        self.client = chromadb.PersistentClient(path=path)
        self.collections = {
            name: self.client.get_or_create_collection(name=name) for name in ["tasks", "lessons", "preferences", "outputs", "episodic"]
        }

    def store(self, chunk: MemoryChunk) -> str:
        coll = self.collections[chunk.memory_type if chunk.memory_type in self.collections else "outputs"]
        coll.add(
            ids=[chunk.id],
            documents=[chunk.content],
            embeddings=[chunk.embedding] if chunk.embedding else None,
            metadatas=[{
                "source_agent": chunk.source_agent,
                "task_id": chunk.task_id,
                "created_at": chunk.created_at.isoformat(),
                "tags": ",".join(chunk.tags),
                "compressed": chunk.compressed,
            }],
        )
        return chunk.id

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[dict[str, Any]]:
        coll = self.collections["outputs"]
        res = coll.query(query_embeddings=[query_embedding], n_results=top_k)
        out: list[dict[str, Any]] = []
        for i, doc in enumerate(res.get("documents", [[]])[0]):
            out.append({"content": doc, "metadata": res["metadatas"][0][i], "distance": res["distances"][0][i]})
        return out

    def summarize_old(self) -> int:
        cutoff = datetime.utcnow() - timedelta(days=7)
        updated = 0
        for coll in self.collections.values():
            items = coll.get(include=["documents", "metadatas"])
            ids: list[str] = []
            docs: list[str] = []
            metas: list[dict[str, Any]] = []
            for i, md in enumerate(items.get("metadatas", [])):
                if datetime.fromisoformat(md["created_at"]) < cutoff and not md.get("compressed", False):
                    ids.append(items["ids"][i])
                    docs.append((items["documents"][i][:400] + " ...") if len(items["documents"][i]) > 400 else items["documents"][i])
                    md["compressed"] = True
                    metas.append(md)
            if ids:
                coll.update(ids=ids, documents=docs, metadatas=metas)
                updated += len(ids)
        return updated

    def prune(self, max_entries: int = 10000) -> int:
        coll = self.collections["outputs"]
        items = coll.get(include=[])
        total = len(items.get("ids", []))
        if total <= max_entries:
            return 0
        to_remove = items["ids"][: total - max_entries]
        coll.delete(ids=to_remove)
        return len(to_remove)

    @staticmethod
    def new_chunk(content: str, memory_type: str, source_agent: str, task_id: str, embedding: list[float] | None = None, tags: list[str] | None = None) -> MemoryChunk:
        return MemoryChunk(
            id=str(uuid4()),
            content=content,
            embedding=embedding or [],
            memory_type=memory_type,
            source_agent=source_agent,
            task_id=task_id,
            created_at=datetime.utcnow(),
            tags=tags or [],
        )
