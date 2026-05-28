from chainup_agent.api.deps import DbSession
from chainup_agent.api.schemas.agent_api_binding import (
    ConfirmAgentApiBindingRequest,
    ConfirmAgentApiBindingResponse,
    ValidateAgentApiKeysRequest,
    ValidateAgentApiKeysResponse,
)
from chainup_agent.api.schemas.agent_onboarding import (
    ApiBindingStatusResponse,
    OnboardingInitiateRequest,
    OnboardingInitiateResponse,
    SubaccountCreateDeferredResponse,
    SubaccountStatusResponse,
)
from chainup_agent.api.schemas.agent_runtime import (
    AccessReasonsResponse,
    EligibilityEnvelope,
    EvaluateEligibilityRequest,
    ExecutionAcceptRequest,
    ExecutionAcceptResponse,
    ExecutionFinalizeRequest,
    ExecutionFinalizeResponse,
    ExecutionStatusResponse,
    IntentRecognizeRequest,
    IntentRecognizeResponse,
    RoutingExecuteRequest,
    RoutingExecuteResponse,
    ScenarioListResponse,
    ScenarioDetailOut,
)
from chainup_agent.application.agent_access_evaluate import (
    evaluate_eligibility,
    static_access_reasons,
)
from chainup_agent.application.agent_api_binding import validate_agent_trading_api_keys_or_raise
from chainup_agent.application.agent_api_binding_confirm import confirm_agent_trading_api_binding
from chainup_agent.application.agent_execution_memory import (
    execution_accept,
    execution_finalize,
    execution_get,
)
from chainup_agent.application.agent_intent_pipeline import recognize_intent_full
from chainup_agent.application.agent_onboarding import (
    api_binding_status_for_user,
    onboarding_initiate as run_onboarding_initiate,
    parse_telegram_user_id_query,
    subaccount_status as fetch_subaccount_status,
)
from chainup_agent.application.agent_routing_execute_http import routing_execute_http_with_execution
from chainup_agent.application.agent_scenario_catalog import (
    ORCHESTRATION_REGISTRY_VERSION,
    AGENT_SCENARIO_CATALOG,
    flow_by_scenario_id,
    scenario_to_detail_dict,
)
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/v1/agent", tags=["Agent — Runtime"])


@router.post(
    "/onboarding/initiate",
    response_model=OnboardingInitiateResponse,
    response_model_by_alias=True,
    summary="开通流程入口（根据是否已托管交易 API 绑定返回下一步）",
)
async def onboarding_initiate(
    db: DbSession,
    body: OnboardingInitiateRequest,
) -> OnboardingInitiateResponse:
    return await run_onboarding_initiate(db, body)


@router.get(
    "/subaccount/status",
    response_model=SubaccountStatusResponse,
    response_model_by_alias=True,
    summary="子账户就绪态（以 trading API 绑定近似；无所内子账户主键）",
)
async def subaccount_status(
    db: DbSession,
    user_id: str = Query(..., alias="userId"),
) -> SubaccountStatusResponse:
    tg = parse_telegram_user_id_query(user_id)
    return await fetch_subaccount_status(db, tg)


@router.post(
    "/subaccount/create",
    response_model=SubaccountCreateDeferredResponse,
    response_model_by_alias=True,
    summary="创建子账户（占位：不自动开立；用户须在 Deeplink 前于主站自备子账户与 API Key）",
)
async def subaccount_create() -> SubaccountCreateDeferredResponse:
    return SubaccountCreateDeferredResponse()


@router.get(
    "/api-binding/status",
    response_model=ApiBindingStatusResponse,
    response_model_by_alias=True,
    summary="交易 API 托管绑定状态（按 Telegram userId 查询）",
)
async def api_binding_status(
    db: DbSession,
    user_id: str = Query(..., alias="userId"),
) -> ApiBindingStatusResponse:
    tg = parse_telegram_user_id_query(user_id)
    return await api_binding_status_for_user(db, tg)


@router.post(
    "/api-binding/confirm",
    response_model=ConfirmAgentApiBindingResponse,
    response_model_by_alias=True,
    summary="确认并托管子账户 API（落库 · validate 已通过后再调）",
)
async def api_binding_confirm(
    body: ConfirmAgentApiBindingRequest,
    db: DbSession,
) -> ConfirmAgentApiBindingResponse:
    """
    再次执行交易所探针后与 **telegram.tg_id** 关联写入 **telegram_agent_trading_binding**；

    Secret 使用 **CHAINUP_AGENT_BINDING_SECRETS_FERNET_KEY** 密封存储。
    同步 upsert **agent_instance**（每 Telegram 用户至多一行）。
    """
    tg_map: dict[str, str] | None = None
    if body.telegram is not None:
        dumped = body.telegram.model_dump(mode="python", exclude_none=True)
        tg_map = {k: str(v) for k, v in dumped.items()} or None
    settings = get_settings()
    row, binding_row_created, instance_id, welcome = await confirm_agent_trading_api_binding(
        session=db,
        settings=settings,
        openapi_base_url=body.openapi_base_url,
        api_key=body.api_key,
        secret_key=body.secret_key,
        sub_account_id=body.sub_account_id,
        telegram=tg_map,
        idempotency_key=None,
        deeplink_token=None,
    )
    sub_echo = (body.sub_account_id or "").strip()
    return ConfirmAgentApiBindingResponse(
        telegram_user_id=row.telegram_user_id,
        instance_id=instance_id,
        exchange_sub_account_user_id=sub_echo,
        binding_row_created=binding_row_created,
        activation_welcome_sent=welcome.sent,
        activation_welcome_skip_reason=welcome.skip_reason,
    )


