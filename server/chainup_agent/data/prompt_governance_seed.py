"""Build DB payloads for governance ``pp-*`` pack upsert."""

from __future__ import annotations

import hashlib
import json

from chainup_agent.data.prompt_governance_catalog import GovernancePackSeed


def _sha_etag(messages: list[dict]) -> str:
    raw = json.dumps(messages, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return f'W/"{hashlib.sha256(raw).hexdigest()[:32]}"'


def _write_path_few_shot(seed: GovernancePackSeed) -> list[dict[str, str]]:
    sid = seed.scenario_id
    return [
        {
            "role": "user",
            "content": f"示例：请说明场景 {sid} 下用户须核对哪些参数后再确认。",
        },
        {
            "role": "assistant",
            "content": (
                "示意：根据 Behavioral Rules 列出必填字段与风险要点；"
                "须等待 Type-A 确认，不代替用户下单或改单。"
            ),
        },
    ]


def pack_messages_and_schema(seed: GovernancePackSeed) -> tuple[str, str, str | None]:
    """Returns ``(messages_json, etag, variable_schema_json)``."""
    messages: list[dict[str, str]] = [{"role": "system", "content": seed.body_markdown.strip()}]
    if seed.prompt_pack_type == "TRADING" and seed.skill_id:
        messages.extend(_write_path_few_shot(seed))
    schema: str | None = None
    if seed.skill_id:
        schema = json.dumps({"skillSpecRef": seed.skill_id}, ensure_ascii=False)
    etag = _sha_etag(messages)
    return json.dumps(messages, ensure_ascii=False), etag, schema
