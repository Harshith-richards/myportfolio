"""Plugin discovery and registration helpers."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Protocol, runtime_checkable


@runtime_checkable
class AgentPlugin(Protocol):
    name: str
    description: str

    async def execute(self, task): ...


@runtime_checkable
class ToolPlugin(Protocol):
    name: str

    async def run(self, params: dict): ...


def discover_plugins(path: str = "nexus/plugins") -> list[object]:
    plugins: list[object] = []
    for file in Path(path).glob("*.py"):
        if file.name.startswith("__"):
            continue
        spec = importlib.util.spec_from_file_location(file.stem, file)
        if not spec or not spec.loader:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for value in module.__dict__.values():
            if isinstance(value, type) and (hasattr(value, "execute") or hasattr(value, "run")):
                try:
                    plugins.append(value())
                except TypeError:
                    continue
    return plugins
