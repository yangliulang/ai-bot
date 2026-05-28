"""Effective Telegram LLM narrate flags: env override + gateway_defaults.telegramLlmNarrate."""

from __future__ import annotations

from typing import Any

from chainup_agent.core.config import Settings

TELEGRAM_LLM_NARRATE_SCENARIO_KEYS: tuple[str, ...] = (
    "readMarketTicker",
    "readMarketDepth",
    "readMarketTrades",
    "readAccountBalance",
    "wealthHoldingsRead",
    "spotFlashConfirm",
    "spotLimitConfirm",
    "futuresMarketConfirm",
    "futuresLimitConfirm",
)

DEFAULT_TELEGRAM_LLM_NARRATE: dict[str, bool] = dict.fromkeys(
    TELEGRAM_LLM_NARRATE_SCENARIO_KEYS, False
)

_SETTINGS_ATTR_BY_SCENARIO_KEY: dict[str, str] = {
    "readMarketTicker": "telegram_llm_narrate_read_market_ticker",
    "readMarketDepth": "telegram_llm_narrate_read_market_depth",
    "readMarketTrades": "telegram_llm_narrate_read_market_trades",
    "readAccountBalance": "telegram_llm_narrate_read_account_balance",
    "wealthHoldingsRead": "telegram_llm_narrate_wealth_holdings_read",
    "spotFlashConfirm": "telegram_llm_narrate_spot_flash_confirm",
    "spotLimitConfirm": "telegram_llm_narrate_spot_limit_confirm",
    "futuresMarketConfirm": "telegram_llm_narrate_futures_market_confirm",
    "futuresLimitConfirm": "telegram_llm_narrate_futures_limit_confirm",
}


def normalize_telegram_llm_narrate_defaults(merged: dict[str, Any]) -> dict[str, Any]:
    """Ensure ``telegramLlmNarrate`` has all known keys with boolean defaults."""
    raw = merged.get("telegramLlmNarrate")
    if not isinstance(raw, dict):
        raw = {}
    out = dict(merged)
    out["telegramLlmNarrate"] = {**DEFAULT_TELEGRAM_LLM_NARRATE, **raw}
    return out


def resolve_effective_telegram_llm_narrate(
    settings: Settings,
    merged_defaults: dict[str, Any] | None,
    scenario_key: str,
) -> bool:
    """
    Effective narrate for one scenario: env ``CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_*=true`` wins;
    else ``gateway_defaults.telegramLlmNarrate.<field>`` (default false when unset).
    """
    env_attr = _SETTINGS_ATTR_BY_SCENARIO_KEY.get(scenario_key)
    if env_attr and getattr(settings, env_attr, False):
        return True
    narrate: dict[str, Any] = {}
    if merged_defaults and isinstance(merged_defaults.get("telegramLlmNarrate"), dict):
        narrate = merged_defaults["telegramLlmNarrate"]
    return narrate.get(scenario_key) is True


def build_effective_telegram_llm_narrate_map(
    settings: Settings,
    merged_defaults: dict[str, Any] | None,
) -> dict[str, bool]:
    return {
        key: resolve_effective_telegram_llm_narrate(settings, merged_defaults, key)
        for key in TELEGRAM_LLM_NARRATE_SCENARIO_KEYS
    }
