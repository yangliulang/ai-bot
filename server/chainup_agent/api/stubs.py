from chainup_agent.api.schemas.common import StubBody


def stub(operation_id: str) -> StubBody:
    return StubBody(operation_id=operation_id)
