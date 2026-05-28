"""Admin API — list/delete Telegram trading API bindings (operational, no secrets in responses)."""

from __future__ import annotations

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.admin_trading_bindings import (
    AdminTradingBindingListItem,
    AdminTradingBindingListResponse,
    mask_optional_tail,
)
from chainup_agent.infrastructure.persistence.models.telegram_agent_trading_binding import (
    TelegramAgentTradingBinding,
)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import delete, func, select

router = APIRouter(
    prefix="/api/v1/admin/agent",
    tags=["Admin — Agent bindings"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get(
    "/trading-bindings",
    response_model=AdminTradingBindingListResponse,
    response_model_by_alias=True,
    summary="列出已落库的 Telegram 交易 API 绑定（无密钥列）",
)
async def get_admin_trading_bindings(
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> AdminTradingBindingListResponse:
    row = await db.execute(select(func.count()).select_from(TelegramAgentTradingBinding))
    total = int(row.scalar_one())
    result = await db.execute(
        select(TelegramAgentTradingBinding)
        .order_by(TelegramAgentTradingBinding.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = result.scalars().all()
    items = [
        AdminTradingBindingListItem(
            id=r.id,
            telegram_user_id=r.telegram_user_id,
            tg_username=r.tg_username,
            tg_first_name=r.tg_first_name,
            tg_last_name=r.tg_last_name,
            tg_lang=r.tg_lang,
            openapi_base_url=r.openapi_base_url,
            idempotency_key_last_masked=mask_optional_tail(r.idempotency_key_last),
            deeplink_token_last_masked=mask_optional_tail(r.deeplink_token_last),
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in rows
    ]
    return AdminTradingBindingListResponse(items=items, total=total)


@router.delete(
    "/trading-bindings/{binding_id}",
    status_code=204,
    summary="按主键删除一条 Telegram 交易绑定（运营解绑；删整行含密封密钥列）",
)
async def delete_admin_trading_binding(binding_id: int, db: DbSession) -> None:
    result = await db.execute(
        delete(TelegramAgentTradingBinding).where(TelegramAgentTradingBinding.id == binding_id),
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="未找到绑定记录")
