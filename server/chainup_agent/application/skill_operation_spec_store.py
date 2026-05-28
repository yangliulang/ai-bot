"""DB store for skill operation specs — Publish + effective read."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.application.runtime_skill_operation_spec import (
    EffectiveSkillOperationSpec,
    SkillOperationSpecSection,
    _sections_from_markdown,
    scenario_to_skill_id,
)
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.skill_operation_spec import (
    SkillOperationSpecPointer,
    SkillOperationSpecVersion,
)

_BUNDLE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "skill_specs" / "runtime-bundle.json"
)

_VERSION_PART_RE = re.compile(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:-(.+))?$")


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def _utc_iso(dt: datetime) -> str:
    return dt.astimezone(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compute_spec_digest(body_markdown: str) -> str:
    return hashlib.sha256(body_markdown.encode("utf-8")).hexdigest()


def _version_sort_key(version: str) -> tuple:
    v = version.strip()
    m = _VERSION_PART_RE.match(v.split("@", 1)[0])
    if not m:
        return (0, 0, 0, v)
    major = int(m.group(1) or 0)
    minor = int(m.group(2) or 0) if m.group(2) is not None else 0
    patch = int(m.group(3) or 0) if m.group(3) is not None else 0
    suffix = m.group(4) or ""
    return (major, minor, patch, suffix)


def version_greater_than(a: str, b: str) -> bool:
    return _version_sort_key(a) > _version_sort_key(b)


def infer_contract_complete(body_markdown: str) -> bool:
    body = body_markdown.strip()
    if len(body) < 200:
        return False
    return "## 1." in body or "## 1 " in body


def _etag_for(skill_id: str, skill_spec_version: str, spec_digest: str) -> str:
    short = spec_digest[:16] if spec_digest else "0"
    return f'"{short}-{skill_spec_version}"'


def _row_to_summary(
    ver: SkillOperationSpecVersion,
    *,
    pointer_version: str | None,
) -> dict[str, Any]:
    eff_ver = pointer_version or ver.skill_spec_version
    return {
        "skillId": ver.skill_id,
        "skillSpecVersion": eff_ver,
        "lifecycle": ver.lifecycle if ver.skill_spec_version == eff_ver else "DEPRECATED",
        "scenarioIds": [],
        "contractComplete": bool(ver.contract_complete),
        "specDigest": ver.spec_digest,
        "publishedAt": _utc_iso(ver.published_at),
    }


async def import_runtime_bundle(session: AsyncSession) -> int:
    if not _BUNDLE_PATH.is_file():
        return 0
    raw = json.loads(_BUNDLE_PATH.read_text(encoding="utf-8"))
    items = raw.get("items") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        return 0
    count = 0
    for it in items:
        if not isinstance(it, dict):
            continue
        skill_id = str(it.get("skillId") or "").strip()
        version = str(it.get("skillSpecVersion") or "").strip()
        body = str(it.get("bodyMarkdown") or "")
        if not skill_id or not version or not body.strip():
            continue
        digest = str(it.get("specDigest") or "").strip() or compute_spec_digest(body)
        lifecycle = str(it.get("lifecycle") or "PUBLISHED").strip().upper()
        if lifecycle != "PUBLISHED":
            continue
        await _upsert_published_version(
            session,
            skill_id=skill_id,
            skill_spec_version=version,
            body_markdown=body,
            spec_digest=digest,
            contract_complete=infer_contract_complete(body),
            source_git_ref=str(it.get("sourceGitRef") or "") or None,
            set_pointer=True,
        )
        count += 1
    await session.flush()
    return count


async def _upsert_published_version(
    session: AsyncSession,
    *,
    skill_id: str,
    skill_spec_version: str,
    body_markdown: str,
    spec_digest: str,
    contract_complete: bool,
    source_git_ref: str | None,
    set_pointer: bool,
) -> SkillOperationSpecVersion:
    existing = await session.get(
        SkillOperationSpecVersion,
        {"skill_id": skill_id, "skill_spec_version": skill_spec_version},
    )
    now = _utc_now()
    if existing is None:
        row = SkillOperationSpecVersion(
            skill_id=skill_id,
            skill_spec_version=skill_spec_version,
            lifecycle="PUBLISHED",
            body_markdown=body_markdown,
            spec_digest=spec_digest,
            published_at=now,
            source_git_ref=source_git_ref,
            contract_complete=contract_complete,
        )
        session.add(row)
    else:
        existing.lifecycle = "PUBLISHED"
        existing.body_markdown = body_markdown
        existing.spec_digest = spec_digest
        existing.published_at = now
        existing.source_git_ref = source_git_ref
        existing.contract_complete = contract_complete
        row = existing
    if set_pointer:
        ptr = await session.get(SkillOperationSpecPointer, skill_id)
        if ptr is None:
            session.add(
                SkillOperationSpecPointer(
                    skill_id=skill_id,
                    skill_spec_version=skill_spec_version,
                    updated_at=now,
                )
            )
        else:
            ptr.skill_spec_version = skill_spec_version
            ptr.updated_at = now
    return row


async def list_skill_specs(
    session: AsyncSession,
    *,
    lifecycle: str | None = None,
) -> list[dict[str, Any]]:
    ptr_res = await session.execute(select(SkillOperationSpecPointer))
    pointers = {p.skill_id: p for p in ptr_res.scalars().all()}
    if not pointers:
        return []
    out: list[dict[str, Any]] = []
    for skill_id, ptr in sorted(pointers.items()):
        ver = await session.get(
            SkillOperationSpecVersion,
            {"skill_id": skill_id, "skill_spec_version": ptr.skill_spec_version},
        )
        if ver is None:
            continue
        summary = _row_to_summary(ver, pointer_version=ptr.skill_spec_version)
        if lifecycle and summary["lifecycle"].upper() != lifecycle.strip().upper():
            continue
        out.append(summary)
    return out


async def get_skill_spec_summary(session: AsyncSession, skill_id: str) -> dict[str, Any] | None:
    kid = skill_id.strip()
    ptr = await session.get(SkillOperationSpecPointer, kid)
    if ptr is None:
        ver_res = await session.execute(
            select(SkillOperationSpecVersion)
            .where(SkillOperationSpecVersion.skill_id == kid)
            .order_by(SkillOperationSpecVersion.published_at.desc())
            .limit(1)
        )
        ver = ver_res.scalar_one_or_none()
        if ver is None:
            return None
        return _row_to_summary(ver, pointer_version=None)
    ver = await session.get(
        SkillOperationSpecVersion,
        {"skill_id": kid, "skill_spec_version": ptr.skill_spec_version},
    )
    if ver is None:
        return None
    return _row_to_summary(ver, pointer_version=ptr.skill_spec_version)


async def list_versions(session: AsyncSession, skill_id: str) -> dict[str, Any] | None:
    kid = skill_id.strip()
    res = await session.execute(
        select(SkillOperationSpecVersion)
        .where(SkillOperationSpecVersion.skill_id == kid)
        .order_by(SkillOperationSpecVersion.published_at.desc())
    )
    rows = list(res.scalars().all())
    if not rows:
        return None
    return {
        "skillId": kid,
        "items": [
            {
                "skillSpecVersion": r.skill_spec_version,
                "lifecycle": r.lifecycle,
                "publishedAt": _utc_iso(r.published_at),
            }
            for r in rows
        ],
    }


async def get_version_body(
    session: AsyncSession,
    skill_id: str,
    skill_spec_version: str,
) -> dict[str, Any] | None:
    row = await session.get(
        SkillOperationSpecVersion,
        {"skill_id": skill_id.strip(), "skill_spec_version": skill_spec_version.strip()},
    )
    if row is None:
        return None
    return {
        "skillId": row.skill_id,
        "skillSpecVersion": row.skill_spec_version,
        "bodyMarkdown": row.body_markdown,
        "specDigest": row.spec_digest,
        "sourceGitRef": row.source_git_ref,
    }


async def get_max_published_version(session: AsyncSession, skill_id: str) -> str | None:
    res = await session.execute(
        select(SkillOperationSpecVersion.skill_spec_version).where(
            SkillOperationSpecVersion.skill_id == skill_id.strip(),
            SkillOperationSpecVersion.lifecycle == "PUBLISHED",
        )
    )
    versions = [r[0] for r in res.all()]
    if not versions:
        return None
    return max(versions, key=_version_sort_key)


async def publish_skill_spec(
    session: AsyncSession,
    *,
    skill_id: str,
    skill_spec_version: str,
    body_markdown: str | None,
    spec_digest: str | None,
    source_git_ref: str | None,
) -> dict[str, Any]:
    kid = skill_id.strip()
    ver = skill_spec_version.strip()
    if not kid or not ver:
        raise AppError("VALIDATION_ERROR", "skillId 与 skillSpecVersion 必填", status_code=422)

    body = (body_markdown or "").strip()
    if not body:
        ptr = await session.get(SkillOperationSpecPointer, kid)
        if ptr:
            prev = await session.get(
                SkillOperationSpecVersion,
                {"skill_id": kid, "skill_spec_version": ptr.skill_spec_version},
            )
            if prev:
                body = prev.body_markdown
        if not body:
            bundle_item = _bundle_item(kid)
            body = str((bundle_item or {}).get("bodyMarkdown") or "")
    if not body.strip():
        raise AppError(
            "PROMPT_SKILL_CONTRACT_INCOMPLETE",
            "发布须提供 bodyMarkdown 全文",
            status_code=422,
        )

    if not infer_contract_complete(body):
        raise AppError(
            "PROMPT_SKILL_CONTRACT_INCOMPLETE",
            "技能规范未满足 contract-complete（须含 §1 且足够正文）",
            status_code=422,
        )

    max_ver = await get_max_published_version(session, kid)
    if max_ver and not version_greater_than(ver, max_ver):
        raise AppError(
            "PROMPT_SKILL_VERSION_ROLLBACK",
            f"skillSpecVersion 不可低于已发布版本（当前 {max_ver}）",
            status_code=400,
            details={"skillId": kid, "requestedVersion": ver, "maxPublishedVersion": max_ver},
        )

    digest = (spec_digest or "").strip() or compute_spec_digest(body)

    if max_ver:
        old_rows = await session.execute(
            select(SkillOperationSpecVersion).where(
                SkillOperationSpecVersion.skill_id == kid,
                SkillOperationSpecVersion.lifecycle == "PUBLISHED",
                SkillOperationSpecVersion.skill_spec_version != ver,
            )
        )
        for old in old_rows.scalars().all():
            old.lifecycle = "DEPRECATED"

    await _upsert_published_version(
        session,
        skill_id=kid,
        skill_spec_version=ver,
        body_markdown=body,
        spec_digest=digest,
        contract_complete=True,
        source_git_ref=source_git_ref,
        set_pointer=True,
    )
    await session.flush()
    return {
        "skillId": kid,
        "skillSpecVersion": ver,
        "lifecycle": "PUBLISHED",
        "specDigest": digest,
    }


def _bundle_item(skill_id: str) -> dict[str, Any] | None:
    if not _BUNDLE_PATH.is_file():
        return None
    raw = json.loads(_BUNDLE_PATH.read_text(encoding="utf-8"))
    for it in raw.get("items") or []:
        if isinstance(it, dict) and str(it.get("skillId") or "").strip() == skill_id:
            return it
    return None


async def get_published_version_row(
    session: AsyncSession,
    skill_id: str,
    skill_spec_version: str,
) -> SkillOperationSpecVersion | None:
    row = await session.get(
        SkillOperationSpecVersion,
        {"skill_id": skill_id.strip(), "skill_spec_version": skill_spec_version.strip()},
    )
    if row is None or row.lifecycle != "PUBLISHED":
        return None
    return row


async def get_effective_from_db(
    session: AsyncSession,
    *,
    skill_id: str,
    skill_spec_version: str | None = None,
    scenario_id: str | None = None,
) -> EffectiveSkillOperationSpec:
    kid = skill_id.strip()
    if not kid:
        raise AppError("VALIDATION_ERROR", "skillId 不能为空", status_code=422)

    if scenario_id:
        mapped = scenario_to_skill_id(scenario_id)
        if mapped and mapped != kid:
            raise AppError(
                "PROMPT_SKILL_REF_INVALID",
                f"scenarioId 与 skillId 不匹配（期望 {mapped}）",
                status_code=403,
            )

    ver_key = (skill_spec_version or "").strip()
    if not ver_key:
        ptr = await session.get(SkillOperationSpecPointer, kid)
        if ptr is None:
            raise AppError(
                "PROMPT_SKILL_REF_INVALID",
                f"未找到已发布的技能操作规范：{kid}",
                status_code=404,
            )
        ver_key = ptr.skill_spec_version

    row = await get_published_version_row(session, kid, ver_key)
    if row is None:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            "技能操作规范未发布或版本无效",
            status_code=403,
        )

    return EffectiveSkillOperationSpec(
        skill_id=kid,
        skill_spec_version=row.skill_spec_version,
        spec_digest=row.spec_digest,
        lifecycle="PUBLISHED",
        scenario_id=scenario_id.strip() if scenario_id and scenario_id.strip() else None,
        sections=_sections_from_markdown(row.body_markdown),
    )


async def get_effective_body_response(
    session: AsyncSession,
    *,
    skill_id: str,
    skill_spec_version: str,
    if_none_match: str | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    row = await get_published_version_row(session, skill_id, skill_spec_version)
    if row is None:
        raise AppError(
            "PROMPT_SKILL_REF_INVALID",
            "技能操作规范未发布或版本无效",
            status_code=403,
        )
    etag = _etag_for(row.skill_id, row.skill_spec_version, row.spec_digest)
    if if_none_match and if_none_match.strip().strip('"') == etag.strip('"'):
        return None, etag
    return {
        "skillId": row.skill_id,
        "skillSpecVersion": row.skill_spec_version,
        "bodyMarkdown": row.body_markdown,
        "specDigest": row.spec_digest,
        "etag": etag,
    }, etag
