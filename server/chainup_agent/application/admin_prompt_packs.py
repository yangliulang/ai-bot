"""Admin Prompt Management — list/read/patch, drafts, publish, fork, versions, rollback."""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.agent_prompt_effective import (
    PROMPT_BODY_MAX_BYTES,
    _sha_etag,
    messages_json_byte_length,
    pack_messages_or_empty,
    patch_prompt_pack_messages,
)
from chainup_agent.application.agent_scenario_catalog import (
    flow_by_scenario_id,
    registered_scenario_ids,
)
from chainup_agent.application.prompt_placeholder_validation import (
    validate_prompt_messages_placeholders_with_schema,
)
from chainup_agent.application.prompt_safety_phrase_validation import (
    SAFETY_PHRASE_BLOCKLIST_REVISION,
    validate_messages_safety_phrases,
)
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.admin_prompt_pack import AdminPromptPack
from chainup_agent.infrastructure.persistence.models.admin_prompt_pack_version_event import (
    AdminPromptPackVersionEvent,
)

_VALID_TYPES = frozenset({"SYSTEM", "TRADING", "ANALYSIS", "SAFETY"})
_ID_SAFE = re.compile(r"^[a-zA-Z0-9._-]+$")
_FORK_SOURCE_LIFECYCLES = frozenset({"DRAFT", "PUBLISHED", "LOCKED", "DEPRECATED"})

_PROMPT_PACK_TYPE_ZH: dict[str, str] = {
    "SYSTEM": "系统",
    "TRADING": "交易",
    "ANALYSIS": "分析",
    "SAFETY": "安全防护",
}

# ``agent.runtime.*`` 不在 orchestration 寄存器；与控制台 shortLabel / 产品 mock 对齐
_AGENT_RUNTIME_SCENARIO_TITLES: dict[str, str] = {
    "agent.runtime.platform_system": "平台 SYSTEM 内核",
    "agent.runtime.platform_safety": "平台 SAFETY 护栏",
    "agent.runtime.runtime_clarify": "运行时澄清（pp-runtime-clarify）",
    "agent.runtime.runtime_output_contract": "运行时输出契约（pp-runtime-output-contract）",
    "agent.runtime.analysis_core": "统一分析包（pp-analysis-core）",
    "agent.runtime.intent_nlu": "意图 NLU 系统包",
}


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


def check_prompt_pack_row_version(row: AdminPromptPack, if_match: str | None) -> None:
    """PM-C03 — optional If-Match against ``row_version``."""
    expect = _normalize_if_match(if_match)
    if expect is None:
        return
    if expect != str(row.row_version):
        raise AppError(
            code="AGENT_PROMPT_PACK_VERSION_CONFLICT",
            message="资源已被他人更新，请刷新后重试（If-Match / rowVersion 不一致）。",
            status_code=409,
            details={"expectedVersion": expect, "currentVersion": str(row.row_version)},
        )


def _messages_body_markdown(messages: list[dict[str, Any]]) -> str:
    if not messages:
        return ""
    sys_idx = next(
        (i for i, m in enumerate(messages) if isinstance(m, dict) and m.get("role") == "system"),
        0,
    )
    row = messages[sys_idx] if sys_idx < len(messages) else None
    if isinstance(row, dict) and isinstance(row.get("content"), str):
        return row["content"]
    return ""


