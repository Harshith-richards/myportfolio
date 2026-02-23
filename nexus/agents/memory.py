from __future__ import annotations

from datetime import datetime

from nexus.agents.base import AgentOutput, BaseAgent, Task
from nexus.memory.long_term import LongTermMemory
from nexus.memory.short_term import ShortTermMemory


class MemoryAgent(BaseAgent):
    SYSTEM_PROMPT = "You manage memory storage and retrieval for NEXUS."

    def __init__(self, tools, llm=None, short_term: ShortTermMemory | None = None, long_term: LongTermMemory | None = None) -> None:
        super().__init__("memory", tools, llm)
        self.short_term = short_term or ShortTermMemory()
        self.long_term = long_term or LongTermMemory()

    async def execute(self, task: Task) -> AgentOutput:
        started = datetime.utcnow()
        action = task.payload.get("action", "retrieve")
        reasoning = [f"Handling memory action={action}"]
        try:
            if action == "store":
                content = str(task.payload.get("content", ""))
                embedding = await self.llm.embed(content) if self.llm else []
                chunk = self.long_term.new_chunk(content, "output", "memory", task.id, embedding=embedding)
                stored_id = self.long_term.store(chunk)
                self.short_term.set(task.id, content)
                output = {"memories": [chunk.model_dump()], "stored_id": stored_id, "relevance_scores": []}
            elif action in {"retrieve", "search"}:
                query = str(task.payload.get("query", ""))
                embedding = await self.llm.embed(query) if (self.llm and query) else []
                results = self.long_term.search(embedding, top_k=int(task.payload.get("top_k", 5))) if embedding else []
                output = {"memories": results, "stored_id": None, "relevance_scores": [1 - r["distance"] for r in results]}
            elif action == "prune":
                removed = self.long_term.prune()
                output = {"memories": [], "stored_id": None, "relevance_scores": [float(removed)]}
            else:
                raise ValueError("Unknown memory action")
            return AgentOutput(task_id=task.id, agent=self.name, success=True, output=output, reasoning_log=reasoning, started_at=started, finished_at=datetime.utcnow())
        except (ValueError, RuntimeError) as exc:
            return AgentOutput(task_id=task.id, agent=self.name, success=False, error=str(exc), reasoning_log=reasoning, started_at=started, finished_at=datetime.utcnow())
