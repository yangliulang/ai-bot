"""Admin Confirmation Rules API — ai.confirmation-rules."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from chainup_agent.api.deps import DbSession, require_admin_console_bearer, require_admin_console_user
from chainup_agent.api.schemas.admin_confirmation_rules import (
    ConfirmationRuleCreateRequest,
    ConfirmationRuleEnabledPatchRequest,
    ConfirmationRuleItem,
    ConfirmationRuleListResponse,
    ConfirmationRuleResetResponse,
    ConfirmationRuleUpdateRequest,
)
from chainup_agent.application.admin_confirmation_rules import (
    create_custom_confirmation_rule,
    delete_custom_confirmation_rule,
    get_confirmation_rule,
    list_confirmation_rules,
    patch_rule_enabled,
    reset_confirmation_rules,
    update_custom_confirmation_rule,
)

router = APIRouter(
    prefix="/api/v1/admin/confirmation-rules",
    tags=["Admin — Confirmation rules"],
    dependencies=[Depends(require_admin_console_bearer)],
)


@router.get("", response_model=ConfirmationRuleListResponse, response_model_by_alias=True)
async def admin_list_confirmation_rules(db: DbSession) -> ConfirmationRuleListResponse:
    return await list_confirmation_rules(db)


@router.post(
    "",
    response_model=ConfirmationRuleItem,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
)
async def admin_create_confirmation_rule(
    db: DbSession,
    body: ConfirmationRuleCreateRequest,
    actor: Annotated[str, Depends(require_admin_console_user)],
) -> ConfirmationRuleItem:
    item = await create_custom_confirmation_rule(db, body, actor=actor)
    await db.commit()
    return item


@router.post(
    "/reset",
    response_model=ConfirmationRuleResetResponse,
    response_model_by_alias=True,
)
async def admin_reset_confirmation_rules(db: DbSession) -> ConfirmationRuleResetResponse:
    out = await reset_confirmation_rules(db)
    await db.commit()
    return out


@router.get("/{rule_id}", response_model=ConfirmationRuleItem, response_model_by_alias=True)
async def admin_get_confirmation_rule(rule_id: str, db: DbSession) -> ConfirmationRuleItem:
    return await get_confirmation_rule(db, rule_id)


@router.put("/{rule_id}", response_model=ConfirmationRuleItem, response_model_by_alias=True)
async def admin_update_confirmation_rule(
    rule_id: str,
    db: DbSession,
    body: ConfirmationRuleUpdateRequest,
) -> ConfirmationRuleItem:
    item = await update_custom_confirmation_rule(db, rule_id, body)
    await db.commit()
    return item


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_confirmation_rule(rule_id: str, db: DbSession) -> None:
    await delete_custom_confirmation_rule(db, rule_id)
    await db.commit()


@router.patch("/{rule_id}/enabled", response_model=ConfirmationRuleItem, response_model_by_alias=True)
async def admin_patch_confirmation_rule_enabled(
    rule_id: str,
    db: DbSession,
    body: ConfirmationRuleEnabledPatchRequest,
) -> ConfirmationRuleItem:
    item = await patch_rule_enabled(db, rule_id, enabled=body.enabled)
    await db.commit()
    return item
