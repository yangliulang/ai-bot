"""Registry SSOT mirror idempotency — CC-P1-03 · MR-E · SC-MCV1-05 / SC-OBS01."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from chainup_agent.application.exchange_tool_schema_registry import exchange_read_tools_bundle
from chainup_agent.application.orchestration_flow_catalog import ORCHESTRATION_FLOW_CATALOG
from chainup_agent.application.skill_operation_spec_ref import SCENARIO_PRIMARY_SKILL

REGISTRY_AUDIT_VERSION = "0.1.0"

_BUNDLE_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "skill_specs" / "runtime-bundle.json"
)
_MANIFEST_PATH = Path(__file__).resolve().parent.parent / "data" / "registry" / "ssot_manifest.json"

_SKILL_TO_SCENARIO = {skill: scenario for scenario, skill in SCENARIO_PRIMARY_SKILL.items()}

_TOOL_LIKE_EVENTS = frozenset(
    {
        "agent.tool.call",
        "trading.exchange_private",
        "trading.exchange_public",
    }
)


@dataclass(frozen=True)
class EnableGateResult:
    allowed: bool
    code: str | None = None


@dataclass(frozen=True)
class RegistryMirrorEntry:
    stable_id: str
    entry_class: str
    matrix_status: str
    scenario_id: str | None = None
    summary: str | None = None


@dataclass(frozen=True)
class RegistryMirror:
    skill_ids: tuple[str, ...]
    tool_ids: tuple[str, ...]
    scenario_ids: tuple[str, ...]
    items: tuple[RegistryMirrorEntry, ...]


@dataclass(frozen=True)
class IdempotencyMismatch:
    missing_in_mirror: tuple[str, ...]
    extra_in_mirror: tuple[str, ...]


def _normalize_matrix_status(raw: str) -> str:
    t = (raw or "").strip()
    if not t:
        return "TBD"
    upper = t.upper()
    if upper == "TBD":
        return "TBD"
    lower = t.lower()
    if lower in ("draft", "frozen", "ready"):
        return lower
    return t


@lru_cache(maxsize=1)
def _load_bundle_skill_ids() -> tuple[str, ...]:
    if not _BUNDLE_PATH.is_file():
        return ()
    raw = json.loads(_BUNDLE_PATH.read_text(encoding="utf-8"))
    items = raw.get("items") if isinstance(raw, dict) else None
    if not isinstance(items, list):
        return ()
    out: list[str] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        lifecycle = str(it.get("lifecycle") or "").strip().upper()
        if lifecycle != "PUBLISHED":
            continue
        sid = str(it.get("skillId") or "").strip()
        if sid:
            out.append(sid)
    return tuple(sorted(set(out)))


@lru_cache(maxsize=1)
def _load_ssot_manifest() -> dict[str, Any]:
    if not _MANIFEST_PATH.is_file():
        return {"tools": [], "optionalTools": []}
    raw = json.loads(_MANIFEST_PATH.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {"tools": [], "optionalTools": []}


def ssot_tool_ids_from_manifest() -> tuple[str, ...]:
    manifest = _load_ssot_manifest()
    tools = manifest.get("tools")
    if not isinstance(tools, list):
        return ()
    ids: list[str] = []
    for row in tools:
        if isinstance(row, dict):
            tid = str(row.get("toolId") or "").strip()
            if tid:
                ids.append(tid)
    return tuple(sorted(set(ids)))


def ssot_tool_ids_from_exchange_registry() -> tuple[str, ...]:
    bundle = exchange_read_tools_bundle()
    tools = bundle.get("tools")
    if not isinstance(tools, list):
        return ()
    ids: list[str] = []
    for row in tools:
        if isinstance(row, dict):
            tid = str(row.get("toolId") or "").strip()
            if tid:
                ids.append(tid)
    return tuple(sorted(set(ids)))


def load_registry_mirror() -> RegistryMirror:
    """Project runtime registry mirror from bundle + exchange tools + catalog."""
    skill_ids = _load_bundle_skill_ids()
    tool_ids = ssot_tool_ids_from_exchange_registry()
    scenario_ids = tuple(sorted({flow.scenario_id for flow in ORCHESTRATION_FLOW_CATALOG}))

    items: list[RegistryMirrorEntry] = []
    for sid in skill_ids:
        items.append(
            RegistryMirrorEntry(
                stable_id=sid,
                entry_class="A",
                matrix_status="frozen",
                scenario_id=_SKILL_TO_SCENARIO.get(sid),
                summary=f"PUBLISHED skill operation spec · {sid}",
            )
        )

    manifest = _load_ssot_manifest()
    manifest_tools = manifest.get("tools")
    if isinstance(manifest_tools, list):
        for row in manifest_tools:
            if not isinstance(row, dict):
                continue
            tid = str(row.get("toolId") or "").strip()
            if not tid or tid not in tool_ids:
                continue
            items.append(
                RegistryMirrorEntry(
                    stable_id=tid,
                    entry_class=str(row.get("entryClass") or "B"),
                    matrix_status=_normalize_matrix_status(str(row.get("matrixStatus") or "frozen")),
                    summary=str(row.get("summary") or "") or None,
                )
            )

    return RegistryMirror(
        skill_ids=skill_ids,
        tool_ids=tool_ids,
        scenario_ids=scenario_ids,
        items=tuple(items),
    )


def _mirror_class_ids(mirror: RegistryMirror, entry_class: str) -> set[str]:
    return {e.stable_id for e in mirror.items if e.entry_class == entry_class}


def _diff_sets(expected: set[str], actual: set[str]) -> IdempotencyMismatch:
    return IdempotencyMismatch(
        missing_in_mirror=tuple(sorted(expected - actual)),
        extra_in_mirror=tuple(sorted(actual - expected)),
    )


def assert_skill_registry_idempotent(
    mirror: RegistryMirror,
    ssot_skills: tuple[str, ...] | set[str],
) -> None:
    expected = set(ssot_skills)
    actual = _mirror_class_ids(mirror, "A")
    diff = _diff_sets(expected, actual)
    if diff.missing_in_mirror or diff.extra_in_mirror:
        raise AssertionError(
            f"skill registry not idempotent: missing={diff.missing_in_mirror} extra={diff.extra_in_mirror}"
        )


def assert_tool_registry_idempotent(
    mirror: RegistryMirror,
    ssot_tools: tuple[str, ...] | set[str],
) -> None:
    expected = set(ssot_tools)
    actual = _mirror_class_ids(mirror, "B")
    diff = _diff_sets(expected, actual)
    if diff.missing_in_mirror or diff.extra_in_mirror:
        raise AssertionError(
            f"tool registry not idempotent: missing={diff.missing_in_mirror} extra={diff.extra_in_mirror}"
        )


def assert_enable_allowed(matrix_status: str) -> EnableGateResult:
    """SC-MCV1-05 — matrix TBD/draft must not enable."""
    normalized = _normalize_matrix_status(matrix_status)
    if normalized in ("TBD", "draft"):
        return EnableGateResult(allowed=False, code="REGISTRY_MATRIX_TBD")
    if normalized in ("frozen", "ready"):
        return EnableGateResult(allowed=True)
    return EnableGateResult(allowed=False, code="REGISTRY_MATRIX_TBD")


def _event_summary(event: dict[str, Any]) -> dict[str, Any]:
    summary = event.get("summary")
    return summary if isinstance(summary, dict) else {}


def _timeline_scenario_id(events: list[dict[str, Any]]) -> str | None:
    for ev in events:
        summary = _event_summary(ev)
        sid = summary.get("scenarioId") or summary.get("scenario_id")
        if sid:
            return str(sid).strip()
    return None


def assert_obs_tool_call_scenario_join(
    events: list[dict[str, Any]],
    registry_tool_ids: tuple[str, ...] | set[str] | None = None,
) -> None:
    """SC-OBS01 direction — tool/write events must join scenarioId on same timeline."""
    scenario_id = _timeline_scenario_id(events)
    tool_events = [
        ev
        for ev in events
        if (ev.get("eventName") or ev.get("event_name")) in _TOOL_LIKE_EVENTS
    ]
    if not tool_events:
        return
    for ev in tool_events:
        summary = _event_summary(ev)
        ev_scenario = summary.get("scenarioId") or summary.get("scenario_id") or scenario_id
        if not ev_scenario:
            raise AssertionError(
                "SC-OBS01 violated: tool/write event missing joinable scenarioId"
            )


def compute_idempotency_audit() -> dict[str, Any]:
    mirror = load_registry_mirror()
    ssot_skills = _load_bundle_skill_ids()
    ssot_tools = ssot_tool_ids_from_manifest()
    skill_diff = _diff_sets(set(ssot_skills), _mirror_class_ids(mirror, "A"))
    tool_diff = _diff_sets(set(ssot_tools), _mirror_class_ids(mirror, "B"))
    ok = not (
        skill_diff.missing_in_mirror
        or skill_diff.extra_in_mirror
        or tool_diff.missing_in_mirror
        or tool_diff.extra_in_mirror
    )
    return {
        "ok": ok,
        "auditVersion": REGISTRY_AUDIT_VERSION,
        "skillMismatches": {
            "missingInMirror": list(skill_diff.missing_in_mirror),
            "extraInMirror": list(skill_diff.extra_in_mirror),
        },
        "toolMismatches": {
            "missingInMirror": list(tool_diff.missing_in_mirror),
            "extraInMirror": list(tool_diff.extra_in_mirror),
        },
    }


def registry_mirror_list_payload(
    *,
    entry_class: str | None = None,
    matrix_status: str | None = None,
) -> dict[str, Any]:
    mirror = load_registry_mirror()
    items = list(mirror.items)
    if entry_class:
        ec = entry_class.strip().upper()
        items = [i for i in items if i.entry_class.upper() == ec]
    if matrix_status:
        ms = _normalize_matrix_status(matrix_status)
        items = [i for i in items if i.matrix_status == ms]
    return {
        "registryVersion": REGISTRY_AUDIT_VERSION,
        "items": [
            {
                "stableId": e.stable_id,
                "entryClass": e.entry_class,
                "matrixStatus": e.matrix_status,
                "scenarioId": e.scenario_id,
                "summary": e.summary,
            }
            for e in items
        ],
    }
