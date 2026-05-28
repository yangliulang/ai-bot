"""Admin AI Settings — CRUD aligned with product-doc OpenAPI `admin/ai-settings.yaml`."""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.telegram_llm_narrate_policy import (
    DEFAULT_TELEGRAM_LLM_NARRATE,
    TELEGRAM_LLM_NARRATE_SCENARIO_KEYS,
    normalize_telegram_llm_narrate_defaults,
)
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.admin_ai_settings import (
    AdminAiDocument,
    AdminAiModel,
    AdminAiProvider,
)

DOC_GATEWAY_DEFAULTS = "gateway_defaults"
DOC_HEALTH_POLICY = "health_policy"

DEFAULT_GATEWAY_DEFAULTS: dict[str, Any] = {
    "defaultProviderId": "demo",
    "defaultModelId": "gpt-4.1-mini",
    "orchestrationExecutionBudget": {
        "maxToolCallsPerExecution": 32,
        "maxOrchestrationStepsPerExecution": 32,
        "maxModelTurnsPerExecution": None,
    },
    # Product prototype `/ai-settings` (aiRuntimePolicyMock) — stored alongside OpenAPI fields.
    "defaultInferenceModel": "gpt-4.1",
    "scenarioChatModel": "gpt-4.1-mini",
    "scenarioTradingModel": "gpt-4.1",
    "scenarioRiskModel": "gpt-4.1",
    "maxContextTokens": 128_000,
    "maxOutputTokens": 4096,
    "timeoutSec": 120,
    "fallbackOnPrimaryFailure": True,
    "fallbackOnTimeout": True,
    "downgradePeakTraffic": False,
    "fallbackModel": "gpt-4.1-mini",
    "maxTokensPerRequest": 32_000,
    "dailyTokenBudgetM": 50,
    "rateLimitRpm": 600,
    "intentNluUseLlm": False,
    "intentClarifyUseLlm": False,
    "telegramLlmNarrate": dict(DEFAULT_TELEGRAM_LLM_NARRATE),
}

DEFAULT_HEALTH_POLICY: dict[str, Any] = {}

# Runtime policy JSON fields that reference `admin_ai_model.model_id` (catalog id).
_GATEWAY_POLICY_MODEL_REF_KEYS: tuple[str, ...] = (
    "defaultModelId",
    "defaultInferenceModel",
    "scenarioChatModel",
    "scenarioTradingModel",
    "scenarioRiskModel",
    "fallbackModel",
)


def _utc_now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_if_match(raw: str | None) -> str | None:
    if raw is None or not raw.strip():
        return None
    s = raw.strip()
    if s.startswith("W/"):
        s = s[2:].strip()
    if len(s) >= 2 and s.startswith('"') and s.endswith('"'):
        s = s[1:-1]
    return s.strip() or None


def _check_version(row_version: int, if_match: str | None) -> None:
    expect = _normalize_if_match(if_match)
    if expect is None:
        return
    if expect != str(row_version):
        raise AppError(
            code="AGENT_AI_SETTINGS_VERSION_CONFLICT",
            message="资源已被他人更新，请刷新后重试（If-Match / rowVersion 不一致）。",
            status_code=409,
            details={"expectedVersion": expect, "currentVersion": str(row_version)},
        )


async def _load_document(session: AsyncSession, key: str) -> AdminAiDocument | None:
    return await session.get(AdminAiDocument, key)


async def ensure_gateway_defaults(session: AsyncSession) -> AdminAiDocument:
    row = await _load_document(session, DOC_GATEWAY_DEFAULTS)
    if row is None:
        row = AdminAiDocument(
            doc_key=DOC_GATEWAY_DEFAULTS,
            payload_json=json.dumps(DEFAULT_GATEWAY_DEFAULTS, ensure_ascii=False),
            row_version=1,
        )
        session.add(row)
        await session.flush()
    return row


async def ensure_health_policy(session: AsyncSession) -> AdminAiDocument:
    row = await _load_document(session, DOC_HEALTH_POLICY)
    if row is None:
        row = AdminAiDocument(
            doc_key=DOC_HEALTH_POLICY,
            payload_json=json.dumps(DEFAULT_HEALTH_POLICY, ensure_ascii=False),
            row_version=1,
        )
        session.add(row)
        await session.flush()
    return row


