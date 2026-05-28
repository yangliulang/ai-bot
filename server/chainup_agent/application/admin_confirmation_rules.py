"""Admin confirmation rules — persistence, CRUD, enabled map (ai.confirmation-rules)."""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.admin_confirmation_rules import (
    ConfirmationRuleCreateRequest,
    ConfirmationRuleItem,
    ConfirmationRuleListResponse,
    ConfirmationRuleResetResponse,
    ConfirmationRuleUpdateRequest,
    TriggerConditionRow,
)
from chainup_agent.core.errors import AppError
from chainup_agent.domain.confirmation_rules_catalog import (
    BUILTIN_CONFIRMATION_RULES,
    DEMO_CUSTOM_CONFIRMATION_RULES,
    VALID_ACTIONS,
    VALID_RISK_LEVELS,
    VALID_SCENARIOS,
    VALID_TRIGGER_FIELDS,
    VALID_TRIGGER_OPS,
    ConfirmationRuleDefinition,
    is_builtin_rule_id,
)
from chainup_agent.infrastructure.persistence.models.admin_confirmation_rule_custom import (
    AdminConfirmationRuleCustom,
)
from chainup_agent.infrastructure.persistence.models.admin_confirmation_rule_enabled import (
    AdminConfirmationRuleEnabled,
)


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _parse_json_list(raw: str) -> list:
    try:
        val = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AppError(
            code="AGENT_ADMIN_CONFIRMATION_RULE_CORRUPT",
            message="规则 JSON 数据损坏。",
            status_code=500,
        ) from exc
    if not isinstance(val, list):
        raise AppError(
            code="AGENT_ADMIN_CONFIRMATION_RULE_CORRUPT",
            message="规则 JSON 数据损坏。",
            status_code=500,
        )
    return val


def _validate_trigger_rows(rows: list[TriggerConditionRow]) -> None:
    for row in rows:
        if row.field_key not in VALID_TRIGGER_FIELDS:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"非法 trigger fieldKey: {row.field_key}",
                status_code=422,
            )
        if row.operator not in VALID_TRIGGER_OPS:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"非法 trigger operator: {row.operator}",
                status_code=422,
            )


def _validate_rule_body(
    *,
    risk_level: str,
    action: str,
    scenarios: list[str],
    trigger_conditions: list[TriggerConditionRow],
) -> None:
    if risk_level not in VALID_RISK_LEVELS:
        raise AppError(code="VALIDATION_ERROR", message="非法 riskLevel。", status_code=422)
    if action not in VALID_ACTIONS:
        raise AppError(code="VALIDATION_ERROR", message="非法 action。", status_code=422)
    if not scenarios:
        raise AppError(code="VALIDATION_ERROR", message="scenarios 不能为空。", status_code=422)
    for s in scenarios:
        if s not in VALID_SCENARIOS:
            raise AppError(code="VALIDATION_ERROR", message=f"非法 scenario: {s}", status_code=422)
    if not trigger_conditions:
        raise AppError(code="VALIDATION_ERROR", message="triggerConditions 不能为空。", status_code=422)
    _validate_trigger_rows(trigger_conditions)


def _rule_def_from_custom_row(row: AdminConfirmationRuleCustom) -> ConfirmationRuleDefinition:
    return {
        "id": row.rule_id,
        "title": row.title,
        "summary": row.summary,
        "riskLevel": row.risk_level,  # type: ignore[typeddict-item]
        "triggerConditions": _parse_json_list(row.trigger_conditions_json),  # type: ignore[typeddict-item]
        "scenarios": _parse_json_list(row.scenarios_json),  # type: ignore[typeddict-item]
        "action": row.action,  # type: ignore[typeddict-item]
        "defaultEnabled": row.default_enabled,
    }


async def _load_enabled_overrides(session: AsyncSession) -> dict[str, bool]:
    res = await session.execute(select(AdminConfirmationRuleEnabled))
    return {r.rule_id: r.enabled for r in res.scalars().all()}


def _resolve_enabled(
    rule_id: str,
    default_enabled: bool,
    overrides: dict[str, bool],
) -> bool:
    if rule_id in overrides:
        return overrides[rule_id]
    return default_enabled


def _to_item(
    rule: ConfirmationRuleDefinition,
    *,
    enabled: bool,
    is_builtin: bool,
    updated_at: datetime | None = None,
) -> ConfirmationRuleItem:
    return ConfirmationRuleItem(
        id=rule["id"],
        title=rule["title"],
        summary=rule["summary"],
        riskLevel=rule["riskLevel"],
        triggerConditions=[TriggerConditionRow.model_validate(r) for r in rule["triggerConditions"]],
        scenarios=rule["scenarios"],  # type: ignore[arg-type]
        action=rule["action"],
        defaultEnabled=rule["defaultEnabled"],
        enabled=enabled,
        isBuiltin=is_builtin,
        updatedAt=updated_at,
    )


