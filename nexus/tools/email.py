from __future__ import annotations

import uuid

from pydantic import BaseModel, Field

from nexus.tools.base import BaseTool, ToolResult


class EmailInput(BaseModel):
    to: list[str]
    subject: str
    body: str
    attachments: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)
    is_bulk: bool = False


class EmailTool(BaseTool):
    name = "email_sender"
    description = "Email sender stub for SMTP integrations"
    input_schema = EmailInput
    requires_permission = True

    async def run(self, params: EmailInput) -> ToolResult:
        if params.is_bulk:
            return ToolResult(success=False, error="Bulk email requires human approval")
        return ToolResult(success=True, data={"sent": True, "message_id": str(uuid.uuid4())})