def _variable_schema_out(row: AdminPromptPack) -> dict[str, Any] | None:
    raw = row.variable_schema_json
    if raw is None or not str(raw).strip():
        return None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def resolve_prompt_pack_title(row: AdminPromptPack) -> str:
    """运营可见展示名（config §3 ``title``；列表「Prompt 名称」列 · 原型 ``MockPromptPack.title``）。"""
    sid = (row.scenario_id or "").strip()
    lc = (row.lifecycle or "").upper()
    base: str | None = None

    if sid:
        flow = flow_by_scenario_id(sid)
        if flow is not None:
            base = flow.title
        else:
            base = _AGENT_RUNTIME_SCENARIO_TITLES.get(sid)

    if base is None and row.prompt_pack_id.startswith("pack_draft_"):
        ptype_zh = _PROMPT_PACK_TYPE_ZH.get(row.prompt_pack_type, row.prompt_pack_type)
        suffix = row.prompt_pack_id.removeprefix("pack_draft_")[:8]
        base = f"{ptype_zh}草稿" + (f" · {suffix}" if suffix else "")

    if base is None:
        if row.prompt_pack_type == "SYSTEM":
            base = "系统 Prompt 包"
        elif row.prompt_pack_type == "SAFETY":
            base = "安全防护包"
        elif row.prompt_pack_type == "ANALYSIS":
            base = "分析 Prompt 包"
        elif row.prompt_pack_type == "TRADING":
            base = "交易 Prompt 包"
        else:
            base = row.prompt_pack_id

    if lc == "DRAFT" and "草稿" not in base:
        base = f"{base}（草稿）"
    return base


def pack_to_summary_dict(row: AdminPromptPack) -> dict[str, Any]:
    return {
        "promptPackId": row.prompt_pack_id,
        "promptPackType": row.prompt_pack_type,
        "scenarioId": row.scenario_id,
        "title": resolve_prompt_pack_title(row),
        "promptPackVersion": row.prompt_pack_version,
        "lifecycle": row.lifecycle,
        "etag": row.etag,
        "updatedAt": _utc_now_iso() if row.updated_at is None else row.updated_at.isoformat().replace("+00:00", "Z"),
        "rowVersion": int(row.row_version),
    }


def pack_to_detail_dict(row: AdminPromptPack) -> dict[str, Any]:
    sid = (row.scenario_id or "").strip() or row.prompt_pack_id
    msgs = pack_messages_or_empty(row)
    return {
        "promptPackId": row.prompt_pack_id,
        "promptPackType": row.prompt_pack_type,
        "scenarioId": row.scenario_id,
        "title": resolve_prompt_pack_title(row),
        "promptPackVersion": row.prompt_pack_version,
        "lifecycle": row.lifecycle,
        "etag": row.etag,
        "rowVersion": int(row.row_version),
        "updatedAt": _utc_now_iso() if row.updated_at is None else row.updated_at.isoformat().replace("+00:00", "Z"),
        "placeholderDenylistRevision": row.placeholder_denylist_revision,
        "safetyPhraseBlocklistRevision": row.safety_phrase_blocklist_revision,
        "messages": msgs,
        "bodyMarkdown": _messages_body_markdown(msgs),
        "variableSchema": _variable_schema_out(row),
        "resolvedPromptBinding": {
            "scenarioId": sid,
            "sessionId": None,
            "systemPromptPackId": row.prompt_pack_id if row.prompt_pack_type == "SYSTEM" else None,
            "systemPromptPackVersion": row.prompt_pack_version
            if row.prompt_pack_type == "SYSTEM"
            else None,
            "safetyPromptPackId": row.prompt_pack_id if row.prompt_pack_type == "SAFETY" else None,
            "safetyPromptPackVersion": row.prompt_pack_version
            if row.prompt_pack_type == "SAFETY"
            else None,
            "tradingPromptPackId": row.prompt_pack_id
            if row.prompt_pack_type in ("TRADING", "ANALYSIS")
            else None,
            "tradingPromptPackVersion": row.prompt_pack_version
            if row.prompt_pack_type in ("TRADING", "ANALYSIS")
            else None,
            "fewShotDigest": None,
            "placeholderDenylistRevision": row.placeholder_denylist_revision,
            "safetyPhraseBlocklistRevision": row.safety_phrase_blocklist_revision,
        },
    }


