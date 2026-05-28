"""Admin Access Control API — `product-doc/specs/openapi/admin/access-control.yaml` subset."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from chainup_agent.api.deps import DbSession, require_admin_console_bearer, require_admin_console_user
from chainup_agent.api.schemas.admin_access_control import (
    AccessControlKycMirrorStub,
    BanCreateRequest,
    BanItem,
    BanListResponse,
    MinVipTierPatchRequest,
    MinVipTierResponse,
    RolloutPolicyPatchRequest,
    RolloutPolicyResponse,
    WhitelistCreateRequest,
    WhitelistEntryItem,
    WhitelistListResponse,
)
from chainup_agent.application.admin_access_control import (
    create_ban,
    create_whitelist_entry,
    delete_ban,
    delete_whitelist_entry,
    get_min_vip,
    get_rollout_policy,
    list_bans,
    list_whitelist,
    patch_min_vip,
    patch_rollout_policy,
)
from chainup_agent.core.errors import AppError

router = APIRouter(
    prefix="/api/v1/admin/access-control",
    tags=["Admin — Access control"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get("/whitelist", response_model=WhitelistListResponse, response_model_by_alias=True)
async def get_whitelist(
    db: DbSession,
    list_id: str | None = Query(None, alias="listId"),
    q: str | None = Query(None, description="Client-side style filter (optional)"),
) -> WhitelistListResponse:
    return await list_whitelist(db, list_id=list_id, q=q)


@router.post(
    "/whitelist",
    response_model=WhitelistEntryItem,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
async def post_whitelist(
    db: DbSession,
    body: WhitelistCreateRequest,
    actor: Annotated[str, Depends(require_admin_console_user)],
) -> WhitelistEntryItem:
    item = await create_whitelist_entry(db, body, actor=actor)
    await db.commit()
    return item


@router.delete("/whitelist/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_whitelist(entry_id: str, db: DbSession) -> None:
    await delete_whitelist_entry(db, entry_id)
    await db.commit()


@router.get("/bans", response_model=BanListResponse, response_model_by_alias=True)
async def get_bans(
    db: DbSession,
    q: str | None = None,
) -> BanListResponse:
    return await list_bans(db, q=q)


@router.post(
    "/bans",
    response_model=BanItem,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
async def post_ban(
    db: DbSession,
    body: BanCreateRequest,
    actor: Annotated[str, Depends(require_admin_console_user)],
) -> BanItem:
    item = await create_ban(db, body, actor=actor)
    await db.commit()
    return item


@router.delete("/bans/{ban_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_ban(ban_id: str, db: DbSession) -> None:
    await delete_ban(db, ban_id)
    await db.commit()


@router.get(
    "/membership/min-vip-tier",
    response_model=MinVipTierResponse,
    response_model_by_alias=True,
)
async def get_min_vip_tier(db: DbSession) -> MinVipTierResponse:
    return await get_min_vip(db)


@router.patch(
    "/membership/min-vip-tier",
    response_model=MinVipTierResponse,
    response_model_by_alias=True,
)
async def patch_min_vip_tier(
    db: DbSession,
    body: MinVipTierPatchRequest,
) -> MinVipTierResponse:
    out = await patch_min_vip(db, body.min_vip_tier)
    await db.commit()
    return out


@router.get("/rollout", response_model=RolloutPolicyResponse, response_model_by_alias=True)
async def get_rollout(db: DbSession) -> RolloutPolicyResponse:
    return await get_rollout_policy(db)


@router.patch("/rollout", response_model=RolloutPolicyResponse, response_model_by_alias=True)
async def patch_rollout(
    db: DbSession,
    body: RolloutPolicyPatchRequest,
) -> RolloutPolicyResponse:
    if body.rollout_whitelist_enforced is None:
        raise AppError(
            code="VALIDATION_ERROR",
            message="Body 须包含 rolloutWhitelistEnforced。",
            status_code=422,
        )
    out = await patch_rollout_policy(db, body.rollout_whitelist_enforced)
    await db.commit()
    return out


@router.get(
    "/users/{user_id}/kyc-mirror",
    response_model=AccessControlKycMirrorStub,
    response_model_by_alias=True,
)
async def get_kyc_mirror(user_id: str) -> AccessControlKycMirrorStub:
    return AccessControlKycMirrorStub(userId=user_id)
