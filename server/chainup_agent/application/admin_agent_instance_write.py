"""Admin I02 create · I04 bind/unbind · I05 instanceOverrides."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.admin_access_control import (
    ban_envelope_code,
    fetch_active_ban,
    rollout_whitelist_enforced,
    user_in_rollout_whitelist,
)
from chainup_agent.application.admin_agent_instances import get_agent_instance_joined_admin
from chainup_agent.application.agent_instance import _new_public_instance_id
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.domain.instance_overrides import (
    dumps_instance_overrides,
    parse_instance_overrides_json,
    validate_instance_overrides_patch,
)
from chainup_agent.infrastructure.persistence.models.agent_instance import AgentInstance
_ALLOWED_RUNTIME = frozenset({"RUNNING", "PAUSED", "STOPPED", "ERROR"})


async def assert_i02_create_allowed(
    session: AsyncSession,
    *,
    settings: Settings,
    telegram_user_id: int,
) -> None:
    if settings.agent_runtime_global_disabled:
        raise AppError(
            code="AGENT_GLOBAL_OFF",
            message="全局 Agent 开关已关闭，禁止新建实例。",
            status_code=422,
        )
    if settings.agent_runtime_ops_suspended:
        raise AppError(
            code="AGENT_OPS_SUSPENDED",
            message="运维全局暂停，禁止新建实例。",
            status_code=422,
        )
    ban = await fetch_active_ban(session, user_uid=str(telegram_user_id))
    if ban is not None:
        raise AppError(
            code=ban_envelope_code(ban),
            message="用户处于封禁状态，禁止新建实例。",
            status_code=422,
            details={"reasonCode": ban.reason_code},
        )
    if await rollout_whitelist_enforced(session):
        if not await user_in_rollout_whitelist(session, user_uid=str(telegram_user_id)):
            raise AppError(
                code="AGENT_ROLLOUT_BLOCKED",
                message="灰度白名单未包含该用户，禁止新建实例。",
                status_code=422,
            )


async def create_agent_instance_admin(
    session: AsyncSession,
    *,
    settings: Settings,
    telegram_user_id: int,
    template_id: str | None,
    template_version: str | None,
    exchange_sub_account_user_id: str | None,
) -> AgentInstance:
    await assert_i02_create_allowed(session, settings=settings, telegram_user_id=telegram_user_id)
    stmt = select(AgentInstance).where(AgentInstance.telegram_user_id == telegram_user_id)
    if (await session.execute(stmt)).scalar_one_or_none() is not None:
        raise AppError(
            code="AGENT_QUOTA_EXCEEDED",
            message="该 Telegram 用户已有 Agent 实例。",
            status_code=422,
            details={"telegramUserId": str(telegram_user_id)},
        )
    tid = (template_id or "").strip() or settings.default_agent_template_id.strip() or "tmpl_agent_default"
    tv = (template_version or "").strip() or settings.default_agent_template_version.strip() or "1"
    sub = (exchange_sub_account_user_id or "").strip() or "unassigned"
    now = datetime.now(UTC)
    inst = AgentInstance(
        instance_id=_new_public_instance_id(),
        telegram_user_id=telegram_user_id,
        exchange_sub_account_user_id=sub[:128],
        template_id=tid[:64],
        template_version=tv[:32],
        runtime_state="RUNNING",
        instance_overrides_json="{}",
        created_at=now,
        updated_at=now,
    )
    session.add(inst)
    await session.flush()
    return inst


async def patch_agent_instance_admin(
    session: AsyncSession,
    *,
    instance_public_id: str,
    instance_overrides_patch: dict | None,
    runtime_state: str | None,
) -> AgentInstance:
    pair = await get_agent_instance_joined_admin(session, instance_public_id=instance_public_id)
    if pair is None:
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_NOT_FOUND",
            message="未找到该实例",
            status_code=404,
            details={"instanceId": instance_public_id.strip()[:80]},
        )
    inst, _tb = pair
    if instance_overrides_patch is not None:
        existing = parse_instance_overrides_json(inst.instance_overrides_json)
        merged = validate_instance_overrides_patch(instance_overrides_patch, existing=existing)
        inst.instance_overrides_json = dumps_instance_overrides(merged)
    if runtime_state is not None:
        rs = runtime_state.strip().upper()
        if rs not in _ALLOWED_RUNTIME:
            raise AppError(
                code="VALIDATION_ERROR",
                message="runtimeState 无效",
                status_code=422,
                details={"field": "runtimeState", "allowed": sorted(_ALLOWED_RUNTIME)},
            )
        inst.runtime_state = rs
    inst.updated_at = datetime.now(UTC)
    await session.flush()
    return inst


async def bind_instance_subaccount_admin(
    session: AsyncSession,
    *,
    instance_public_id: str,
    exchange_sub_account_user_id: str,
) -> AgentInstance:
    sub = exchange_sub_account_user_id.strip()
    if not sub:
        raise AppError(
            code="VALIDATION_ERROR",
            message="须提供 exchangeSubAccountUserId 或 subAccountId",
            status_code=422,
            details={"fields": ["exchangeSubAccountUserId", "subAccountId"]},
        )
    pair = await get_agent_instance_joined_admin(session, instance_public_id=instance_public_id)
    if pair is None:
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_NOT_FOUND",
            message="未找到该实例",
            status_code=404,
            details={"instanceId": instance_public_id.strip()[:80]},
        )
    inst, _tb = pair
    inst.exchange_sub_account_user_id = sub[:128]
    inst.updated_at = datetime.now(UTC)
    await session.flush()
    return inst


async def unbind_instance_subaccount_admin(
    session: AsyncSession,
    *,
    instance_public_id: str,
) -> None:
    pair = await get_agent_instance_joined_admin(session, instance_public_id=instance_public_id)
    if pair is None:
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_NOT_FOUND",
            message="未找到该实例",
            status_code=404,
            details={"instanceId": instance_public_id.strip()[:80]},
        )
    inst, tb = pair
    if tb is not None:
        await session.delete(tb)
    inst.updated_at = datetime.now(UTC)
    await session.flush()
