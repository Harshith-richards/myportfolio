from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ApprovalRequest:
    action: str
    reason: str
    expected_outcome: str


class HumanApproval:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def check(self, request: ApprovalRequest) -> bool:
        if not self.enabled:
            return True
        return False
