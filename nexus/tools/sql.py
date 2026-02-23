from __future__ import annotations

import sqlite3

from pydantic import BaseModel, Field

from nexus.tools.base import BaseTool, ToolResult


class SQLInput(BaseModel):
    query: str
    db_path: str
    params: list = Field(default_factory=list)
    read_only: bool = True


class SQLTool(BaseTool):
    name = "sql_connector"
    description = "SQLite query tool"
    input_schema = SQLInput

    async def run(self, params: SQLInput) -> ToolResult:
        try:
            lowered = params.query.strip().lower()
            if params.read_only and not lowered.startswith("select"):
                return ToolResult(success=False, error="Read-only mode enabled")
            con = sqlite3.connect(params.db_path)
            con.row_factory = sqlite3.Row
            cur = con.cursor()
            cur.execute(params.query, params.params)
            rows = [dict(r) for r in cur.fetchall()] if lowered.startswith("select") else []
            affected = cur.rowcount if cur.rowcount != -1 else 0
            columns = [d[0] for d in cur.description] if cur.description else []
            con.commit()
            con.close()
            return ToolResult(success=True, data={"rows": rows, "affected_rows": affected, "columns": columns})
        except sqlite3.Error as exc:
            return ToolResult(success=False, error=str(exc))
