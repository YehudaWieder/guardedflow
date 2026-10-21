"""A fake ApprovalHandler — returns a scripted decision instead of pausing
the run for a human."""

from flowpermit.approval import ApprovalDecision, ApprovalRequest


class FakeApprovalHandler:
    def __init__(self, decision: ApprovalDecision | None = None) -> None:
        self.decision = decision or ApprovalDecision(approved=True)
        self.requests: list[ApprovalRequest] = []

    async def request(self, request: ApprovalRequest) -> ApprovalDecision:
        self.requests.append(request)
        return self.decision
