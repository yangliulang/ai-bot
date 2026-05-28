"""Admin trading-agent GlobalConfigBundle schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GlobalConfigBundleResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_version: int = Field(alias="configVersion")
    values: dict[str, Any] = Field(default_factory=dict)
    defaults: dict[str, Any] | None = Field(
        default=None,
        description="Env/product defaults for Admin read-only diff (extension).",
    )
    applied_keys: list[str] = Field(default_factory=list, alias="appliedKeys")


class GlobalConfigBundlePatchBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    values: dict[str, Any] = Field(default_factory=dict)
    expected_config_version: int | None = Field(
        default=None, alias="expectedConfigVersion"
    )


class GlobalConfigBundlePatchResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    config_version: int = Field(alias="configVersion")
    values: dict[str, Any] = Field(default_factory=dict)
    applied_keys: list[str] = Field(default_factory=list, alias="appliedKeys")
