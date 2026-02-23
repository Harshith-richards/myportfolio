from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/memory")
async def list_memory() -> dict:
    return {"items": []}


@router.delete("/memory")
async def clear_memory() -> dict:
    return {"cleared": True}
