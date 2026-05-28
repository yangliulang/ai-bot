"""Admin console auth DTOs (dev / BFF; replace when SSO or product OpenAPI freezes)."""

from pydantic import BaseModel, Field, field_validator


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=128, description="Console operator id")
    password: str = Field(
        min_length=1,
        max_length=256,
        description="Plain password (TLS in transit)",
    )

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value


class AdminLoginResponse(BaseModel):
    access_token: str = Field(description="Opaque bearer; store as secret client-side")
    token_type: str = Field(default="bearer", description="OAuth2-style type tag")
    username: str = Field(description="Echo of authenticated operator id")


class AdminRegisterRequest(BaseModel):
    """Self-service signup for DB-backed operators (see BACKEND_SPEC §3.1)."""

    username: str = Field(min_length=1, max_length=128, description="Console operator id")
    password: str = Field(
        min_length=8,
        max_length=256,
        description="Plain password (TLS in transit); min length 8 for register",
    )

    @field_validator("username", mode="before")
    @classmethod
    def strip_username(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value
