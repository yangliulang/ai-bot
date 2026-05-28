from pydantic import BaseModel, Field


class ErrorBody(BaseModel):
    """Unified API error envelope (align with observability SSOT incrementally)."""

    code: str = Field(description="Stable machine-readable code")
    message: str
    request_id: str
    details: dict | None = None


class StubBody(BaseModel):
    """Roadmap Phase-1 scaffolding marker — replaced by concrete DTOs + OpenAPI $ref."""

    status: str = Field(default="not_implemented", examples=["not_implemented"])
    phase: str = Field(default="1")
    operation_id: str
    hint: str = Field(
        default=(
            "Implement per monorepo product-doc/product/roadmap.md Phase 1 "
            "+ product-doc/specs/openapi SSOT."
        ),
    )