@router.post(
    "/api-binding/validate",
    response_model=ValidateAgentApiKeysResponse,
    summary="校验子账户交易 API Key（不落库）",
)
async def api_binding_validate(body: ValidateAgentApiKeysRequest) -> ValidateAgentApiKeysResponse:
    """
    **不写库**；用于 Deeplink 开通页「验证密钥」。

    对 ``openapi_base_url`` 做形态校验后，以子账户凭据对 **GET /sapi/v1/account**
    做只读探针；**须**提供 ``sub_account_id``，若响应体含可识别账户 id 字段则须与之匹配。
    """
    await validate_agent_trading_api_keys_or_raise(
        openapi_base_url=body.openapi_base_url,
        api_key=body.api_key,
        secret_key=body.secret_key,
        sub_account_id=body.sub_account_id,
    )
    return ValidateAgentApiKeysResponse()


@router.post(
    "/intent/recognize",
    response_model=IntentRecognizeResponse,
    response_model_by_alias=True,
    summary="意图识别（NLU 草案 + 裁决层：关键词 MVP；结构化 nlu/plan 供 Bot 编排）",
)
async def intent_recognize(
    body: IntentRecognizeRequest,
    db: DbSession,
) -> IntentRecognizeResponse:
    return await recognize_intent_full(
        settings=get_settings(),
        text=body.text,
        session_id=body.session_id,
        execution_id=body.execution_id,
        user_id=body.user_id,
        locale=body.locale,
        previous_scenario_id=body.previous_scenario_id,
        session=db,
    )


@router.get(
    "/scenarios",
    response_model=ScenarioListResponse,
    response_model_by_alias=True,
    summary="场景目录（占位就绪度标注）",
)
async def list_scenarios() -> ScenarioListResponse:
    return ScenarioListResponse(
        scenarios=list(AGENT_SCENARIO_CATALOG),
        orchestration_registry_version=ORCHESTRATION_REGISTRY_VERSION,
    )


@router.get(
    "/scenarios/{scenario_id}",
    response_model=ScenarioDetailOut,
    response_model_by_alias=True,
    summary="场景编排详情（执行流程步骤登记）",
)
async def get_scenario_detail(scenario_id: str) -> ScenarioDetailOut:
    flow = flow_by_scenario_id(scenario_id)
    if flow is None:
        raise AppError(
            code="AGENT_SCENARIO_NOT_FOUND",
            message=f"未登记的场景：{scenario_id.strip()}",
            status_code=404,
        )
    return ScenarioDetailOut.model_validate(scenario_to_detail_dict(flow))


@router.post(
    "/routing/execute",
    response_model=RoutingExecuteResponse,
    response_model_by_alias=True,
    summary="路由执行（只读 wiring + 闪兑 orchestration 指引）",
)
async def routing_execute(body: RoutingExecuteRequest, db: DbSession) -> RoutingExecuteResponse:
    return await routing_execute_http_with_execution(
        session=db,
        settings=get_settings(),
        body=body,
    )


@router.post(
    "/access/evaluate",
    response_model=EligibilityEnvelope,
    response_model_by_alias=True,
    summary="准入评估（DB 绑定 + chat_id 放行）",
)
async def access_evaluate(
    body: EvaluateEligibilityRequest,
    db: DbSession,
) -> EligibilityEnvelope:
    return await evaluate_eligibility(session=db, settings=get_settings(), body=body)


@router.get(
    "/access/reasons",
    response_model=AccessReasonsResponse,
    response_model_by_alias=True,
    summary="门禁阻断码与人类可读摘要（对照 OpenAPI AgentManagement enum）",
)
async def access_reasons() -> AccessReasonsResponse:
    return static_access_reasons()


@router.post(
    "/execution/accept",
    response_model=ExecutionAcceptResponse,
    response_model_by_alias=True,
    summary="接受可计费执行（持久化 ``agent_execution``；幂等与计费钩子后续迭代）",
)
async def exec_accept(body: ExecutionAcceptRequest, db: DbSession) -> ExecutionAcceptResponse:
    out = await execution_accept(db, body, source="http_api")
    await db.commit()
    return out


@router.get(
    "/execution/{execution_id}",
    response_model=ExecutionStatusResponse,
    response_model_by_alias=True,
)
async def exec_get(execution_id: str, db: DbSession) -> ExecutionStatusResponse:
    row = await execution_get(db, execution_id)
    if row is None:
        raise AppError(
            code="EXECUTION_NOT_FOUND",
            message="Unknown execution id.",
            status_code=404,
            details={"executionId": execution_id},
        )
    return row


@router.post(
    "/execution/finalize",
    response_model=ExecutionFinalizeResponse,
    response_model_by_alias=True,
)
async def exec_finalize(body: ExecutionFinalizeRequest, db: DbSession) -> ExecutionFinalizeResponse:
    row = await execution_finalize(db, body)
    if row is None:
        raise AppError(
            code="EXECUTION_NOT_FOUND",
            message="Cannot finalize unknown execution id.",
            status_code=404,
            details={"executionId": body.execution_id},
        )
    await db.commit()
    return row