def merge_gateway_payload(existing: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = dict(existing)
    for k, v in patch.items():
        if (
            k == "orchestrationExecutionBudget"
            and isinstance(v, dict)
            and isinstance(out.get("orchestrationExecutionBudget"), dict)
        ):
            ob = dict(out["orchestrationExecutionBudget"])
            for bk, bv in v.items():
                ob[bk] = bv
            out["orchestrationExecutionBudget"] = ob
        elif k == "telegramLlmNarrate" and isinstance(v, dict):
            base = out.get("telegramLlmNarrate")
            tn = dict(base) if isinstance(base, dict) else {}
            for bk, bv in v.items():
                tn[bk] = bv
            out["telegramLlmNarrate"] = tn
        else:
            out[k] = v
    return out


def validate_gateway_patch(patch: dict[str, Any]) -> None:
    if "intentNluUseLlm" in patch and patch["intentNluUseLlm"] is not None:
        if not isinstance(patch["intentNluUseLlm"], bool):
            raise AppError(
                code="VALIDATION_ERROR",
                message="intentNluUseLlm 须为 boolean",
                status_code=422,
                details={"field": "intentNluUseLlm"},
            )
    if "intentClarifyUseLlm" in patch and patch["intentClarifyUseLlm"] is not None:
        if not isinstance(patch["intentClarifyUseLlm"], bool):
            raise AppError(
                code="VALIDATION_ERROR",
                message="intentClarifyUseLlm 须为 boolean",
                status_code=422,
                details={"field": "intentClarifyUseLlm"},
            )
    narrate_patch = patch.get("telegramLlmNarrate")
    if narrate_patch is not None:
        if not isinstance(narrate_patch, dict):
            raise AppError(
                code="VALIDATION_ERROR",
                message="telegramLlmNarrate 须为 object",
                status_code=422,
                details={"field": "telegramLlmNarrate"},
            )
        for key, val in narrate_patch.items():
            if key not in TELEGRAM_LLM_NARRATE_SCENARIO_KEYS:
                raise AppError(
                    code="VALIDATION_ERROR",
                    message=f"telegramLlmNarrate 未知字段: {key}",
                    status_code=422,
                    details={"field": f"telegramLlmNarrate.{key}"},
                )
            if val is not None and not isinstance(val, bool):
                raise AppError(
                    code="VALIDATION_ERROR",
                    message=f"telegramLlmNarrate.{key} 须为 boolean",
                    status_code=422,
                    details={"field": f"telegramLlmNarrate.{key}"},
                )
    bud = patch.get("orchestrationExecutionBudget")
    if not isinstance(bud, dict):
        return
    for key in ("maxToolCallsPerExecution", "maxOrchestrationStepsPerExecution"):
        if key not in bud or bud[key] is None:
            continue
        try:
            n = int(bud[key])
        except (TypeError, ValueError):
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"orchestrationExecutionBudget.{key} 须为正整数",
                status_code=422,
                details={"field": key},
            ) from None
        if n < 1:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"orchestrationExecutionBudget.{key} 须 ≥ 1",
                status_code=422,
                details={"field": key},
            )
    if "maxModelTurnsPerExecution" in bud and bud["maxModelTurnsPerExecution"] is not None:
        try:
            n = int(bud["maxModelTurnsPerExecution"])
        except (TypeError, ValueError):
            raise AppError(
                code="VALIDATION_ERROR",
                message="orchestrationExecutionBudget.maxModelTurnsPerExecution 须为正整数或 null",
                status_code=422,
                details={"field": "maxModelTurnsPerExecution"},
            ) from None
        if n < 1:
            raise AppError(
                code="VALIDATION_ERROR",
                message="orchestrationExecutionBudget.maxModelTurnsPerExecution 须 ≥ 1",
                status_code=422,
                details={"field": "maxModelTurnsPerExecution"},
            )


