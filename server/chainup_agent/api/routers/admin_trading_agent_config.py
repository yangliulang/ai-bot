"""Admin — trading-agent GlobalConfigBundle (memory/STM + SESSION keys)."""

from __future__ import annotations

from typing import Annotated

from chainup_agent.api.deps import DbSession, require_admin_console_bearer
from chainup_agent.api.schemas.admin_trading_agent_config import (
    GlobalConfigBundlePatchBody,
    GlobalConfigBundlePatchResponse,
    GlobalConfigBundleResponse,
)
from chainup_agent.application.admin_trading_agent_config import (
    patch_trading_agent_config_bundle,
    read_trading_agent_config_bundle,
)
from fastapi import APIRouter, Depends, Header

router = APIRouter(
    prefix="/api/v1/admin/trading-agent-config",
    tags=["Admin — Trading agent config"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get(
    "/bundle",
    response_model=GlobalConfigBundleResponse,
    response_model_by_alias=True,
    summary="全局 bundle 只读 · configVersion + 生效值",
)
async def get_admin_trading_agent_config_bundle(db: DbSession) -> GlobalConfigBundleResponse:
    data, _ver = await read_trading_agent_config_bundle(db)
    return GlobalConfigBundleResponse.model_validate(data)


@router.patch(
    "/bundle",
    response_model=GlobalConfigBundlePatchResponse,
    response_model_by_alias=True,
    summary="全局 bundle 原子写 · If-Match / expectedConfigVersion",
)
async def patch_admin_trading_agent_config_bundle(
    db: DbSession,
    body: GlobalConfigBundlePatchBody,
    if_match: Annotated[str | None, Header(alias="If-Match")] = None,
) -> GlobalConfigBundlePatchResponse:
    data, _keys = await patch_trading_agent_config_bundle(
        db,
        values=body.values,
        if_match=if_match,
        expected_config_version=body.expected_config_version,
    )
    await db.commit()
    return GlobalConfigBundlePatchResponse.model_validate(data)