def _assert_messages_size(messages: list[dict[str, Any]]) -> None:
    n = messages_json_byte_length(messages)
    if n > PROMPT_BODY_MAX_BYTES:
        raise AppError(
            code="PROMPT_BODY_TOO_LARGE",
            message=f"messages 序列化后超过上限 {PROMPT_BODY_MAX_BYTES} 字节（当前 {n}）。",
            status_code=400,
            details={"maxBytes": PROMPT_BODY_MAX_BYTES, "actualBytes": n},
        )


def _assert_pack_type(t: str) -> str:
    u = t.strip().upper()
    if u not in _VALID_TYPES:
        raise AppError(
            code="VALIDATION_ERROR",
            message=f"无效的 promptPackType：{t!r}；须为 SYSTEM / TRADING / ANALYSIS / SAFETY。",
            status_code=422,
            details={"field": "promptPackType"},
        )
    return u


def _lifecycle_upper(row: AdminPromptPack) -> str:
    return (row.lifecycle or "").strip().upper()


def assert_prompt_pack_messages_mutable(row: AdminPromptPack) -> None:
    """SC-PM-01 / FR-PM02：LOCKED 与下线态禁止原位改 messages；

    DRAFT / PUBLISHED（非 LOCKED）可写。
    """
    lc = _lifecycle_upper(row)
    if lc == "LOCKED":
        raise AppError(
            code="PROMPT_PACK_LOCKED",
            message="该 Prompt 包已锁定（LOCKED），禁止原位修改正文；请新建草稿版本线后发布。",
            status_code=409,
            details={"promptPackId": row.prompt_pack_id},
        )
    if lc in ("DEPRECATED", "DISABLED"):
        raise AppError(
            code="PROMPT_PACK_DEPRECATED",
            message="该 Prompt 包已下线或停用，禁止修改。",
            status_code=409,
            details={"promptPackId": row.prompt_pack_id, "lifecycle": row.lifecycle},
        )


async def list_prompt_packs(
    session: AsyncSession,
    *,
    prompt_pack_type: str | None = None,
    scenario_id: str | None = None,
    lifecycle: str | None = None,
) -> list[AdminPromptPack]:
    stmt = select(AdminPromptPack).order_by(AdminPromptPack.prompt_pack_id.asc())
    if prompt_pack_type and prompt_pack_type.strip():
        stmt = stmt.where(
            AdminPromptPack.prompt_pack_type == prompt_pack_type.strip().upper(),
        )
    if scenario_id and scenario_id.strip():
        stmt = stmt.where(AdminPromptPack.scenario_id == scenario_id.strip())
    if lifecycle and lifecycle.strip():
        stmt = stmt.where(
            AdminPromptPack.lifecycle == lifecycle.strip().upper(),
        )
    return list((await session.scalars(stmt)).all())


async def get_prompt_pack(session: AsyncSession, prompt_pack_id: str) -> AdminPromptPack | None:
    return await session.get(AdminPromptPack, prompt_pack_id.strip())


def _validate_prompt_pack_id_field(prompt_pack_id: str) -> str:
    pid = prompt_pack_id.strip()
    if len(pid) > 128 or not _ID_SAFE.match(pid):
        raise AppError(
            code="VALIDATION_ERROR",
            message="promptPackId 须为 1～128 字符，仅含字母数字与 ._-",
            status_code=422,
            details={"field": "promptPackId"},
        )
    return pid


def _resolve_new_draft_pack_id(
    *,
    prompt_pack_id: str | None,
    scenario_id: str | None,
    source_pack_id: str | None,
) -> str:
    if prompt_pack_id and prompt_pack_id.strip():
        return _validate_prompt_pack_id_field(prompt_pack_id)
    if scenario_id:
        slug = scenario_id.replace(".", "_").replace("/", "_")[:72]
        return f"pack_{slug}_{uuid.uuid4().hex[:8]}"
    if source_pack_id:
        base = re.sub(r"[^a-zA-Z0-9._-]", "_", source_pack_id)[:72]
        return f"{base}_fork_{uuid.uuid4().hex[:8]}"
    return f"pack_draft_{uuid.uuid4().hex[:12]}"


