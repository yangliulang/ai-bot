"""``scenarioId`` ↔ ``pp-*`` catalog — mirrors ``product-doc/.../governance-map.md``."""

from __future__ import annotations

from dataclasses import dataclass

from chainup_agent.application.skill_operation_spec_ref import SCENARIO_PRIMARY_SKILL

# Runtime platform / cross-cut rows (not in orchestration scenario registry).
PLATFORM_SYSTEM_SCENARIO_ID = "agent.runtime.platform_system"
PLATFORM_SAFETY_SCENARIO_ID = "agent.runtime.platform_safety"
RUNTIME_CLARIFY_SCENARIO_ID = "agent.runtime.runtime_clarify"
RUNTIME_OUTPUT_CONTRACT_SCENARIO_ID = "agent.runtime.runtime_output_contract"
ANALYSIS_CORE_SCENARIO_ID = "agent.runtime.analysis_core"

WRITE_SCENARIO_TO_PACK_ID: dict[str, str] = {
    "trade.spot.limit_order": "pp-trading-spot-limit",
    "trade.spot.flash_convert": "pp-trading-spot-flash",
    "trade.spot.amend_limit_order": "pp-trading-spot-amend",
    "trade.futures.market_order": "pp-trading-futures-market",
    "trade.futures.limit_order": "pp-trading-futures-limit",
    "trade.futures.amend_limit_order": "pp-trading-futures-amend",
    "trade.futures.take_profit_stop": "pp-trading-futures-tpsl",
    "futures.condition.order_create": "pp-trading-futures-tpsl",
    "margin.cross.market_order": "pp-trading-margin-market",
    "margin.cross.limit_order": "pp-trading-margin-limit",
    "wealth.subscribe": "pp-trading-wealth-subscribe",
    "wealth.redeem": "pp-trading-wealth-redeem",
}

READ_ANALYSIS_EXACT: frozenset[str] = frozenset(
    {
        "wealth.holdings_read",
        "read.account.balance",
        "read.market.ticker",
        "read.market.depth",
        "read.market.trades",
    }
)

READ_ANALYSIS_PREFIXES: tuple[str, ...] = (
    "read.market.",
    "market.read_",
    "research.",
    "monitoring.",
    "orders.read_",
    "portfolio.",
    "futures.read_",
)

# Legacy ``pack_*`` rows superseded by governance ``pp-*`` (same ``scenario_id`` or platform slot).
LEGACY_PACK_IDS_SUPERSEDED: frozenset[str] = frozenset(
    {
        "pack_platform_system_v1",
        "pack_platform_safety_v1",
        "pack_trading_spot_flash_convert_v1",
        "pack_trading_spot_limit_order_v1",
        "pack_trading_spot_amend_limit_order_v1",
        "pack_trading_futures_market_order_v1",
        "pack_trading_futures_limit_order_v1",
        "pack_trading_margin_cross_market_order_v1",
        "pack_trading_margin_cross_limit_order_v1",
        "pack_trading_read_market_ticker_v1",
        "pack_trading_read_market_depth_v1",
        "pack_trading_read_market_trades_v1",
        "pack_trading_read_account_balance_v1",
        "pack_trading_wealth_holdings_read_v1",
    }
)


@dataclass(frozen=True)
class GovernancePackSeed:
    prompt_pack_id: str
    prompt_pack_type: str
    scenario_id: str
    body_markdown: str
    skill_id: str | None = None


def is_analysis_governance_scenario(scenario_id: str) -> bool:
    sid = scenario_id.strip()
    if not sid or sid in WRITE_SCENARIO_TO_PACK_ID:
        return False
    if sid in READ_ANALYSIS_EXACT:
        return sid != "chat.faq"
    return any(sid.startswith(p) for p in READ_ANALYSIS_PREFIXES)


def governance_pack_id_for_scenario(scenario_id: str) -> str | None:
    sid = scenario_id.strip()
    if not sid:
        return None
    if sid in WRITE_SCENARIO_TO_PACK_ID:
        return WRITE_SCENARIO_TO_PACK_ID[sid]
    if is_analysis_governance_scenario(sid):
        return "pp-analysis-core"
    return None


def all_governance_pack_seeds() -> list[GovernancePackSeed]:
    from chainup_agent.data.prompt_governance_bodies import PROMPT_BODY_BY_PACK_ID

    rows: list[GovernancePackSeed] = [
        GovernancePackSeed(
            "pp-system-core",
            "SYSTEM",
            PLATFORM_SYSTEM_SCENARIO_ID,
            PROMPT_BODY_BY_PACK_ID["pp-system-core"],
        ),
        GovernancePackSeed(
            "pp-runtime-clarify",
            "SYSTEM",
            RUNTIME_CLARIFY_SCENARIO_ID,
            PROMPT_BODY_BY_PACK_ID["pp-runtime-clarify"],
        ),
        GovernancePackSeed(
            "pp-runtime-output-contract",
            "SYSTEM",
            RUNTIME_OUTPUT_CONTRACT_SCENARIO_ID,
            PROMPT_BODY_BY_PACK_ID["pp-runtime-output-contract"],
        ),
        GovernancePackSeed(
            "pp-safety-global",
            "SAFETY",
            PLATFORM_SAFETY_SCENARIO_ID,
            PROMPT_BODY_BY_PACK_ID["pp-safety-global"],
        ),
        GovernancePackSeed(
            "pp-analysis-core",
            "ANALYSIS",
            ANALYSIS_CORE_SCENARIO_ID,
            PROMPT_BODY_BY_PACK_ID["pp-analysis-core"],
        ),
    ]
    for scenario_id, pack_id in WRITE_SCENARIO_TO_PACK_ID.items():
        if scenario_id == "futures.condition.order_create":
            continue
        skill_id = SCENARIO_PRIMARY_SKILL.get(scenario_id)
        rows.append(
            GovernancePackSeed(
                pack_id,
                "TRADING",
                scenario_id,
                PROMPT_BODY_BY_PACK_ID[pack_id],
                skill_id=skill_id,
            )
        )
    return rows
