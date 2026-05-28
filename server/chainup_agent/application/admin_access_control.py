"""Admin access-control persistence + eligibility helpers (FR-MC602/603/607)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.admin_access_control import (
    BanCreateRequest,
    BanItem,
    BanListResponse,
    MinVipTierResponse,
    RolloutPolicyResponse,
    WhitelistCreateRequest,
    WhitelistEntryItem,
    WhitelistListResponse,
)
from chainup_agent.core.errors import AppError
from chainup_agent.infrastructure.persistence.models.admin_access_ban import AdminAccessUserBan
from chainup_agent.infrastructure.persistence.models.admin_access_membership_policy import (
    AdminAccessMembershipPolicy,
)
from chainup_agent.infrastructure.persistence.models.admin_access_whitelist import (
    AdminAccessWhitelistEntry,
)
from chainup_agent.infrastructure.persistence.models.agent_instance import AgentInstance

_POLICY_ROW_ID = 1


def _ban_reason_to_envelope_code(reason_code: str) -> str:
    if reason_code == "COMPLIANCE_ABUSE":
        return "AGENT_COMPLIANCE_RESTRICTED"
    return "AGENT_USER_BLOCKED"


def _now_utc() -> datetime:
    return datetime.now(UTC)


async def get_policy_row(session: AsyncSession) -> AdminAccessMembershipPolicy:
    res = await session.execute(
        select(AdminAccessMembershipPolicy).where(AdminAccessMembershipPolicy.id == _POLICY_ROW_ID)
    )
    row = res.scalar_one_or_none()
    if row is None:
        row = AdminAccessMembershipPolicy(
            id=_POLICY_ROW_ID,
            min_vip_tier=0,
            enforce_rollout_whitelist=False,
        )
        session.add(row)
        await session.flush()
    return row


async def list_whitelist(session: AsyncSession, *, list_id: str | None, q: str | None) -> WhitelistListResponse:
    stmt = select(AdminAccessWhitelistEntry).order_by(AdminAccessWhitelistEntry.created_at.desc())
    if list_id and list_id.strip():
        stmt = stmt.where(AdminAccessWhitelistEntry.list_id == list_id.strip())
    res = await session.execute(stmt)
    rows = list(res.scalars().all())
    if q and q.strip():
        qq = q.strip().lower()
        rows = [
            r
            for r in rows
            if qq in r.list_id.lower()
            or qq in r.user_uid.lower()
            or qq in (r.user_id_masked or "").lower()
            or (r.note and qq in r.note.lower())
        ]
    items = [
        WhitelistEntryItem(
            entryId=r.entry_id,
            listId=r.list_id,
            userUid=r.user_uid,
            userIdMasked=r.user_id_masked,
            note=r.note,
            addedAt=r.created_at,
            addedBy=r.created_by,
        )
        for r in rows
    ]
    return WhitelistListResponse(items=items, total=len(items))


async def create_whitelist_entry(
    session: AsyncSession,
    body: WhitelistCreateRequest,
    *,
    actor: str,
) -> WhitelistEntryItem:
    masked = (body.user_id_masked or body.user_uid).strip()
    uid = body.user_uid.strip()
    lid = body.list_id.strip()
    entry_id = f"wle_{uuid.uuid4().hex[:22]}"
    row = AdminAccessWhitelistEntry(
        entry_id=entry_id,
        list_id=lid,
        user_uid=uid,
        user_id_masked=masked,
        note=(body.note.strip() if body.note else None) or None,
        created_by=actor[:128],
    )
    session.add(row)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        raise AppError(
            code="AGENT_ADMIN_ACCESS_WHITELIST_DUPLICATE",
            message="该名单下已存在相同 userUid 的白名单条目。",
            status_code=409,
            details={"listId": lid, "userUid": uid},
        ) from exc
    return WhitelistEntryItem(
        entryId=row.entry_id,
        listId=row.list_id,
        userUid=row.user_uid,
        userIdMasked=row.user_id_masked,
        note=row.note,
        addedAt=row.created_at,
        addedBy=row.created_by,
    )


async def delete_whitelist_entry(session: AsyncSession, entry_id: str) -> None:
    res = await session.execute(
        select(AdminAccessWhitelistEntry).where(AdminAccessWhitelistEntry.entry_id == entry_id.strip())
    )
    row = res.scalar_one_or_none()
    if row is None:
        raise AppError(
            code="AGENT_ADMIN_ACCESS_WHITELIST_NOT_FOUND",
            message="白名单条目不存在。",
            status_code=404,
        )
    await session.delete(row)


async def list_bans(session: AsyncSession, *, q: str | None) -> BanListResponse:
    stmt = select(AdminAccessUserBan).order_by(AdminAccessUserBan.created_at.desc())
    res = await session.execute(stmt)
    rows = list(res.scalars().all())
    if q and q.strip():
        qq = q.strip().lower()
        rows = [
            r
            for r in rows
            if qq in r.ban_id.lower()
            or qq in r.user_uid.lower()
            or qq in r.reason_code.lower()
        ]
    items = [
        BanItem(
            banId=r.ban_id,
            userUid=r.user_uid,
            reasonCode=r.reason_code,
            scope=r.scope,
            expiresAt=r.expires_at,
            linkedPause=r.linked_pause,
            createdAt=r.created_at,
            createdBy=r.created_by,
        )
        for r in rows
    ]
    return BanListResponse(items=items, total=len(items))


async def _maybe_pause_binding_instance(session: AsyncSession, user_uid: str) -> None:
    if not user_uid.isdigit():
        return
    tid = int(user_uid)
    await session.execute(
        update(AgentInstance)
        .where(AgentInstance.telegram_user_id == tid)
        .values(runtime_state="PAUSED")
    )


async def create_ban(
    session: AsyncSession,
    body: BanCreateRequest,
    *,
    actor: str,
) -> BanItem:
    ban_id = f"ban_{uuid.uuid4().hex[:22]}"
    row = AdminAccessUserBan(
        ban_id=ban_id,
        user_uid=body.user_uid.strip(),
        reason_code=body.reason_code.strip(),
        scope=(body.scope or "AGENT_PRODUCT").strip()[:32],
        expires_at=body.expires_at,
        linked_pause=body.linked_pause,
        created_by=actor[:128],
    )
    session.add(row)
    await session.flush()
    if body.linked_pause:
        await _maybe_pause_binding_instance(session, row.user_uid)
    return BanItem(
        banId=row.ban_id,
        userUid=row.user_uid,
        reasonCode=row.reason_code,
        scope=row.scope,
        expiresAt=row.expires_at,
        linkedPause=row.linked_pause,
        createdAt=row.created_at,
        createdBy=row.created_by,
    )


async def delete_ban(session: AsyncSession, ban_id: str) -> None:
    res = await session.execute(select(AdminAccessUserBan).where(AdminAccessUserBan.ban_id == ban_id.strip()))
    row = res.scalar_one_or_none()
    if row is None:
        raise AppError(
            code="AGENT_ADMIN_ACCESS_BAN_NOT_FOUND",
            message="封禁记录不存在。",
            status_code=404,
        )
    await session.delete(row)


async def get_min_vip(session: AsyncSession) -> MinVipTierResponse:
    row = await get_policy_row(session)
    return MinVipTierResponse(
        minVipTier=row.min_vip_tier,
        updatedAt=row.updated_at,
    )


async def patch_min_vip(session: AsyncSession, min_vip: int) -> MinVipTierResponse:
    row = await get_policy_row(session)
    row.min_vip_tier = min_vip
    row.updated_at = _now_utc()
    await session.flush()
    return MinVipTierResponse(minVipTier=row.min_vip_tier, updatedAt=row.updated_at)


async def get_rollout_policy(session: AsyncSession) -> RolloutPolicyResponse:
    row = await get_policy_row(session)
    return RolloutPolicyResponse(rolloutWhitelistEnforced=row.enforce_rollout_whitelist)


async def patch_rollout_policy(session: AsyncSession, enforced: bool) -> RolloutPolicyResponse:
    row = await get_policy_row(session)
    row.enforce_rollout_whitelist = enforced
    row.updated_at = _now_utc()
    await session.flush()
    return RolloutPolicyResponse(rolloutWhitelistEnforced=row.enforce_rollout_whitelist)


async def fetch_active_ban(session: AsyncSession, *, user_uid: str) -> AdminAccessUserBan | None:
    now = _now_utc()
    stmt = select(AdminAccessUserBan).where(AdminAccessUserBan.user_uid == user_uid.strip())
    res = await session.execute(stmt)
    for row in res.scalars().all():
        if row.expires_at is None or row.expires_at > now:
            return row
    return None


async def user_in_rollout_whitelist(session: AsyncSession, *, user_uid: str) -> bool:
    stmt = (
        select(func.count())
        .select_from(AdminAccessWhitelistEntry)
        .where(AdminAccessWhitelistEntry.user_uid == user_uid.strip())
    )
    res = await session.execute(stmt)
    n = res.scalar_one()
    return int(n or 0) > 0


def ban_envelope_code(row: AdminAccessUserBan) -> str:
    return _ban_reason_to_envelope_code(row.reason_code)


async def rollout_whitelist_enforced(session: AsyncSession) -> bool:
    row = await get_policy_row(session)
    return bool(row.enforce_rollout_whitelist)