def _assert_scenario_for_pack_type(ptype: str, scenario_id: str | None) -> str | None:
    """Create/publish rules for ``scenarioId`` vs ``PromptPackType``."""
    sid = (scenario_id or "").strip() or None
    if ptype in ("TRADING", "ANALYSIS"):
        if not sid:
            raise AppError(
                code="VALIDATION_ERROR",
                message=f"{ptype} 类草稿创建须填写 scenarioId（与编排场景寄存器对齐）。",
                status_code=422,
                details={"field": "scenarioId", "promptPackType": ptype},
            )
        if sid not in registered_scenario_ids():
            raise AppError(
                code="PROMPT_SCENARIO_INVALID",
                message=(
                    f"scenarioId {sid!r} 不在当前场景寄存器中；"
                    "请从 GET /api/v1/agent/scenarios 选择有效场景。"
                ),
                status_code=422,
                details={"scenarioId": sid},
            )
    elif sid and sid not in registered_scenario_ids():
        raise AppError(
            code="PROMPT_SCENARIO_INVALID",
            message=(
                f"scenarioId {sid!r} 不在当前场景寄存器中；"
                "请从 GET /api/v1/agent/scenarios 选择有效场景。"
            ),
            status_code=422,
            details={"scenarioId": sid},
        )
    return sid


def _default_draft_messages(ptype: str, scenario_id: str | None) -> list[dict[str, Any]]:
    lines = [
        f"你是 ChainUp AI Agent 的 {ptype} 类提示词包（草稿）。",
        "请在此编写 system 正文；发布前须通过占位符与安全用语校验。",
    ]
    if scenario_id:
        flow = flow_by_scenario_id(scenario_id)
        if flow is not None:
            lines.append(f"\n绑定场景：{flow.title}（{scenario_id}）")
            if flow.prompt_binding_hint:
                lines.append(flow.prompt_binding_hint)
            elif flow.flow_summary:
                lines.append(f"执行流程：{flow.flow_summary}")
        else:
            lines.append(f"\n绑定场景 ID：{scenario_id}")
    return [{"role": "system", "content": "\n".join(lines)}]


async def create_draft_prompt_pack(
    session: AsyncSession,
    *,
    prompt_pack_type: str,
    scenario_id: str | None,
    prompt_pack_id: str | None,
    source_prompt_pack_id: str | None = None,
) -> AdminPromptPack:
    """
    Create a DRAFT line: blank (default system stub) or clone from ``sourcePromptPackId``.

    Aligns with product ``/prompts/strategy`` ·「新建草稿」：空白 / 从模板复制。
    """
    ptype = _assert_pack_type(prompt_pack_type)
    sid = _assert_scenario_for_pack_type(ptype, scenario_id)
    src_id = (source_prompt_pack_id or "").strip() or None

    if src_id:
        pid = _resolve_new_draft_pack_id(
            prompt_pack_id=prompt_pack_id,
            scenario_id=sid,
            source_pack_id=src_id,
        )
        if await session.get(AdminPromptPack, pid):
            raise AppError(
                code="AGENT_PROMPT_PACK_ID_CONFLICT",
                message="promptPackId 已存在。",
                status_code=409,
                details={"promptPackId": pid},
            )
        row = await fork_prompt_pack_from_source(
            session,
            source_prompt_pack_id=src_id,
            new_prompt_pack_id=pid,
        )
        row.prompt_pack_type = ptype
        row.scenario_id = sid
        msgs = pack_messages_or_empty(row)
        row.etag = _sha_etag(msgs)
        await session.flush()
        return row

    pid = _resolve_new_draft_pack_id(
        prompt_pack_id=prompt_pack_id,
        scenario_id=sid,
        source_pack_id=None,
    )
    if await session.get(AdminPromptPack, pid):
        raise AppError(
            code="AGENT_PROMPT_PACK_ID_CONFLICT",
            message="promptPackId 已存在。",
            status_code=409,
            details={"promptPackId": pid},
        )

    default_messages = _default_draft_messages(ptype, sid)
    _assert_messages_size(default_messages)
    row = AdminPromptPack(
        prompt_pack_id=pid,
        prompt_pack_type=ptype,
        scenario_id=sid,
        lifecycle="DRAFT",
        prompt_pack_version="1",
        etag=_sha_etag(default_messages),
        messages_json=json.dumps(default_messages, ensure_ascii=False),
        placeholder_denylist_revision="rev0",
        safety_phrase_blocklist_revision=SAFETY_PHRASE_BLOCKLIST_REVISION,
    )
    session.add(row)
    await session.flush()
    return row


