"""Safety phrase blocklist for Prompt Publish/Patch (runtime-injection §7.1)."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Literal

from chainup_agent.core.errors import AppError

# Monotonic revision — bump when §7.1.1 table changes.
SAFETY_PHRASE_BLOCKLIST_REVISION = "rev1"

DEFAULT_SAFETY_PHRASE_SCAN_SCOPE: Literal["FULL_PACK", "TRADING_BODY_FEWSHOT"] = "FULL_PACK"


@dataclass(frozen=True, slots=True)
class SafetyPhraseRule:
    rule_id: str
    phrase: str
    match_mode: Literal["latin_lower", "literal"]


SAFETY_PHRASE_RULES: tuple[SafetyPhraseRule, ...] = (
    SafetyPhraseRule("safety-01", "ignore previous instructions", "latin_lower"),
    SafetyPhraseRule("safety-02", "ignore the above", "latin_lower"),
    SafetyPhraseRule("safety-03", "disregard the above", "latin_lower"),
    SafetyPhraseRule("safety-04", "bypass safety", "latin_lower"),
    SafetyPhraseRule("safety-05", "bypass the safety", "latin_lower"),
    SafetyPhraseRule("safety-06", "you are now in developer mode", "latin_lower"),
    SafetyPhraseRule("safety-07", "jailbreak", "latin_lower"),
    SafetyPhraseRule("safety-08", "dan mode", "latin_lower"),
    SafetyPhraseRule("safety-09", "reveal your system prompt", "latin_lower"),
    SafetyPhraseRule("safety-10", "show your system prompt", "latin_lower"),
    SafetyPhraseRule("safety-11", "没有安全限制", "literal"),
    SafetyPhraseRule("safety-12", "忽略安全策略", "literal"),
    SafetyPhraseRule("safety-13", "绕过护栏", "literal"),
    SafetyPhraseRule("safety-14", "无视风控", "literal"),
    SafetyPhraseRule("safety-15", "取消内容策略", "literal"),
)


def _normalize_latin(text: str) -> str:
    return unicodedata.normalize("NFKC", text).lower()


def scan_text_for_safety_phrases(text: str) -> list[dict[str, str]]:
    """Return matched rules (ruleId only — do not echo full matched sentence in logs)."""
    if not text or not text.strip():
        return []
    latin_blob = _normalize_latin(text)
    hits: list[dict[str, str]] = []
    for rule in SAFETY_PHRASE_RULES:
        if rule.match_mode == "latin_lower":
            if rule.phrase in latin_blob:
                hits.append({"matchedRuleId": rule.rule_id, "gate": "SAFETY_PHRASE"})
        elif rule.phrase in text:
            hits.append({"matchedRuleId": rule.rule_id, "gate": "SAFETY_PHRASE"})
    return hits


def _collect_strings_from_messages(messages: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        c = m.get("content")
        if isinstance(c, str) and c.strip():
            parts.append(c)
    return "\n".join(parts)


def validate_messages_safety_phrases(
    messages: list[dict[str, Any]],
    *,
    field_label: str = "messages",
    extra_scan_text: str | None = None,
) -> None:
    """Raises ``AppError`` **PROMPT_SAFETY_VIOLATION** or **PROMPT_VALIDATION_FAILED** alias."""
    blob = _collect_strings_from_messages(messages)
    if extra_scan_text and extra_scan_text.strip():
        blob = f"{blob}\n{extra_scan_text.strip()}"
    hits = scan_text_for_safety_phrases(blob)
    if not hits:
        return
    first = hits[0]
    raise AppError(
        code="PROMPT_SAFETY_VIOLATION",
        message="Prompt 正文命中越狱/绕过护栏用语闸，禁止发布或保存。",
        status_code=422,
        details={
            "field": field_label,
            "gate": first.get("gate", "SAFETY_PHRASE"),
            "matchedRuleId": first.get("matchedRuleId"),
            "safetyPhraseBlocklistRevision": SAFETY_PHRASE_BLOCKLIST_REVISION,
            "matchCount": len(hits),
        },
    )


def blocklist_rules_for_api() -> list[dict[str, str]]:
    return [
        {
            "ruleId": r.rule_id,
            "phrase": r.phrase,
            "matchMode": r.match_mode,
        }
        for r in SAFETY_PHRASE_RULES
    ]
