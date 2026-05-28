"""Admin API — Agent instances (I01/I02/I03/I04/I05/I06)."""

from __future__ import annotations

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.admin_agent_instance_write import (
    AdminAgentInstanceCreatedResponse,
    AdminBindInstanceSubaccountRequest,
    AdminCreateAgentInstanceRequest,
    AdminPatchAgentInstanceRequest,
)
from chainup_agent.api.schemas.admin_agent_instances import (
    AdminAgentInstanceItem,
    AdminAgentInstanceListResponse,
    admin_agent_instance_item_from_rows,
)
from chainup_agent.application.admin_agent_instance_write import (
    bind_instance_subaccount_admin,
    create_agent_instance_admin,
    patch_agent_instance_admin,
    unbind_instance_subaccount_admin,
)
from chainup_agent.application.admin_agent_instances import (
    count_agent_instances_admin,
    delete_agent_instance_admin,
    get_agent_instance_joined_admin,
    list_agent_instances_joined_admin,
)
from chainup_agent.core.config import get_settings
from chainup_agent.core.errors import AppError
from fastapi import APIRouter, Depends, Query, Response, status

router = APIRouter(
    prefix="/api/v1/admin/agents",
    tags=["Admin — Agent instances"],
    dependencies=[Depends(require_admin_console_bearer)],
)


def _optional_telegram_user_id_filter(raw: str | None) -> int | None:
    if raw is None or not str(raw).strip():
        return None
    t = str(raw).strip()
    try:
        return int(t)
    except ValueError as e:
        raise AppError(
            code="VALIDATION_ERROR",
            message="telegramUserId 须为数值字符串",
            status_code=422,
            details={"field": "telegramUserId", "value": t[:32]},
        ) from e


@router.post(
    "/instances",
    response_model=AdminAgentInstanceCreatedResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="创建实例 I02（门禁：G01/封禁/灰度；每 tg 用户一行）",
)
async def create_admin_agent_instance(
    db: DbSession,
    body: AdminCreateAgentInstanceRequest,
) -> AdminAgentInstanceCreatedResponse:
    tg_raw = body.telegram_user_id.strip()
    try:
        tg = int(tg_raw)
    except ValueError as e:
        raise AppError(
            code="VALIDATION_ERROR",
            message="telegramUserId 须为数值字符串",
            status_code=422,
            details={"field": "telegramUserId"},
        ) from e
    settings = get_settings()
    inst = await create_agent_instance_admin(
        db,
        settings=settings,
        telegram_user_id=tg,
        template_id=body.template_id,
        template_version=body.template_version,
        exchange_sub_account_user_id=body.exchange_sub_account_user_id,
    )
    await db.commit()
    return AdminAgentInstanceCreatedResponse(
        instance_id=inst.instance_id,
        user_id=str(inst.telegram_user_id),
        template_id=inst.template_id,
        runtime_instance_state=inst.runtime_state,
        agent_sub_account_id=inst.exchange_sub_account_user_id or None,
    )


@router.get(
    "/instances",
    response_model=AdminAgentInstanceListResponse,
    response_model_by_alias=True,
    summary="实例列表 I01（读 agent_instance + 可选绑定摘要）",
)
async def list_admin_agent_instances(
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    instance_id: str | None = Query(default=None, alias="instanceId"),
    telegram_user_id: str | None = Query(default=None, alias="telegramUserId"),
) -> AdminAgentInstanceListResponse:
    tg_filter = _optional_telegram_user_id_filter(telegram_user_id)
    filt_inst = instance_id.strip() if instance_id and instance_id.strip() else None
    total = await count_agent_instances_admin(
        db,
        filter_instance_id=filt_inst,
        filter_telegram_user_id=tg_filter,
    )
    pairs = await list_agent_instances_joined_admin(
        db,
        limit=limit,
        offset=offset,
        filter_instance_id=filt_inst,
        filter_telegram_user_id=tg_filter,
    )
    items = [
        admin_agent_instance_item_from_rows(
            instance_row=ai, binding_row=tb, settings=get_settings()
        )
        for ai, tb in pairs
    ]
    return AdminAgentInstanceListResponse(items=items, total=total)


@router.get(
    "/instances/{instance_id}",
    response_model=AdminAgentInstanceItem,
    response_model_by_alias=True,
    summary="实例详情 I03",
)
async def get_admin_agent_instance(
    instance_id: str,
    db: DbSession,
) -> AdminAgentInstanceItem:
    pair = await get_agent_instance_joined_admin(db, instance_public_id=instance_id)
    if pair is None:
        raise AppError(
            code="AGENT_ADMIN_INSTANCE_NOT_FOUND",
            message="未找到该实例",
            status_code=404,
            details={"instanceId": instance_id.strip()[:80]},
        )
    ai, tb = pair
    return admin_agent_instance_item_from_rows(
        instance_row=ai, binding_row=tb, settings=get_settings()
    )


@router.patch(
    "/instances/{instance_id}",
    response_model=AdminAgentInstanceItem,
    response_model_by_alias=True,
    summary="实例更新 I05（instanceOverrides 白名单 · 可选 runtimeState）",
)
async def patch_admin_agent_instance(
    instance_id: str,
    db: DbSession,
    body: AdminPatchAgentInstanceRequest,
) -> AdminAgentInstanceItem:
    inst = await patch_agent_instance_admin(
        db,
        instance_public_id=instance_id,
        instance_overrides_patch=body.instance_overrides,
        runtime_state=body.runtime_state,
    )
    await db.commit()
    pair = await get_agent_instance_joined_admin(db, instance_public_id=inst.instance_id)
    assert pair is not None
    ai, tb = pair
    return admin_agent_instance_item_from_rows(
        instance_row=ai, binding_row=tb, settings=get_settings()
    )


@router.post(
    "/instances/{instance_id}/binding",
    response_model=AdminAgentInstanceItem,
    response_model_by_alias=True,
    summary="子账户绑定 I04 · 登记 exchangeSubAccountUserId（API 密钥仍走 Deeplink）",
)
async def bind_admin_agent_instance_subaccount(
    instance_id: str,
    db: DbSession,
    body: AdminBindInstanceSubaccountRequest,
) -> AdminAgentInstanceItem:
    sub = (body.exchange_sub_account_user_id or body.sub_account_id or "").strip()
    inst = await bind_instance_subaccount_admin(
        db,
        instance_public_id=instance_id,
        exchange_sub_account_user_id=sub,
    )
    await db.commit()
    pair = await get_agent_instance_joined_admin(db, instance_public_id=inst.instance_id)
    assert pair is not None
    ai, tb = pair
    return admin_agent_instance_item_from_rows(
        instance_row=ai, binding_row=tb, settings=get_settings()
    )


@router.delete(
    "/instances/{instance_id}/binding",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="解绑 I04 · 删除 telegram_agent_trading_binding（保留 agent_instance）",
)
async def unbind_admin_agent_instance_subaccount(
    instance_id: str,
    db: DbSession,
) -> Response:
    await unbind_instance_subaccount_admin(db, instance_public_id=instance_id)
    await db.commit()
    return Response(status_code=204)


@router.delete(
    "/instances/{instance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除实例 I06（硬删 agent_instance + 解绑 trading API 托管行）",
)
async def delete_admin_agent_instance(
    instance_id: str,
    db: DbSession,
) -> Response:
    await delete_agent_instance_admin(db, instance_public_id=instance_id)
    await db.commit()
    return Response(status_code=204)
