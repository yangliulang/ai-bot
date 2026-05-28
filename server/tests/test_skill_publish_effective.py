"""Skill Publish effective chain — 2026-05-27--skill-publish-effective."""

from __future__ import annotations

import json

import pytest
from httpx import AsyncClient

from tests.skill_spec_helpers import seed_skill_operation_specs_from_bundle


@pytest.fixture(autouse=True)
async def _seed_skills() -> None:
    await seed_skill_operation_specs_from_bundle()


@pytest.mark.asyncio
async def test_skill_spec_import_list_count(http_client: AsyncClient) -> None:
    """TC-01 / TC-02 — bundle import visible in list."""
    r = await http_client.get("/api/v1/admin/skill-specs")
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 11
    ids = {x["skillId"] for x in items}
    assert "skill.spot.limit_order" in ids


@pytest.mark.asyncio
async def test_skill_spec_admin_detail_versions_body(http_client: AsyncClient) -> None:
    """TC-03."""
    kid = "skill.spot.limit_order"
    r = await http_client.get(f"/api/v1/admin/skill-specs/{kid}")
    assert r.status_code == 200
    assert r.json()["skillSpecVersion"]

    rv = await http_client.get(f"/api/v1/admin/skill-specs/{kid}/versions")
    assert rv.status_code == 200
    ver = rv.json()["items"][0]["skillSpecVersion"]

    rb = await http_client.get(f"/api/v1/admin/skill-specs/{kid}/versions/{ver}")
    assert rb.status_code == 200
    assert len(rb.json()["bodyMarkdown"]) > 200

    missing = await http_client.get("/api/v1/admin/skill-specs/skill.unknown.nope")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_skill_spec_publish_higher_version(http_client: AsyncClient) -> None:
    """TC-04."""
    kid = "skill.spot.flash_convert"
    body = {
        "skillSpecVersion": "9.9.9-contract",
        "bodyMarkdown": (
            "# Skill test\n\n## 1. Required / Optional Params\n\n"
            + ("x" * 300)
        ),
    }
    r = await http_client.post(f"/api/v1/admin/skill-specs/{kid}/publish", json=body)
    assert r.status_code == 200
    assert r.json()["lifecycle"] == "PUBLISHED"
    assert r.json()["skillSpecVersion"] == "9.9.9-contract"


@pytest.mark.asyncio
async def test_internal_effective_and_runtime_pointer(http_client: AsyncClient) -> None:
    """TC-05 / TC-06."""
    kid = "skill.spot.limit_order"
    summary = await http_client.get(f"/api/v1/admin/skill-specs/{kid}")
    ver = summary.json()["skillSpecVersion"]

    ri = await http_client.get(
        "/api/v1/internal/skills/effective",
        params={"skillId": kid, "skillSpecVersion": ver},
    )
    assert ri.status_code == 200
    assert ri.json()["bodyMarkdown"]
    assert ri.headers.get("etag")

    rr = await http_client.get(
        "/api/v1/runtime/skill-operation-spec/effective",
        params={"skillId": kid},
    )
    assert rr.status_code == 200
    assert rr.json()["skillSpecVersion"] == ver

    bad = await http_client.get(
        "/api/v1/internal/skills/effective",
        params={"skillId": kid, "skillSpecVersion": "0.0.0-not-published"},
    )
    assert bad.status_code == 403
    assert bad.json()["code"] == "PROMPT_SKILL_REF_INVALID"


@pytest.mark.asyncio
async def test_prompt_publish_skill_spec_ref_gate(
    http_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-07."""
    create = await http_client.post(
        "/api/v1/admin/prompt-packs",
        json={
            "promptPackType": "TRADING",
            "scenarioId": "trade.spot.limit_order",
            "promptPackId": "pack_skill_gate_test",
        },
    )
    assert create.status_code == 201
    pid = create.json()["promptPackId"]

    patch = await http_client.patch(
        f"/api/v1/admin/prompt-packs/{pid}",
        json={
            "messages": [{"role": "system", "content": "test"}],
            "variableSchema": {
                "skillSpecRef": "skill.spot.limit_order@0.0.0-not-published"
            },
        },
    )
    assert patch.status_code == 200

    pub_fail = await http_client.post(f"/api/v1/admin/prompt-packs/{pid}/publish")
    assert pub_fail.status_code == 422
    assert pub_fail.json()["code"] == "PROMPT_SKILL_REF_INVALID"

    summary = await http_client.get("/api/v1/admin/skill-specs/skill.spot.limit_order")
    ver = summary.json()["skillSpecVersion"]
    patch_ok = await http_client.patch(
        f"/api/v1/admin/prompt-packs/{pid}",
        json={
            "variableSchema": {"skillSpecRef": f"skill.spot.limit_order@{ver}"},
        },
    )
    assert patch_ok.status_code == 200
    pub_ok = await http_client.post(f"/api/v1/admin/prompt-packs/{pid}/publish")
    assert pub_ok.status_code == 200


@pytest.mark.asyncio
async def test_publish_version_rollback_rejected(http_client: AsyncClient) -> None:
    """TC-08 / TC-09."""
    kid = "skill.spot.amend_limit_order"
    summary = await http_client.get(f"/api/v1/admin/skill-specs/{kid}")
    current = summary.json()["skillSpecVersion"]

    r = await http_client.post(
        f"/api/v1/admin/skill-specs/{kid}/publish",
        json={"skillSpecVersion": "0.0.1-mvp", "bodyMarkdown": ""},
    )
    assert r.status_code == 400
    assert r.json()["code"] == "PROMPT_SKILL_VERSION_ROLLBACK"

    body = {
        "skillSpecVersion": "9.8.0-contract",
        "bodyMarkdown": (
            "# Amend skill\n\n## 1. Required / Optional Params\n\n" + ("y" * 400)
        ),
    }
    ok = await http_client.post(f"/api/v1/admin/skill-specs/{kid}/publish", json=body)
    assert ok.status_code == 200
    assert version_greater(ok.json()["skillSpecVersion"], current) or ok.json()[
        "skillSpecVersion"
    ] == "9.8.0-contract"


def version_greater(a: str, b: str) -> bool:
    from chainup_agent.application.skill_operation_spec_store import version_greater_than

    return version_greater_than(a, b)