async def _load_custom_rules(session: AsyncSession) -> list[AdminConfirmationRuleCustom]:
    res = await session.execute(
        select(AdminConfirmationRuleCustom).order_by(AdminConfirmationRuleCustom.created_at.asc())
    )
    return list(res.scalars().all())


async def list_confirmation_rules(session: AsyncSession) -> ConfirmationRuleListResponse:
    overrides = await _load_enabled_overrides(session)
    custom_rows = await _load_custom_rules(session)
    if not custom_rows:
        await seed_demo_custom_rules(session)
        custom_rows = await _load_custom_rules(session)
    items: list[ConfirmationRuleItem] = []

    for rule in BUILTIN_CONFIRMATION_RULES:
        enabled = _resolve_enabled(rule["id"], rule["defaultEnabled"], overrides)
        items.append(_to_item(rule, enabled=enabled, is_builtin=True))

    for row in custom_rows:
        rule = _rule_def_from_custom_row(row)
        enabled = _resolve_enabled(rule["id"], rule["defaultEnabled"], overrides)
        items.append(
            _to_item(rule, enabled=enabled, is_builtin=False, updated_at=row.updated_at),
        )

    enabled_count = sum(1 for i in items if i.enabled)
    return ConfirmationRuleListResponse(items=items, total=len(items), enabledCount=enabled_count)


async def get_confirmation_rule(session: AsyncSession, rule_id: str) -> ConfirmationRuleItem:
    rid = rule_id.strip()
    overrides = await _load_enabled_overrides(session)

    builtin = next((r for r in BUILTIN_CONFIRMATION_RULES if r["id"] == rid), None)
    if builtin is not None:
        enabled = _resolve_enabled(rid, builtin["defaultEnabled"], overrides)
        return _to_item(builtin, enabled=enabled, is_builtin=True)

    res = await session.execute(
        select(AdminConfirmationRuleCustom).where(AdminConfirmationRuleCustom.rule_id == rid)
    )
    row = res.scalar_one_or_none()
    if row is None:
        raise AppError(
            code="AGENT_ADMIN_CONFIRMATION_RULE_NOT_FOUND",
            message="人工确认规则不存在。",
            status_code=404,
            details={"ruleId": rid},
        )
    rule = _rule_def_from_custom_row(row)
    enabled = _resolve_enabled(rid, rule["defaultEnabled"], overrides)
    return _to_item(rule, enabled=enabled, is_builtin=False, updated_at=row.updated_at)


async def create_custom_confirmation_rule(
    session: AsyncSession,
    body: ConfirmationRuleCreateRequest,
    *,
    actor: str,
) -> ConfirmationRuleItem:
    _validate_rule_body(
        risk_level=body.risk_level,
        action=body.action,
        scenarios=list(body.scenarios),
        trigger_conditions=body.trigger_conditions,
    )
    rule_id = f"custom-{uuid.uuid4()}"
    row = AdminConfirmationRuleCustom(
        rule_id=rule_id,
        title=body.title.strip(),
        summary=body.summary.strip(),
        risk_level=body.risk_level,
        action=body.action,
        scenarios_json=json.dumps(list(body.scenarios), ensure_ascii=False),
        trigger_conditions_json=json.dumps(
            [r.model_dump(by_alias=True) for r in body.trigger_conditions],
            ensure_ascii=False,
        ),
        default_enabled=body.default_enabled,
        created_by=actor[:128],
    )
    session.add(row)
    await session.flush()

    if body.default_enabled is False:
        session.add(AdminConfirmationRuleEnabled(rule_id=rule_id, enabled=False))

    overrides = await _load_enabled_overrides(session)
    rule = _rule_def_from_custom_row(row)
    enabled = _resolve_enabled(rule_id, rule["defaultEnabled"], overrides)
    return _to_item(rule, enabled=enabled, is_builtin=False, updated_at=row.updated_at)