async def patch_messages(
    session: AsyncSession,
    *,
    prompt_pack_id: str,
    messages: list[dict[str, Any]] | None = None,
    variable_schema: dict[str, Any] | None = None,
    if_match: str | None = None,
) -> AdminPromptPack | None:
    row = await get_prompt_pack(session, prompt_pack_id)
    if row is None:
        return None
    check_prompt_pack_row_version(row, if_match)
    assert_prompt_pack_messages_mutable(row)

    if variable_schema is not None:
        row.variable_schema_json = json.dumps(variable_schema, ensure_ascii=False, sort_keys=True)
        row.row_version = int(row.row_version) + 1

    schema_raw = row.variable_schema_json

    if messages is not None:
        _assert_messages_size(messages)
        extra = await _safety_scan_extra_for_publish(session, ptype=row.prompt_pack_type)
        _apply_safety_phrase_check(messages, extra_scan_text=extra)
        validate_prompt_messages_placeholders_with_schema(
            messages,
            variable_schema_json=schema_raw,
            field_label="messages",
        )
        return await patch_prompt_pack_messages(
            session,
            prompt_pack_id=prompt_pack_id,
            messages=messages,
            bump_version=True,
        )

    if variable_schema is not None:
        msgs_preview = pack_messages_or_empty(row)
        extra = await _safety_scan_extra_for_publish(session, ptype=row.prompt_pack_type)
        _apply_safety_phrase_check(msgs_preview, extra_scan_text=extra)
        validate_prompt_messages_placeholders_with_schema(
            msgs_preview,
            variable_schema_json=schema_raw,
            field_label="messages",
        )
        await session.flush()
        return row

    return row


async def _deprecate_other_published_safety_same_scenario(
    session: AsyncSession,
    *,
    scenario_id: str | None,
    keep_pack_id: str,
) -> None:
    stmt = select(AdminPromptPack).where(
        AdminPromptPack.prompt_pack_type == "SAFETY",
        AdminPromptPack.lifecycle == "PUBLISHED",
        AdminPromptPack.prompt_pack_id != keep_pack_id,
    )
    if scenario_id and scenario_id.strip():
        stmt = stmt.where(AdminPromptPack.scenario_id == scenario_id.strip())
    res = await session.execute(stmt)
    for other in res.scalars().all():
        other.lifecycle = "DEPRECATED"


async def _safety_scan_extra_for_publish(
    session: AsyncSession,
    *,
    ptype: str,
) -> str | None:
    if ptype not in ("TRADING", "ANALYSIS", "SAFETY", "SYSTEM"):
        return None
    from chainup_agent.application.admin_prompt_safety import load_full_pack_scan_extra_text

    return await load_full_pack_scan_extra_text(session)


def _apply_safety_phrase_check(
    messages: list[dict[str, Any]],
    *,
    extra_scan_text: str | None,
) -> None:
    validate_messages_safety_phrases(messages, extra_scan_text=extra_scan_text)


