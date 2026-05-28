"""BCP-47 hints → product **effective_locale** buckets (telegram/overview · ASSEMBLY §2)."""

from __future__ import annotations

# Three buckets aligned with product-doc `telegram/overview` §2.4 / prompts library.
EFFECTIVE_LOCALE_ZH_HANS = "zh-Hans"
EFFECTIVE_LOCALE_ZH_HANT = "zh-Hant"
EFFECTIVE_LOCALE_EN = "en"


def normalize_effective_locale(raw: str | None) -> str | None:
    """Map arbitrary locale tags to **zh-Hans** | **zh-Hant** | **en**.

    Returns ``None`` when ``raw`` is empty / whitespace only.
    Unrecognized tags fall back to **en** (product default for non-CJK).
    """
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    low = s.lower().replace("_", "-")
    if low in ("zh", "zh-cmn", "cmn"):
        return EFFECTIVE_LOCALE_ZH_HANS
    if low in ("zh-hans", "zh-cn", "zh-sg"):
        return EFFECTIVE_LOCALE_ZH_HANS
    if low.startswith("zh-hans"):
        return EFFECTIVE_LOCALE_ZH_HANS
    if low in ("zh-hant", "zh-tw", "zh-hk", "zh-mo"):
        return EFFECTIVE_LOCALE_ZH_HANT
    if low.startswith("zh-hant"):
        return EFFECTIVE_LOCALE_ZH_HANT
    if low == "en" or low.startswith("en-"):
        return EFFECTIVE_LOCALE_EN
    if low.startswith("zh-"):
        # Unknown Chinese regional tag — default to Simplified bucket.
        return EFFECTIVE_LOCALE_ZH_HANS
    return EFFECTIVE_LOCALE_EN
