"""Example plugin for NEXUS."""
from __future__ import annotations


class ExampleAgentPlugin:
    name = "example_plugin"
    description = "Demonstrates custom plugin registration"

    async def execute(self, task):
        return {"ok": True, "task": task}