async def _deprecate_other_published_same_scenario(
    session: AsyncSession,
    *,
    scenario_id: str,
    keep_pack_id: str,
    pack_types: tuple[str, ...],
) -> None:
    stmt = select(AdminPromptPack).where(
        AdminPromptPack.scenario_id == scenario_id,
        AdminPromptPack.lifecycle.in_(("PUBLISHED", "LOCKED")),
        AdminPromptPack.prompt_pack_type.in_(pack_types),
        AdminPromptPack.prompt_pack_id != keep_pack_id,
    )
    res = await session.execute(stmt)
    for other in res.scalars().all():
        other.lifecycle = "DEPRECATED"


async def _record_version_event(
    session: AsyncSession,
    *,
    row: AdminPromptPack,
    event: str,
    summary: str | None = None,
    actor: str | None = None,
) -> None:
    session.add(
        AdminPromptPackVersionEvent(
            prompt_pack_id=row.prompt_pack_id,
            prompt_pack_version=row.prompt_pack_version,
            lifecycle=row.lifecycle,
            event=event,
            actor=actor,
            summary=summary,
            messages_json=row.messages_json,
            variable_schema_json=row.variable_schema_json,
        ),
    )


async def fork_prompt_pack_from_source(
    session: AsyncSession,
    *,
    source_prompt_pack_id: str,
    new_prompt_pack_id: str | None = None,
) -> AdminPromptPack:
    """Copy snapshot from LOCKED/PUBLISHED/DRAFT source into a new DRAFT version line."""
    src = await get_prompt_pack(session, source_prompt_pack_id)
    if src is None:
        raise AppError(
            code="AGENT_PROMPT_PACK_NOT_FOUND",
            message="未知的 source promptPackId。",
            status_code=404,
            details={"promptPackId": source_prompt_pack_id.strip()},
        )
    if _lifecycle_upper(src) not in _FORK_SOURCE_LIFECYCLES:
        raise AppError(
            code="PROMPT_FORK_INVALID_SOURCE",
            message="该包状态不可作为模板复制。",
            status_code=422,
            details={"promptPackId": src.prompt_pack_id, "lifecycle": src.lifecycle},
        )

    if new_prompt_pack_id and new_prompt_pack_id.strip():
        pid = new_prompt_pack_id.strip()
        if len(pid) > 128 or not _ID_SAFE.match(pid):
            raise AppError(
                code="VALIDATION_ERROR",
                message="promptPackId 须为 1～128 字符，仅含字母数字与 ._-",
                status_code=422,
                details={"field": "promptPackId"},
            )
    else:
        base = re.sub(r"[^a-zA-Z0-9._-]", "_", src.prompt_pack_id)[:72]
        pid = f"{base}_fork_{uuid.uuid4().hex[:8]}"

    if await session.get(AdminPromptPack, pid):
        raise AppError(
            code="AGENT_PROMPT_PACK_ID_CONFLICT",
            message="promptPackId 已存在。",
            status_code=409,
            details={"promptPackId": pid},
        )

    msgs = pack_messages_or_empty(src)
    _assert_messages_size(msgs)
    row = AdminPromptPack(
        prompt_pack_id=pid,
        prompt_pack_type=src.prompt_pack_type,
        scenario_id=src.scenario_id,
        lifecycle="DRAFT",
        prompt_pack_version="1",
        etag=_sha_etag(msgs),
        messages_json=src.messages_json,
        variable_schema_json=src.variable_schema_json,
        placeholder_denylist_revision=src.placeholder_denylist_revision,
        safety_phrase_blocklist_revision=src.safety_phrase_blocklist_revision,
    )
    session.add(row)
    await session.flush()
    return row


async def list_prompt_pack_versions(
    session: AsyncSession,
    *,
    prompt_pack_id: str,
) -> list[dict[str, Any]]:
    stmt = (
        select(AdminPromptPackVersionEvent)
        .where(AdminPromptPackVersionEvent.prompt_pack_id == prompt_pack_id.strip())
        .order_by(AdminPromptPackVersionEvent.published_at.desc(), AdminPromptPackVersionEvent.id.desc())
    )
    rows = list((await session.scalars(stmt)).all())
    return [
        {
            "promptPackVersion": r.prompt_pack_version,
            "publishedAt": r.published_at.isoformat().replace("+00:00", "Z"),
            "lifecycle": r.lifecycle,
            "event": r.event,
            "actor": r.actor,
            "summary": r.summary,
        }
        for r in rows
    ]