async def update_custom_confirmation_rule(
    session: AsyncSession,
    rule_id: str,
    body: ConfirmationRuleUpdateRequest,
) -> ConfirmationRuleItem:
    rid = rule_id.strip()
    if is_builtin_rule_id(rid):
        raise AppError(
            code="AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY",
            message="内置规则不可编辑，仅可切换启用状态。",
            status_code=409,
            details={"ruleId": rid},
        )
    _validate_rule_body(
        risk_level=body.risk_level,
        action=body.action,
        scenarios=list(body.scenarios),
        trigger_conditions=body.trigger_conditions,
    )
    res = await session.execute(
        select(AdminConfirmationRuleCustom).where(AdminConfirmationRuleCustom.rule_id == rid)
    )
    row = res.scalar_one_or_none()
    if row is None:
        raise AppError(
            code="AGENT_ADMIN_CONFIRMATION_RULE_NOT_FOUND",
            message="人工确认规则不存在。",
            status_code=404,
            details={"ruleId": rid},
        )
    row.title = body.title.strip()
    row.summary = body.summary.strip()
    row.risk_level = body.risk_level
    row.action = body.action
    row.scenarios_json = json.dumps(list(body.scenarios), ensure_ascii=False)
    row.trigger_conditions_json = json.dumps(
        [r.model_dump(by_alias=True) for r in body.trigger_conditions],
        ensure_ascii=False,
    )
    row.default_enabled = body.default_enabled
    row.updated_at = _now_utc()
    await session.flush()

    overrides = await _load_enabled_overrides(session)
    rule = _rule_def_from_custom_row(row)
    enabled = _resolve_enabled(rid, rule["defaultEnabled"], overrides)
    return _to_item(rule, enabled=enabled, is_builtin=False, updated_at=row.updated_at)


async def delete_custom_confirmation_rule(session: AsyncSession, rule_id: str) -> None:
    rid = rule_id.strip()
    if is_builtin_rule_id(rid):
        raise AppError(
            code="AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY",
            message="内置规则不可删除。",
            status_code=409,
            details={"ruleId": rid},
        )
    res = await session.execute(
        select(AdminConfirmationRuleCustom).where(AdminConfirmationRuleCustom.rule_id == rid)
    )
    row = res.scalar_one_or_none()
    if row is None:
        raise AppError(
            code="AGENT_ADMIN_CONFIRMATION_RULE_NOT_FOUND",
            message="人工确认规则不存在。",
            status_code=404,
            details={"ruleId": rid},
        )
    await session.delete(row)
    res_e = await session.execute(
        select(AdminConfirmationRuleEnabled).where(AdminConfirmationRuleEnabled.rule_id == rid)
    )
    en = res_e.scalar_one_or_none()
    if en is not None:
        await session.delete(en)


async def patch_rule_enabled(session: AsyncSession, rule_id: str, *, enabled: bool) -> ConfirmationRuleItem:
    rid = rule_id.strip()
    # Ensure rule exists (builtin or custom)
    await get_confirmation_rule(session, rid)

    res = await session.execute(
        select(AdminConfirmationRuleEnabled).where(AdminConfirmationRuleEnabled.rule_id == rid)
    )
    row = res.scalar_one_or_none()
    if row is None:
        row = AdminConfirmationRuleEnabled(rule_id=rid, enabled=enabled)
        session.add(row)
    else:
        row.enabled = enabled
        row.updated_at = _now_utc()
    await session.flush()
    return await get_confirmation_rule(session, rid)


async def seed_demo_custom_rules(session: AsyncSession) -> None:
    for demo in DEMO_CUSTOM_CONFIRMATION_RULES:
        res = await session.execute(
            select(AdminConfirmationRuleCustom).where(
                AdminConfirmationRuleCustom.rule_id == demo["id"]
            )
        )
        if res.scalar_one_or_none() is not None:
            continue
        session.add(
            AdminConfirmationRuleCustom(
                rule_id=demo["id"],
                title=demo["title"],
                summary=demo["summary"],
                risk_level=demo["riskLevel"],
                action=demo["action"],
                scenarios_json=json.dumps(demo["scenarios"], ensure_ascii=False),
                trigger_conditions_json=json.dumps(demo["triggerConditions"], ensure_ascii=False),
                default_enabled=demo["defaultEnabled"],
                created_by="seed",
            )
        )
    await session.flush()


async def reset_confirmation_rules(session: AsyncSession) -> ConfirmationRuleResetResponse:
    await session.execute(delete(AdminConfirmationRuleCustom))
    await session.execute(delete(AdminConfirmationRuleEnabled))
    await session.flush()
    await seed_demo_custom_rules(session)
    listed = await list_confirmation_rules(session)
    return ConfirmationRuleResetResponse(
        items=listed.items,
        total=listed.total,
        enabledCount=listed.enabled_count,
    )


async def load_merged_enabled_rules(session: AsyncSession) -> list[tuple[ConfirmationRuleDefinition, bool]]:
    """Runtime: builtin + custom rules with resolved enabled flag."""
    overrides = await _load_enabled_overrides(session)
    custom_rows = await _load_custom_rules(session)
    out: list[tuple[ConfirmationRuleDefinition, bool]] = []

    for rule in BUILTIN_CONFIRMATION_RULES:
        enabled = _resolve_enabled(rule["id"], rule["defaultEnabled"], overrides)
        out.append((rule, enabled))

    for row in custom_rows:
        rule = _rule_def_from_custom_row(row)
        enabled = _resolve_enabled(rule["id"], rule["defaultEnabled"], overrides)
        out.append((rule, enabled))

    return out
