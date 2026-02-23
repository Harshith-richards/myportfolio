"""Secure file management tool."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from nexus.tools.base import BaseTool, ToolResult


class FileManagerInput(BaseModel):
    """Input schema for file operations."""

    action: str
    path: str
    content: str = ""
    encoding: str = "utf-8"
    target: str | None = None


class FileManagerTool(BaseTool):
    """Read/write/list/move/copy/delete files with path restrictions."""

    name = "file_manager"
    description = "Manage local files securely"
    input_schema = FileManagerInput
    allowed_roots: list[Path]

    def __init__(self, allowed_roots: list[str] | None = None) -> None:
        self.allowed_roots = [Path(p).resolve() for p in (allowed_roots or ["."])]

    def _validate(self, path: str) -> Path:
        resolved = Path(path).resolve()
        if not any(str(resolved).startswith(str(root)) for root in self.allowed_roots):
            raise ValueError(f"Path not allowed: {path}")
        return resolved

    async def run(self, params: FileManagerInput) -> ToolResult:
        try:
            path = self._validate(params.path)
            action = params.action.lower()
            if action == "read":
                data = path.read_text(encoding=params.encoding)
                return ToolResult(success=True, data={"data": data, "metadata": {"path": str(path)}})
            if action in {"write", "append"}:
                path.parent.mkdir(parents=True, exist_ok=True)
                mode = "a" if action == "append" else "w"
                with path.open(mode, encoding=params.encoding) as handle:
                    handle.write(params.content)
                return ToolResult(success=True, data={"metadata": {"path": str(path), "size": path.stat().st_size}})
            if action == "delete":
                path.unlink(missing_ok=False)
                return ToolResult(success=True, data={"metadata": {"path": str(path)}})
            if action == "list":
                files = [str(p) for p in path.iterdir()]
                return ToolResult(success=True, data={"data": files, "metadata": {"path": str(path)}})
            if action == "move":
                if not params.target:
                    raise ValueError("target is required for move")
                target = self._validate(params.target)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(path), str(target))
                return ToolResult(success=True, data={"metadata": {"path": str(target)}})
            if action == "copy":
                if not params.target:
                    raise ValueError("target is required for copy")
                target = self._validate(params.target)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                return ToolResult(success=True, data={"metadata": {"path": str(target)}})
            return ToolResult(success=False, error=f"Unsupported action: {params.action}")
        except (ValueError, OSError) as exc:
            return ToolResult(success=False, error=str(exc))
