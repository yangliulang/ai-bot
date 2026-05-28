"""Pydantic DTOs — Admin access control (product OpenAPI admin/access-control.yaml subset)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WhitelistEntryItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    entry_id: str = Field(alias="entryId")
    list_id: str = Field(alias="listId")
    user_uid: str = Field(alias="userUid")
    user_id_masked: str = Field(alias="userIdMasked")
    note: str | None = None
    added_at: datetime = Field(alias="addedAt")
    added_by: str | None = Field(default=None, alias="addedBy")


class WhitelistListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[WhitelistEntryItem]
    total: int


class WhitelistCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    list_id: str = Field(alias="listId", min_length=1, max_length=64)
    user_uid: str = Field(
        alias="userUid",
        min_length=1,
        max_length=64,
        description="Canonical user id for runtime match (Telegram tg_id string).",
    )
    user_id_masked: str | None = Field(
        default=None,
        alias="userIdMasked",
        max_length=128,
        description="Display/masked label; defaults to userUid when omitted.",
    )
    note: str | None = Field(default=None, max_length=512)


class BanItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    ban_id: str = Field(alias="banId")
    user_uid: str = Field(alias="userUid")
    reason_code: str = Field(alias="reasonCode")
    scope: str
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    linked_pause: bool = Field(alias="linkedPause")
    created_at: datetime = Field(alias="createdAt")
    created_by: str | None = Field(default=None, alias="createdBy")


class BanListResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    items: list[BanItem]
    total: int


class BanCreateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_uid: str = Field(alias="userUid", min_length=1, max_length=64)
    reason_code: str = Field(alias="reasonCode", min_length=1, max_length=64)
    scope: str = Field(default="AGENT_PRODUCT", max_length=32)
    expires_at: datetime | None = Field(default=None, alias="expiresAt")
    linked_pause: bool = Field(default=False, alias="linkedPause")


class MinVipTierResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_key: str = Field(default="AGENT_MIN_VIP_TIER", alias="configKey")
    min_vip_tier: int = Field(alias="minVipTier", ge=0, le=127)
    updated_at: datetime | None = Field(default=None, alias="updatedAt")


class MinVipTierPatchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    min_vip_tier: int = Field(alias="minVipTier", ge=0, le=127)


class RolloutPolicyResponse(BaseModel):
    """FR-MC601 read shape — minimal V1 (toggle + metadata)."""

    model_config = ConfigDict(populate_by_name=True)

    rollout_whitelist_enforced: bool = Field(
        alias="rolloutWhitelistEnforced",
        description="Mirrors CHAINUP_AGENT_ACCESS_ROLLOUT_WHITELIST_ENFORCED.",
    )


class RolloutPolicyPatchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    rollout_whitelist_enforced: bool | None = Field(default=None, alias="rolloutWhitelistEnforced")


class AccessControlKycMirrorStub(BaseModel):
    """FR-MC605 stub — no upstream KYC in Phase1."""

    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(alias="userId")
    available: bool = False
    message: str = "KYC mirror not wired in this deployment."
    mirror: dict[str, Any] = Field(default_factory=dict)
