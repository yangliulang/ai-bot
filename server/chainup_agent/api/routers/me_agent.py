"""Product-facing user paths under `/api/v1/me/agent/*` (aliases agent onboarding)."""

from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.agent_api_binding import (
    MeAgentTradingApiBindingRequest,
    MeAgentTradingApiBindingResponse,
)
from chainup_agent.application.agent_api_binding_confirm import confirm_agent_trading_api_binding
from chainup_agent.core.config import get_settings
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/me/agent", tags=["User — Agent onboarding"])


@router.post(
    "/bindings/trading-api",
    response_model=MeAgentTradingApiBindingResponse,
    response_model_by_alias=True,
    summary="保存子账户交易 API 绑定（与 Deeplink camelCase Body 对齐）",
)
async def post_me_trading_api_binding(
    body: MeAgentTradingApiBindingRequest,
    db: DbSession,
) -> MeAgentTradingApiBindingResponse:
    """
    产品与 ``deeplink`` **POST trading-api**。

    须含 openapiBaseUrl（与 validate 同口径）、**subAccountId** 及 ``telegram`` 含 ``tg_id``。
    内部等价 POST ``/api/v1/agent/api-binding/confirm``（再次交易所探针）；
    并 upsert **agent_instance**。
    """
    tg = body.telegram.model_dump(mode="python", exclude_none=True) if body.telegram else None
    tg_map = {k: str(v) for k, v in (tg or {}).items()} or None

    settings = get_settings()
    row, binding_row_created, instance_id, welcome = await confirm_agent_trading_api_binding(
        session=db,
        settings=settings,
        openapi_base_url=body.openapi_base_url,
        api_key=body.api_key,
        secret_key=body.secret_key,
        sub_account_id=body.sub_account_id,
        telegram=tg_map,
        idempotency_key=body.idempotency_key,
        deeplink_token=body.deeplink_token,
    )
    sub_echo = (body.sub_account_id or "").strip()
    return MeAgentTradingApiBindingResponse(
        saved=True,
        agent_trading_api_binding_status="BOUND",
        binding_row_created=binding_row_created,
        instance_id=instance_id,
        exchange_sub_account_user_id=sub_echo,
        activation_welcome_sent=welcome.sent,
        activation_welcome_skip_reason=welcome.skip_reason,
    )
