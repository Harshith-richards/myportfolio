from __future__ import annotations

import pytest

from nexus.tools.file_manager import FileManagerTool


@pytest.mark.asyncio
async def test_file_manager_write_read(tmp_path) -> None:
    tool = FileManagerTool([str(tmp_path)])
    p = tmp_path / "a.txt"
    res_w = await tool.run(tool.input_schema(action="write", path=str(p), content="hello"))
    assert res_w.success
    res_r = await tool.run(tool.input_schema(action="read", path=str(p)))
    assert res_r.data["data"] == "hello"
