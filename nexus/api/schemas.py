from __future__ import annotations

from pydantic import BaseModel, Field


class TaskRequest(BaseModel):
    goal: str = Field(min_length=3)


class TaskResponse(BaseModel):
    session_id: str
    status: str
    output: dict