async def rollback_prompt_pack(
    session: AsyncSession,
    *,
    prompt_pack_id: str,
    target_version: str,
) -> AdminPromptPack | None:
    row = await get_prompt_pack(session, prompt_pack_id)
    if row is None:
        return None
    lc = _lifecycle_upper(row)
    if lc not in ("PUBLISHED", "LOCKED"):
        raise AppError(
            code="PROMPT_ROLLBACK_INVALID_STATE",
            message="仅已发布或已锁定的包可回滚；草稿请直接编辑。",
            status_code=422,
            details={"promptPackId": row.prompt_pack_id, "lifecycle": row.lifecycle},
        )

    ver = target_version.strip()
    stmt = (
        select(AdminPromptPackVersionEvent)
        .where(
            AdminPromptPackVersionEvent.prompt_pack_id == row.prompt_pack_id,
            AdminPromptPackVersionEvent.prompt_pack_version == ver,
        )
        .order_by(AdminPromptPackVersionEvent.id.desc())
        .limit(1)
    )
    snap = (await session.execute(stmt)).scalar_one_or_none()
    if snap is None:
        raise AppError(
            code="PROMPT_VERSION_NOT_FOUND",
            message=f"未找到 promptPackVersion={ver!r} 的历史快照。",
            status_code=404,
            details={"promptPackId": row.prompt_pack_id, "promptPackVersion": ver},
        )

    ptype = row.prompt_pack_type.upper()
    sid = (row.scenario_id or "").strip()

    row.messages_json = snap.messages_json
    row.variable_schema_json = snap.variable_schema_json
    row.etag = _sha_etag(pack_messages_or_empty(row))

    if ptype == "SYSTEM":
        row.lifecycle = "LOCKED"
        if sid:
            await _deprecate_other_published_same_scenario(
                session,
                scenario_id=sid,
                keep_pack_id=row.prompt_pack_id,
                pack_types=("SYSTEM",),
            )
    elif ptype in ("TRADING", "ANALYSIS"):
        row.lifecycle = "PUBLISHED"
        if sid:
            await _deprecate_other_published_same_scenario(
                session,
                scenario_id=sid,
                keep_pack_id=row.prompt_pack_id,
                pack_types=("TRADING", "ANALYSIS"),
            )
    elif ptype == "SAFETY":
        row.lifecycle = "PUBLISHED"
        await _deprecate_other_published_safety_same_scenario(
            session,
            scenario_id=sid or None,
            keep_pack_id=row.prompt_pack_id,
        )

    try:
        max_stmt = (
            select(AdminPromptPackVersionEvent.prompt_pack_version)
            .where(AdminPromptPackVersionEvent.prompt_pack_id == row.prompt_pack_id)
        )
        max_ver = 0
        for vrow in (await session.execute(max_stmt)).scalars().all():
            try:
                max_ver = max(max_ver, int(str(vrow)))
            except ValueError:
                pass
        try:
            max_ver = max(max_ver, int(str(row.prompt_pack_version)))
        except ValueError:
            pass
        row.prompt_pack_version = str(max_ver + 1)
    except ValueError:
        row.prompt_pack_version = f"{row.prompt_pack_version}.rb"

    row.row_version = int(row.row_version) + 1
    row.safety_phrase_blocklist_revision = SAFETY_PHRASE_BLOCKLIST_REVISION
    await session.flush()
    await _record_version_event(
        session,
        row=row,
        event="ROLLBACK",
        summary=f"Rollback to v{ver}",
    )
    return row


