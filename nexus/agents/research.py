from __future__ import annotations

from datetime import datetime

from nexus.agents.base import AgentOutput, BaseAgent, Task


class ResearchAgent(BaseAgent):
    SYSTEM_PROMPT = "Research facts from the web and synthesize outputs with citations."

    async def execute(self, task: Task) -> AgentOutput:
        started = datetime.utcnow()
        reasoning: list[str] = []
        query = task.payload.get("query", task.description)
        depth = int(task.payload.get("depth", 3))
        try:
            search = await self.tools.execute("web_search", {"query": query, "num_results": depth})
            if not search.success:
                raise RuntimeError(search.error or "search failed")
            results = search.data.get("results", [])
            facts: list[str] = []
            sources: list[str] = []
            for item in results:
                sources.append(item["url"])
                facts.append(item["snippet"])
            summary = "\n".join(f"- {f}" for f in facts[:8])
            reasoning.append(f"Collected {len(results)} sources")
            out = {"summary": summary, "sources": sources, "facts": facts, "confidence": min(1.0, 0.5 + len(facts) * 0.05)}
            return AgentOutput(task_id=task.id, agent=self.name, success=True, output=out, reasoning_log=reasoning, started_at=started, finished_at=datetime.utcnow())
        except (RuntimeError, ValueError) as exc:
            return AgentOutput(task_id=task.id, agent=self.name, success=False, error=str(exc), reasoning_log=reasoning, started_at=started, finished_at=datetime.utcnow())
