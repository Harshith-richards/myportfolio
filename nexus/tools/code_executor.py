from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

from pydantic import BaseModel

from nexus.tools.base import BaseTool, ToolResult


class CodeExecInput(BaseModel):
    code: str
    language: str = "python"
    timeout: int = 30


class CodeExecutorTool(BaseTool):
    name = "code_executor"
    description = "Executes code via local subprocess (lightweight sandbox mode)."
    input_schema = CodeExecInput
    requires_permission = True

    async def run(self, params: CodeExecInput) -> ToolResult:
        suffix = {"python": ".py", "javascript": ".js", "bash": ".sh", "sql": ".sql"}.get(params.language.lower())
        if not suffix:
            return ToolResult(success=False, error="Unsupported language")
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / f"main{suffix}"
            code_file.write_text(params.code, encoding="utf-8")
            cmd = {
                "python": ["python", str(code_file)],
                "javascript": ["node", str(code_file)],
                "bash": ["bash", str(code_file)],
                "sql": ["sqlite3", ":memory:", f".read {code_file}"],
            }[params.language.lower()]
            try:
                proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                out, err = await asyncio.wait_for(proc.communicate(), timeout=params.timeout)
                return ToolResult(
                    success=proc.returncode == 0,
                    data={"stdout": out.decode(), "stderr": err.decode(), "exit_code": proc.returncode, "files_created": []},
                    error=None if proc.returncode == 0 else err.decode(),
                )
            except TimeoutError:
                return ToolResult(success=False, error="Execution timed out")
