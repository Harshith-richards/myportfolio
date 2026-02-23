from __future__ import annotations

from enum import IntEnum


class PermissionLevel(IntEnum):
    READ_ONLY = 1
    STANDARD = 2
    ELEVATED = 3
    ADMIN = 4


def can_execute(user_level: PermissionLevel, required_level: PermissionLevel) -> bool:
    return user_level >= required_level
