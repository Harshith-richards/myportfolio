from __future__ import annotations

import asyncio

from nexus.core.config import settings
from nexus.core.orchestrator import OrchestratorAgent


async def main() -> None:
    orchestrator = OrchestratorAgent(settings)
    goals = [
        "Create a market research report on electric vehicles in India and build a PowerPoint presentation with charts.",
        "Build a working todo list web app with Python backend, save it to files, and run it.",
        "Research the top 5 AI coding assistants, compare features and pricing, and recommend the best one for a startup.",
    ]
    for goal in goals:
        output = await orchestrator.run(goal)
        print(goal)
        print(output["status"])


if __name__ == "__main__":
    asyncio.run(main())