def merge_health_payload(existing: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    return {**existing, **patch}


async def list_providers(session: AsyncSession) -> list[AdminAiProvider]:
    res = await session.execute(select(AdminAiProvider).order_by(AdminAiProvider.provider_id.asc()))
    return list(res.scalars().all())


async def get_provider(session: AsyncSession, provider_id: str) -> AdminAiProvider | None:
    return await session.get(AdminAiProvider, provider_id.strip())


async def allocate_provider_id(session: AsyncSession, display_name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", display_name.strip().lower()).strip("-")[:40]
    if not base:
        base = "provider"
    cand = base
    for n in range(0, 120):
        pid = cand if n == 0 else f"{base}-{n}"
        if await session.get(AdminAiProvider, pid) is None:
            return pid
    return f"{base}-{uuid.uuid4().hex[:10]}"


async def create_provider(
    session: AsyncSession,
    *,
    display_name: str,
    base_url: str,
    secret_ref: str | None,
    if_match: str | None,
) -> AdminAiProvider:
    _ = if_match  # POST create: If-Match optional per OpenAPI; ignored

    pid = await allocate_provider_id(session, display_name or "provider")
    row = AdminAiProvider(
        provider_id=pid,
        display_name=display_name.strip()[:128],
        base_url=base_url.strip()[:512],
        secret_ref=(secret_ref.strip()[:512] if secret_ref and secret_ref.strip() else None),
        row_version=1,
    )
    session.add(row)
    await session.flush()
    return row


async def assert_gateway_catalog_model_refs_exist(
    session: AsyncSession, merged_gateway: dict[str, Any]
) -> None:
    """Every non-empty routing model string must resolve to a catalog row (PK `model_id`)."""
    missing: list[dict[str, str]] = []
    for key in _GATEWAY_POLICY_MODEL_REF_KEYS:
        raw = merged_gateway.get(key)
        if not isinstance(raw, str):
            continue
        mid = raw.strip()
        if not mid:
            continue
        row = await get_model(session, mid)
        if row is None:
            missing.append({"field": key, "modelId": mid})
    if missing:
        raise AppError(
            code="AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG",
            message="网关策略中存在未注册的模型 catalog id，请先在「厂商→模型目录」中添加或更正字段后再保存。",
            status_code=422,
            details={"missing": missing},
        )


async def patch_provider(
    session: AsyncSession,
    provider_id: str,
    *,
    display_name: str | None,
    base_url: str | None,
    secret_ref: str | None,
    if_match: str | None,
) -> AdminAiProvider:
    row = await get_provider(session, provider_id)
    if row is None:
        raise AppError(
            code="AGENT_AI_PROVIDER_NOT_FOUND",
            message="未找到该 LLM Provider",
            status_code=404,
            details={"providerId": provider_id},
        )
    _check_version(int(row.row_version), if_match)
    if display_name is not None:
        row.display_name = display_name.strip()[:128]
    if base_url is not None:
        row.base_url = base_url.strip()[:512]
    if secret_ref is not None:
        s = secret_ref.strip()
        row.secret_ref = s[:512] if s else None
    row.row_version = int(row.row_version) + 1
    await session.flush()
    return row


async def delete_provider(
    session: AsyncSession,
    provider_id: str,
    *,
    if_match: str | None,
) -> None:
    row = await get_provider(session, provider_id)
    if row is None:
        raise AppError(
            code="AGENT_AI_PROVIDER_NOT_FOUND",
            message="未找到该 LLM Provider",
            status_code=404,
            details={"providerId": provider_id.strip()},
        )
    _check_version(int(row.row_version), if_match)
    await session.delete(row)
    await session.flush()


async def list_models(session: AsyncSession, provider_id: str | None) -> list[AdminAiModel]:
    stmt = select(AdminAiModel).order_by(AdminAiModel.model_id.asc())
    if provider_id and provider_id.strip():
        stmt = stmt.where(AdminAiModel.provider_id == provider_id.strip())
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def get_model(session: AsyncSession, model_id: str) -> AdminAiModel | None:
    return await session.get(AdminAiModel, model_id.strip())


async def patch_model(
    session: AsyncSession,
    model_id: str,
    *,
    provider_id: str | None,
    status: str | None,
    context_window_tokens: int | None,
    api_model: str | None = None,
    patch_api_model: bool = False,
    if_match: str | None,
) -> AdminAiModel:
    row = await session.get(AdminAiModel, model_id.strip())
    if row is None:
        raise AppError(
            code="AGENT_AI_MODEL_NOT_FOUND",
            message="未找到该模型",
            status_code=404,
            details={"modelId": model_id},
        )
    _check_version(int(row.row_version), if_match)
    changed = False
    if provider_id is not None:
        prov = await get_provider(session, provider_id)
        if prov is None:
            raise AppError(
                code="AGENT_AI_PROVIDER_NOT_FOUND",
                message="未找到该 LLM Provider",
                status_code=404,
                details={"providerId": provider_id.strip()},
            )
        new_pid = prov.provider_id
        if row.provider_id != new_pid:
            row.provider_id = new_pid
            changed = True
    if status is not None:
        s = status.strip()[:32]
        if row.status != s:
            row.status = s
            changed = True
    if context_window_tokens is not None:
        v = int(context_window_tokens)
        if row.context_window_tokens != v:
            row.context_window_tokens = v
            changed = True
    if patch_api_model:
        s = (api_model or "").strip() if api_model is not None else ""
        normalized = None if not s else s[:512]
        if row.api_model != normalized:
            row.api_model = normalized
            changed = True
    if changed:
        row.row_version = int(row.row_version) + 1
    await session.flush()
    return row


async def delete_model(
    session: AsyncSession,
    model_id: str,
    *,
    if_match: str | None,
) -> None:
    row = await session.get(AdminAiModel, model_id.strip())
    if row is None:
        raise AppError(
            code="AGENT_AI_MODEL_NOT_FOUND",
            message="未找到该模型",
            status_code=404,
            details={"modelId": model_id},
        )
    _check_version(int(row.row_version), if_match)
    await session.delete(row)
    await session.flush()


async def create_model(
    session: AsyncSession,
    *,
    provider_id: str,
    model_id: str,
    api_model: str | None,
    status: str | None,
    context_window_tokens: int | None,
) -> AdminAiModel:
    prov = await get_provider(session, provider_id)
    if prov is None:
        raise AppError(
            code="AGENT_AI_PROVIDER_NOT_FOUND",
            message="未找到该 LLM Provider",
            status_code=404,
            details={"providerId": provider_id.strip()},
        )
    mid = model_id.strip()
    if not mid:
        raise AppError(
            code="VALIDATION_ERROR",
            message="modelId 不能为空",
            status_code=422,
            details={"field": "modelId"},
        )
    mid_norm = mid[:128]
    existing = await session.get(AdminAiModel, mid_norm)
    if existing is not None:
        raise AppError(
            code="AGENT_AI_MODEL_ID_CONFLICT",
            message="该模型 ID 已存在",
            status_code=409,
            details={"modelId": mid_norm},
        )
    st_raw = (status or "enabled").strip()
    st = st_raw[:32] if st_raw else "enabled"

    api_raw = (api_model or "").strip() if api_model is not None else ""
    api_norm = api_raw[:512] if api_raw else None

    row = AdminAiModel(
        model_id=mid_norm,
        provider_id=prov.provider_id,
        api_model=api_norm,
        status=st,
        context_window_tokens=(
            int(context_window_tokens) if context_window_tokens is not None else None
        ),
        row_version=1,
    )
    session.add(row)
    await session.flush()
    return row


async def get_gateway_defaults_document(session: AsyncSession) -> tuple[dict[str, Any], int]:
    row = await ensure_gateway_defaults(session)
    data = json.loads(row.payload_json)
    if not isinstance(data, dict):
        data = dict(DEFAULT_GATEWAY_DEFAULTS)
    return data, int(row.row_version)


async def read_gateway_defaults_merged(session: AsyncSession) -> tuple[dict[str, Any], int]:
    row = await ensure_gateway_defaults(session)
    raw = json.loads(row.payload_json)
    if not isinstance(raw, dict):
        raw = {}
    merged_view = normalize_telegram_llm_narrate_defaults(
        merge_gateway_payload(DEFAULT_GATEWAY_DEFAULTS, raw)
    )
    return merged_view, int(row.row_version)


async def patch_gateway_defaults(
    session: AsyncSession,
    patch: dict[str, Any],
    if_match: str | None,
) -> tuple[dict[str, Any], int]:
    validate_gateway_patch(patch)
    row = await ensure_gateway_defaults(session)
    _check_version(int(row.row_version), if_match)
    cur = json.loads(row.payload_json)
    if not isinstance(cur, dict):
        cur = {}
    merged = merge_gateway_payload(cur, patch)
    full_view = merge_gateway_payload(DEFAULT_GATEWAY_DEFAULTS, merged)
    await assert_gateway_catalog_model_refs_exist(session, full_view)
    row.payload_json = json.dumps(merged, ensure_ascii=False)
    row.row_version = int(row.row_version) + 1
    await session.flush()
    return normalize_telegram_llm_narrate_defaults(full_view), int(row.row_version)


async def get_health_policy_document(session: AsyncSession) -> tuple[dict[str, Any], int]:
    row = await ensure_health_policy(session)
    data = json.loads(row.payload_json)
    if not isinstance(data, dict):
        data = {}
    return data, int(row.row_version)


async def patch_health_policy(
    session: AsyncSession,
    patch: dict[str, Any],
    if_match: str | None,
) -> tuple[dict[str, Any], int]:
    row = await ensure_health_policy(session)
    _check_version(int(row.row_version), if_match)
    cur = json.loads(row.payload_json)
    if not isinstance(cur, dict):
        cur = {}
    merged = merge_health_payload(cur, patch)
    row.payload_json = json.dumps(merged, ensure_ascii=False)
    row.row_version = int(row.row_version) + 1
    await session.flush()
    return merged, int(row.row_version)


async def probe_provider_health(session: AsyncSession, provider_id: str) -> dict[str, Any]:
    row = await get_provider(session, provider_id)
    if row is None:
        raise AppError(
            code="AGENT_AI_PROVIDER_NOT_FOUND",
            message="未找到该 LLM Provider",
            status_code=404,
            details={"providerId": provider_id},
        )
    base = row.base_url.strip().rstrip("/")
    t0_ms = datetime.now(UTC).timestamp() * 1000
    ok = False
    msg = ""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            try:
                r = await client.head(
                    base + "/", headers={"User-Agent": "ChainUp-Agent-HealthProbe/1"}
                )
                ok = r.status_code < 500
                msg = f"HEAD {base}/ HTTP {r.status_code}"
            except httpx.HTTPError:
                try:
                    r = await client.get(
                        base + "/", headers={"User-Agent": "ChainUp-Agent-HealthProbe/1"}
                    )
                    ok = r.status_code < 500
                    msg = f"GET {base}/ HTTP {r.status_code}"
                except httpx.HTTPError as exc:
                    msg = str(exc)[:200]
                    ok = False
    except httpx.TimeoutException:
        msg = "probe timeout"
        ok = False
    latency = int(datetime.now(UTC).timestamp() * 1000 - t0_ms)
    return {
        "ok": ok,
        "latencyMs": max(latency, 0),
        "checkedAt": _utc_now_iso(),
        "message": msg[:512],
    }


async def seed_demo_ai_catalog(session: AsyncSession) -> None:
    """Idempotent demo rows for local/admin parity with product-doc prototype options."""
    if await session.get(AdminAiProvider, "demo") is not None:
        return
    prov = AdminAiProvider(
        provider_id="demo",
        display_name="Demo OpenAI-compatible",
        base_url="https://api.openai.com/v1",
        secret_ref=None,
        row_version=1,
    )
    session.add(prov)
    for mid, ctx in (
        ("gpt-4.1", 1_000_000),
        ("gpt-4.1-mini", 128_000),
        ("claude-3.5-sonnet", 200_000),
        ("gemini-1.5-pro", 1_000_000),
    ):
        session.add(
            AdminAiModel(
                model_id=mid,
                provider_id="demo",
                status="enabled",
                context_window_tokens=ctx,
                row_version=1,
            )
        )
    await session.flush()
