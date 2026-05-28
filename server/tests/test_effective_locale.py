"""Unit tests for **effective_locale** three-bucket normalization."""

from __future__ import annotations

from chainup_agent.application.effective_locale import (
    EFFECTIVE_LOCALE_EN,
    EFFECTIVE_LOCALE_ZH_HANS,
    EFFECTIVE_LOCALE_ZH_HANT,
    normalize_effective_locale,
)


def test_normalize_none_empty() -> None:
    assert normalize_effective_locale(None) is None
    assert normalize_effective_locale("") is None
    assert normalize_effective_locale("   ") is None


def test_normalize_zh_hans() -> None:
    assert normalize_effective_locale("zh-CN") == EFFECTIVE_LOCALE_ZH_HANS
    assert normalize_effective_locale("zh_hans") == EFFECTIVE_LOCALE_ZH_HANS


def test_normalize_zh_hant() -> None:
    assert normalize_effective_locale("zh-TW") == EFFECTIVE_LOCALE_ZH_HANT
    assert normalize_effective_locale("zh-HK") == EFFECTIVE_LOCALE_ZH_HANT


def test_normalize_en_and_fallback() -> None:
    assert normalize_effective_locale("en") == EFFECTIVE_LOCALE_EN
    assert normalize_effective_locale("en-US") == EFFECTIVE_LOCALE_EN
    assert normalize_effective_locale("de-DE") == EFFECTIVE_LOCALE_EN
