from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from nexus.agents.base import AgentOutput, BaseAgent, Task


class DataAgent(BaseAgent):
    SYSTEM_PROMPT = "Analyze tabular datasets and produce statistical reports."

    async def execute(self, task: Task) -> AgentOutput:
        started = datetime.utcnow()
        source = task.payload.get("data_source", "")
        insights: list[str] = []
        stats: dict[str, float] = {}
        try:
            rows = []
            with Path(source).open("r", encoding="utf-8") as handle:
                reader = csv.DictReader(handle)
                rows = list(reader)
            insights.append(f"Loaded {len(rows)} records")
            if rows:
                numeric_cols = [k for k, v in rows[0].items() if (v or "").replace(".", "", 1).isdigit()]
                for col in numeric_cols:
                    values = [float(r[col]) for r in rows if (r[col] or "").replace(".", "", 1).isdigit()]
                    if values:
                        stats[f"{col}_mean"] = sum(values) / len(values)
            report = "\n".join(insights + [f"{k}: {v:.2f}" for k, v in stats.items()])
            return AgentOutput(task_id=task.id, agent=self.name, success=True, output={"insights": insights, "statistics": stats, "charts": [], "report": report}, reasoning_log=["CSV analysis complete"], started_at=started, finished_at=datetime.utcnow())
        except (OSError, ValueError) as exc:
            return AgentOutput(task_id=task.id, agent=self.name, success=False, error=str(exc), reasoning_log=["Data analysis failed"], started_at=started, finished_at=datetime.utcnow())