async def publish_prompt_pack(
    session: AsyncSession, *, prompt_pack_id: str
) -> AdminPromptPack | None:
    row = await get_prompt_pack(session, prompt_pack_id)
    if row is None:
        return None
    lc = _lifecycle_upper(row)
    if lc != "DRAFT":
        raise AppError(
            code="PROMPT_PUBLISH_INVALID_STATE",
            message="仅 lifecycle=DRAFT 的包可执行发布。",
            status_code=422,
            details={"promptPackId": row.prompt_pack_id, "lifecycle": row.lifecycle},
        )

    msgs_preview = pack_messages_or_empty(row)
    ptype = row.prompt_pack_type.upper()
    extra = await _safety_scan_extra_for_publish(session, ptype=ptype)
    try:
        _apply_safety_phrase_check(msgs_preview, extra_scan_text=extra)
    except AppError as exc:
        from chainup_agent.application.admin_prompt_safety import log_prompt_publish_blocked

        if exc.code == "PROMPT_SAFETY_VIOLATION":
            details = exc.details or {}
            await log_prompt_publish_blocked(
                session,
                prompt_pack_id=row.prompt_pack_id,
                matched_rule_id=str(details.get("matchedRuleId") or ""),
                reason=exc.message,
            )
        raise
    validate_prompt_messages_placeholders_with_schema(
        msgs_preview,
        variable_schema_json=row.variable_schema_json,
        field_label="messages",
    )

    from chainup_agent.application.skill_operation_spec_publish_gate import (
        assert_skill_spec_ref_publishable,
    )

    await assert_skill_spec_ref_publishable(session, row)

    sid = (row.scenario_id or "").strip()

    if ptype in ("TRADING", "ANALYSIS"):
        sid = _assert_scenario_for_pack_type(ptype, sid or None)
        await _deprecate_other_published_same_scenario(
            session,
            scenario_id=sid,
            keep_pack_id=row.prompt_pack_id,
            pack_types=("TRADING", "ANALYSIS"),
        )
        row.lifecycle = "PUBLISHED"
    elif ptype == "SYSTEM":
        sid = (row.scenario_id or "").strip()
        if sid:
            await _deprecate_other_published_same_scenario(
                session,
                scenario_id=sid,
                keep_pack_id=row.prompt_pack_id,
                pack_types=("SYSTEM",),
            )
        row.lifecycle = "LOCKED"
    elif ptype == "SAFETY":
        sid = (row.scenario_id or "").strip() or None
        await _deprecate_other_published_safety_same_scenario(
            session,
            scenario_id=sid,
            keep_pack_id=row.prompt_pack_id,
        )
        row.lifecycle = "PUBLISHED"
    else:
        raise AppError(
            code="VALIDATION_ERROR",
            message=f"无法发布未知类型：{row.prompt_pack_type}",
            status_code=422,
        )

    try:
        v = int(str(row.prompt_pack_version)) + 1
        row.prompt_pack_version = str(v)
    except ValueError:
        row.prompt_pack_version = f"{row.prompt_pack_version}.1"

    msgs = pack_messages_or_empty(row)
    row.messages_json = json.dumps(msgs, ensure_ascii=False)
    row.etag = _sha_etag(msgs)
    row.safety_phrase_blocklist_revision = SAFETY_PHRASE_BLOCKLIST_REVISION
    row.placeholder_denylist_revision = row.placeholder_denylist_revision or "rev0"
    row.row_version = int(row.row_version) + 1

    await _record_version_event(
        session,
        row=row,
        event="PUBLISH",
        summary=f"Published as {row.lifecycle}",
    )
    await session.flush()
    return row


# re-export for tests / router
__all__ = [
    "check_prompt_pack_row_version",
    "create_draft_prompt_pack",
    "fork_prompt_pack_from_source",
    "get_prompt_pack",
    "list_prompt_pack_versions",
    "list_prompt_packs",
    "pack_to_detail_dict",
    "pack_to_summary_dict",
    "patch_messages",
    "publish_prompt_pack",
    "rollback_prompt_pack",
]
