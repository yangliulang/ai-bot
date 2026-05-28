"""Telegram webhook: bound / allowlisted users — gate → intent → read routing."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from chainup_agent.api.schemas.agent_runtime import (
    EligibilityEnvelope,
    EvaluateEligibilityRequest,
    IntentNluDraft,
    IntentPolicyPlan,
    IntentRecognizeResponse,
)
from chainup_agent.application.agent_access_evaluate import evaluate_eligibility
from chainup_agent.application.agent_execution_events import append_execution_timeline_event
from chainup_agent.application.agent_execution_memory import run_telegram_turn_execution
from chainup_agent.application.agent_intent_pipeline import recognize_intent_full
from chainup_agent.application.admin_ai_settings import read_gateway_defaults_merged
from chainup_agent.application.agent_llm_chat import invoke_llm_chat_for_telegram
from chainup_agent.application.agent_prompt_effective import (
    INTENT_NLU_SCENARIO_ID,
    effective_prompt_snapshot_for_scenario,
)
from chainup_agent.application.agent_routing_exchange_read import (
    routing_execute_exchange_reads,
)
from chainup_agent.application.agent_routing_execute_http import (
    append_routing_execute_timeline,
    routing_telegram_read_request,
)
from chainup_agent.application.agent_futures_trade import (
    futures_cancel_order_for_bound_user,
)
from chainup_agent.application.agent_futures_condition_trade import (
    futures_condition_orders_for_bound_user,
)
from chainup_agent.application.agent_spot_trade import (
    check_spot_limit_price_agent_band,
    spot_cancel_order_for_bound_user,
    spot_open_orders_for_bound_user,
    spot_quote_for_bound_user,
)
from chainup_agent.application.confirmation_rules_evaluate import (
    evaluate_confirmation_for_trade,
    format_block_auto_execute_message,
    format_otp_confirm_note,
    format_second_confirm_preamble,
)
from chainup_agent.application.telegram_stm import (
    handle_telegram_memory_command,
    mark_type_a_pending,
    merge_stm_runtime_context,
    previous_scenario_for_session,
    record_telegram_stm_turn,
    remember_resolved_scenario,
    telegram_session_id,
    try_memory_command_intent,
)
from chainup_agent.application.write_path_pipeline import (
    append_confirmation_required,
    ensure_write_path_skill_spec_read,
    write_path_has_skill_spec,
)
from chainup_agent.application.prompt_assembly_write_path_audit import (
    append_trading_write_prompt_snapshot_if_missing,
)
from chainup_agent.application.telegram_llm_narrate_policy import (
    build_effective_telegram_llm_narrate_map,
)
from chainup_agent.application.telegram_app_error_user_message import (
    format_app_error_reply_for_telegram,
)
from chainup_agent.application.telegram_flash_pending import (
    CB_FLASH_CANCEL,
    CB_FLASH_CONFIRM,
    CB_FUTURES_LIMIT_CANCEL,
    CB_FUTURES_LIMIT_CONFIRM,
    CB_FUTURES_MARKET_CANCEL,
    CB_FUTURES_MARKET_CONFIRM,
    CB_CONDITION_CONFIRM,
    CB_CONDITION_CANCEL,
    CB_CONDITION_CANCEL_CONFIRM,
    CB_CONDITION_CANCEL_DISMISS,
    CB_AMEND_CANCEL,
    CB_AMEND_CONFIRM,
    create_condition_pending,
    create_condition_cancel_pending,
    CB_LIMIT_CANCEL,
    CB_LIMIT_CONFIRM,
    CB_MARGIN_LIMIT_P1_CANCEL,
    CB_MARGIN_LIMIT_P1_CONFIRM,
    CB_MARGIN_MARKET_P1_CANCEL,
    CB_MARGIN_MARKET_P1_CONFIRM,
    create_flash_convert_pending,
    create_futures_limit_pending,
    create_futures_market_pending,
    create_margin_limit_pending_phase1,
    create_margin_market_pending_phase1,
    create_spot_amend_pending,
    create_spot_limit_pending,
)
from chainup_agent.application.telegram_symbol_extract import extract_symbol_for_ticker
from chainup_agent.application.agent_llm_clarify import (
    resolve_effective_intent_clarify_use_llm,
    try_llm_clarify_reply,
)
from chainup_agent.application.memory_session_store import (
    clear_pending_clarify,
    get_pending_clarify_slots,
    remember_pending_clarify,
)
from chainup_agent.application.trade_slot_clarify import (
    SCENARIOS_USING_SPOT_NOTIONAL_RESOLVE,
    quote_qty_to_base_at_limit_price,
    quote_qty_to_base_quantity,
    resolve_trade_notional_slots,
)
from chainup_agent.core.config import Settings
from chainup_agent.core.errors import AppError
from chainup_agent.domain.canonical_trading import instrument_ref_from_sym_ticker

_TYPE_A_CB_PREFIXES = (
    CB_FLASH_CONFIRM,
    CB_LIMIT_CONFIRM,
    CB_AMEND_CONFIRM,
    CB_FUTURES_MARKET_CONFIRM,
    CB_FUTURES_LIMIT_CONFIRM,
    CB_CONDITION_CONFIRM,
    CB_MARGIN_MARKET_P1_CONFIRM,
    CB_MARGIN_LIMIT_P1_CONFIRM,
)


def _markup_is_type_a_confirm(markup: dict[str, Any] | None) -> bool:
    if not markup:
        return False
    for row in markup.get("inline_keyboard") or []:
        if not isinstance(row, list):
            continue
        for btn in row:
            if not isinstance(btn, dict):
                continue
            cd = str(btn.get("callback_data") or "")
            if any(cd.startswith(p) for p in _TYPE_A_CB_PREFIXES):
                return True
    return False

_MAX_BODY_CHARS = 3400


def _allowlist_binding_hint(capabilities: dict[str, Any] | None) -> str:
    """Footer when chat/tg is allowlisted but no hosted trading API binding."""
    if not capabilities:
        return ""
    if capabilities.get("boundChatAllowlist") and not capabilities.get("bindingVerified"):
        return (
            "\n\n提示：当前会话命中联调放行名单；若要查询交易所行情或账户余额，"
            "仍需先行完成 Deeplink/H5 托管 API 绑定。"
        )
    return ""


def _lead(body: str) -> str:
    core = body.strip()
    if len(core) <= _MAX_BODY_CHARS:
        return core
    return core[: _MAX_BODY_CHARS - 1] + "…"


def _runtime_context_json_safe(obj: Any) -> Any:
    """Coerce preview blobs for ``runtime_context`` JSON (LLM assembly)."""
    if isinstance(obj, dict):
        return {str(k): _runtime_context_json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_runtime_context_json_safe(x) for x in obj[:500]]
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


async def _try_telegram_public_read_llm_narration(
    *,
    session: AsyncSession,
    settings: Settings,
    enabled: bool,
    scenario_id: str,
    user_text: str,
    turn_eid: str,
    chat_id: int,
    anchor_id: int,
    effective_locale: str | None,
    exchange_read_preview: dict[str, Any],
    routing_note: str | None,
    event_name: str,
    step_kind: str,
    source_attribution_footer: str,
) -> str | None:
    """Optional narration after Telegram ``read.*`` routing succeeds.

    Used for **公有行情**（``read.market.*``）与 **托管只读**（``read.account.balance``、
    ``wealth.holdings_read``）— LLM **启用**时无论成败写入 timeline（见各 ``event_name``）。

    Returns assistant text plus footer when LLM succeeds, else ``None`` (deterministic fallback).
    """
    if not enabled:
        return None
    rtc = {
        "kind": scenario_id,
        "exchangeReadPreview": _runtime_context_json_safe(exchange_read_preview),
        "routingNote": (routing_note or "")[:2000],
    }
    assistant, llm_err, llm_obs = await invoke_llm_chat_for_telegram(
        session=session,
        settings=settings,
        user_text=user_text,
        scenario_id=scenario_id,
        effective_locale=effective_locale,
        execution_id=turn_eid,
        session_id=f"tg:{chat_id}",
        runtime_context=rtc,
    )
    narr_ver, narr_bind = await effective_prompt_snapshot_for_scenario(
        session, scenario_id=scenario_id
    )
    outcome = "success" if assistant else "failure"
    await append_execution_timeline_event(
        session,
        execution_id=turn_eid,
        user_id=str(anchor_id),
        event_name=event_name,
        step_kind=step_kind,
        outcome=outcome,
        payload={
            "scenarioId": scenario_id,
            "promptPackVersion": narr_ver,
            "resolvedPromptBinding": narr_bind,
            "effectiveTelegramLlmNarrateEnabled": True,
            **(llm_obs or {}),
            "userVisibleError": (llm_err or "")[:500] if not assistant else None,
        },
    )
    if assistant:
        return assistant.strip() + source_attribution_footer
    return None


async def _try_telegram_trade_type_a_llm_preamble(
    *,
    session: AsyncSession,
    settings: Settings,
    enabled: bool,
    scenario_id: str,
    user_text: str,
    turn_eid: str,
    chat_id: int,
    anchor_id: int,
    effective_locale: str | None,
    slots_dict: dict[str, Any],
    quote_preview: dict[str, Any],
    event_name: str,
) -> str | None:
    """Optional LLM lines before deterministic Type-A confirmation (flash / limit)."""
    if not enabled:
        return None
    sid = telegram_session_id(chat_id)
    rtc = merge_stm_runtime_context(
        session_id=sid,
        user_id=str(anchor_id),
        base={
            "kind": scenario_id,
            "confirmKind": "type_a_inline",
            "slots": _runtime_context_json_safe(slots_dict),
            "quotePreview": _runtime_context_json_safe(quote_preview),
        },
    )
    assistant, llm_err, llm_obs = await invoke_llm_chat_for_telegram(
        session=session,
        settings=settings,
        user_text=user_text,
        scenario_id=scenario_id,
        effective_locale=effective_locale,
        execution_id=turn_eid,
        session_id=f"tg:{chat_id}",
        runtime_context=rtc,
    )
    narr_ver, narr_bind = await effective_prompt_snapshot_for_scenario(
        session, scenario_id=scenario_id
    )
    outcome = "success" if assistant else "failure"
    await append_execution_timeline_event(
        session,
        execution_id=turn_eid,
        user_id=str(anchor_id),
        event_name=event_name,
        step_kind="type_a_preamble",
        outcome=outcome,
        payload={
            "scenarioId": scenario_id,
            "promptPackVersion": narr_ver,
            "resolvedPromptBinding": narr_bind,
            "effectiveTelegramLlmNarrateEnabled": True,
            **(llm_obs or {}),
            "userVisibleError": (llm_err or "")[:500] if not assistant else None,
        },
    )
    if assistant:
        return assistant.strip() + "\n\n"
    return None


def _format_trade_stub(scenario_id: str) -> str:
    sid = (scenario_id or "").strip() or "unknown"
    head = (
        f"场景 `{sid}` 当前仍为占位（后续路线图），本服务暂不触发对应交易所写路径。\n"
    )
    if sid.startswith("trade.futures"):
        tail = (
            "合约能力将以路线图 Phase2.3 接入；当前可先使用已绑定的现货闪兑/限价（见产品说明）。"
        )
    elif sid.startswith("margin."):
        tail = "全仓杠杆已接入 HTTP/TG 双确认；划转链路与逐仓能力见路线图后续步骤。"
    elif sid.startswith("automation."):
        tail = "条件单已接入 HTTP/TG 类型 A 确认；查询/取消见路线图后续步骤。"
    elif sid in ("trade.spot.oco", "trade.spot.bracket"):
        tail = (
            "OCO / bracket 相关接口仍在矩阵冻结或扩容中，Agent 当前不能替你完成双挂或括号单闭环。\n"
            "请在 Coobit 主站交易页操作，或先使用已支持的现货限价/改单能力。"
        )
    else:
        tail = "如需演示只读能力，可发送「BTC-USDT 行情」「盘口」「账户余额」或「理财持仓」。"
    return head + tail


def _resolve_read_symbol_for_telegram(
    *,
    nlu: IntentNluDraft | None,
    user_text: str,
    session_id: str,
) -> str | None:
    """NLU slots → text extract → STM pending (multi-turn read.* follow-ups)."""
    sym = (nlu.slots.get("symbol") if nlu and nlu.slots else None) or None
    sym = (sym or "").strip() or extract_symbol_for_ticker(user_text)
    if not sym and session_id.strip():
        _, pend = get_pending_clarify_slots(session_id)
        sym = (pend.get("symbol") or "").strip()
    return sym or None


def _format_plan_clarify(plan: IntentPolicyPlan) -> str:
    lines = list(plan.clarify or [])
    if plan.note:
        lines.append(plan.note)
    return "\n".join(lines) if lines else "请补充信息后重试。"


async def _telegram_clarify_reply_body(
    session: AsyncSession,
    settings: Settings,
    *,
    user_text: str,
    plan: IntentPolicyPlan,
    nlu_slots: dict[str, str],
    turn_eid: str,
    anchor_id: int,
    chat_id: int,
    effective_locale: str,
) -> str:
    """Rule-based clarify; optional LLM polish (``agent.runtime.runtime_clarify``)."""
    from chainup_agent.application.clarify_inbound import after_clarify_plan

    rule_body = _format_plan_clarify(plan)
    out = rule_body
    merged_defaults = None
    if not settings.intent_clarify_use_llm:
        merged_defaults, _ = await read_gateway_defaults_merged(session)
    skip_llm_polish = bool(
        nlu_slots.get("tradeMode")
        and (plan.resolved_scenario_id or "").startswith("trade.spot")
    )
    if resolve_effective_intent_clarify_use_llm(settings, merged_defaults) and not skip_llm_polish:
        llm_text, obs = await try_llm_clarify_reply(
            session,
            settings,
            user_text=user_text,
            scenario_id=plan.resolved_scenario_id,
            rule_lines=list(plan.clarify or []),
            policy_codes=list(plan.policy_codes or []),
            slots=nlu_slots,
            effective_locale=effective_locale,
            execution_id=turn_eid,
            session_id=telegram_session_id(chat_id),
        )
        if llm_text:
            ver, bind = await effective_prompt_snapshot_for_scenario(
                session, scenario_id="agent.runtime.runtime_clarify"
            )
            await append_execution_timeline_event(
                session,
                execution_id=turn_eid,
                user_id=str(anchor_id),
                event_name="llm.agent.runtime.runtime_clarify",
                step_kind="clarify_llm",
                outcome="success",
                payload={
                    "scenarioId": "agent.runtime.runtime_clarify",
                    "targetScenarioId": plan.resolved_scenario_id,
                    "promptPackVersion": ver,
                    "resolvedPromptBinding": bind,
                    **(obs or {}),
                },
            )
            out = llm_text

    return after_clarify_plan(
        session_id=telegram_session_id(chat_id),
        execution_id=turn_eid,
        slots=nlu_slots,
        next_step="CLARIFY",
        pending_kind=None,
        settings=settings,
        outbound_text=out,
        inbound_text=user_text,
    )


def _format_blocked_feature(plan: IntentPolicyPlan) -> str:
    codes = ", ".join(plan.policy_codes or [])
    return f"当前环境暂不可执行该请求（功能开关或产品线限制）。\n（policyCodes：`{codes}`）"


async def _append_intent_nlu_prompt_timeline(
    session: AsyncSession,
    settings: Settings,
    *,
    execution_id: str,
    user_id: str,
    ir: IntentRecognizeResponse,
    plan: IntentPolicyPlan | None,
    exec_scenario_id: str,
) -> None:
    ver, bind = await effective_prompt_snapshot_for_scenario(
        session, scenario_id=INTENT_NLU_SCENARIO_ID
    )
    await append_execution_timeline_event(
        session,
        execution_id=execution_id,
        user_id=user_id,
        event_name="prompt.snapshot",
        step_kind="intent_nlu",
        outcome="info",
        payload={
            "scenarioId": INTENT_NLU_SCENARIO_ID,
            "promptPackVersion": ver,
            "resolvedPromptBinding": bind,
            "nluSource": ir.nlu_source,
            "intentNluLlmEnabled": bool(ir.effective_intent_nlu_use_llm),
            "orchestrationVersion": ir.orchestration_version,
            "executionScenarioId": exec_scenario_id,
            "planNextStep": plan.next_step if plan else None,
            "resolvedScenarioId": plan.resolved_scenario_id if plan else None,
        },
    )


_ESTIMATE_QUOTE_DISPLAY_QUANT = Decimal("0.01")


def _spot_base_quote_assets(symbol: str) -> tuple[str | None, str | None]:
    """Parse ``BASE-QUOTE`` / ``BASE/QUOTE`` into assets; unknown shape → ``(None, None)``."""
    raw = (symbol or "").strip().upper().replace("/", "-")
    if not raw or "-" not in raw:
        return None, None
    try:
        ref = instrument_ref_from_sym_ticker(raw)
    except ValueError:
        return None, None
    return ref.base_asset, ref.quote_asset


def _positive_decimal(raw: str) -> Decimal | None:
    try:
        d = Decimal(str(raw).strip())
    except InvalidOperation:
        return None
    if d <= 0:
        return None
    return d


def _last_price_decimal_from_ticker_preview(prev: dict[str, Any]) -> Decimal | None:
    for key in ("lastPrice", "last", "closePrice"):
        v = prev.get(key)
        if v is None:
            continue
        try:
            dec = Decimal(str(v).strip())
        except InvalidOperation:
            continue
        if dec > 0:
            return dec
    return None


def _format_quote_estimate_amount(quote_ccy: str, notional: Decimal) -> str:
    """e.g. ``USDT:630.00`` — quote leg always **2** decimal places (display only)."""
    q = notional.quantize(_ESTIMATE_QUOTE_DISPLAY_QUANT, rounding=ROUND_HALF_UP)
    return f"{quote_ccy}:{q}"


async def _eval_confirmation_rules_for_type_a(
    session: AsyncSession,
    *,
    scenario_id: str,
    nominal_usdt: Decimal | None,
    turn_eid: str,
    anchor_id: int,
) -> tuple[str | None, str]:
    """Return (block_message, preamble_prefix). block_message set → do not offer Type-A."""
    try:
        eval_result = await evaluate_confirmation_for_trade(
            session,
            scenario_id=scenario_id,
            nominal_usdt=nominal_usdt,
        )
    except Exception:
        return None, ""

    await append_execution_timeline_event(
        session,
        execution_id=turn_eid,
        user_id=str(anchor_id),
        event_name="agent.execution.step",
        step_kind="confirm_gate",
        outcome="success" if not eval_result.block_auto_execute else "failure",
        payload={
            "scenarioId": scenario_id,
            "channel": "telegram",
            "transitionTrigger": "confirmation.rules_evaluated",
            "confirmationRules": eval_result.to_timeline_summary(),
        },
    )

    if eval_result.block_auto_execute:
        return format_block_auto_execute_message(), ""

    preamble = ""
    if eval_result.requires_second_confirm:
        preamble += format_second_confirm_preamble()
    if eval_result.requires_otp_confirm:
        preamble += format_otp_confirm_note()
    return None, preamble


def _format_limit_type_a_confirmation(
    slots: dict[str, str],
    *,
    base_asset: str | None,
    quote_asset: str | None,
    notional_quote: Decimal | None,
) -> str:
    sym = slots.get("symbol", "?")
    side = slots.get("side", "?")
    qty = slots.get("quantity", "?")
    price = slots.get("price", "?")
    tif = (slots.get("timeInForce") or "GTC").strip().upper() or "GTC"
    side_zh = "买入" if side == "BUY" else "卖出" if side == "SELL" else side
    qty_line = (
        f"数量：`{qty}` {base_asset}"
        if base_asset
        else f"数量（base）：`{qty}`"
    )
    lines = [
        "—— 现货限价单参数确认 ——",
        f"交易对：`{sym}`",
        f"方向：`{side_zh}`（`{side}`）",
        qty_line,
        f"限价：`{price}`",
        f"时效：`{tif}`",
    ]
    if quote_asset and notional_quote is not None:
        lines.append(_format_quote_estimate_amount(quote_asset, notional_quote))
    lines.append("")
    lines.append("请核对以上参数，并通过下方按钮完成二次确认。")
    return "\n".join(lines)


def _format_spot_amend_type_a_confirmation(
    *,
    symbol: str,
    side: str,
    order_id: str,
    prior_price: str,
    prior_quantity: str,
    new_price: str,
    new_quantity: str,
    time_in_force: str,
) -> str:
    side_zh = "买入" if side == "BUY" else "卖出" if side == "SELL" else side
    tif = (time_in_force or "GTC").strip().upper() or "GTC"
    return "\n".join(
        [
            "—— 修改现货限价挂单 ——",
            f"原委托 · `{symbol}` {side_zh} `{prior_quantity}` @ `{prior_price}`",
            f"新委托 · `{symbol}` {side_zh} `{new_quantity}` @ `{new_price}`",
            f"订单号：`{order_id}`",
            f"时效：`{tif}`",
            "",
            "将按「先撤销原单，再提交新单」处理（并非交易所原生一键改单）。",
            "请核对后点击「确认修改」。",
        ]
    )


def _format_futures_open_close_line(slots: dict[str, str]) -> str | None:
    oc = (slots.get("openClose") or "").strip().upper()
    if oc == "OPEN":
        return "开平：`开仓`（`OPEN`）"
    if oc == "CLOSE":
        return "开平：`平仓`（`CLOSE`）"
    return None


def _format_futures_market_type_a_confirmation(
    slots: dict[str, str],
    *,
    base_asset: str | None,
    quote_asset: str | None,
    notional_quote: Decimal | None,
) -> str:
    sym = slots.get("symbol", "?")
    side = slots.get("side", "?")
    qty = slots.get("quantity", "?")
    side_zh = "买入/做多" if side == "BUY" else "卖出/做空" if side == "SELL" else side
    qty_line = (
        f"数量：`{qty}` {base_asset}"
        if base_asset
        else f"数量（张/base）：`{qty}`"
    )
    lines = [
        "—— 合约市价单参数确认 ——",
        f"合约：`{sym}`",
        f"方向：`{side_zh}`（`{side}`）",
        qty_line,
    ]
    oc_line = _format_futures_open_close_line(slots)
    if oc_line:
        lines.append(oc_line)
    if quote_asset and notional_quote is not None:
        lines.append(
            _format_quote_estimate_amount(quote_asset, notional_quote)
            + "（按现货最新价估算，实际以合约成交为准）"
        )
    lines.append("")
    lines.append("请核对以上参数，并通过下方按钮完成二次确认。")
    return "\n".join(lines)


def _format_futures_limit_type_a_confirmation(
    slots: dict[str, str],
    *,
    base_asset: str | None,
    quote_asset: str | None,
    notional_quote: Decimal | None,
) -> str:
    sym = slots.get("symbol", "?")
    side = slots.get("side", "?")
    qty = slots.get("quantity", "?")
    price = slots.get("price", "?")
    side_zh = "买入/做多" if side == "BUY" else "卖出/做空" if side == "SELL" else side
    qty_line = (
        f"数量：`{qty}` {base_asset}"
        if base_asset
        else f"数量（张/base）：`{qty}`"
    )
    lines = [
        "—— 合约限价单参数确认 ——",
        f"合约：`{sym}`",
        f"方向：`{side_zh}`（`{side}`）",
        qty_line,
        f"限价：`{price}`",
    ]
    oc_line = _format_futures_open_close_line(slots)
    if oc_line:
        lines.append(oc_line)
    if quote_asset and notional_quote is not None:
        lines.append(_format_quote_estimate_amount(quote_asset, notional_quote))
    lines.append("")
    lines.append("请核对以上参数，并通过下方按钮完成二次确认。")
    return "\n".join(lines)


def _trigger_type_zh(trigger_type: str) -> str:
    tt = (trigger_type or "").strip().upper()
    if tt == "3UP":
        return "价格上涨至触发价时触发（3UP）"
    if tt == "4DOWN":
        return "价格下跌至触发价时触发（4DOWN）"
    return trigger_type


def _format_condition_type_a_confirmation(
    slots: dict[str, str],
    *,
    base_asset: str | None,
    order_type: str,
) -> str:
    sym = slots.get("symbol", "?")
    side = slots.get("side", "?")
    qty = slots.get("quantity", "?")
    tp = slots.get("triggerPrice", "?")
    tt = slots.get("triggerType", "?")
    side_zh = "买入/做多" if side == "BUY" else "卖出/做空" if side == "SELL" else side
    qty_disp = f"`{qty}` {base_asset}" if base_asset else f"`{qty}`"
    triggered = "市价" if order_type == "MARKET" else "限价"
    lines = [
        "**永续 · 条件委托**",
        "",
        "**触发条件（请先阅读）**",
        f"• 当价格 {_trigger_type_zh(tt)}",
        f"• 触发价：`{tp}`",
        "",
        "**触发后将提交的委托**",
        f"• **类型**　{triggered}（`{order_type}`）",
        f"• **合约**　`{sym}` · **方向**　`{side_zh}`（`{side}`）",
        f"• **数量**　{qty_disp}",
    ]
    if order_type == "LIMIT":
        lines.append(f"• **委托价**　`{slots.get('price', '?')}`")
    oc_line = _format_futures_open_close_line(slots)
    if oc_line:
        lines.append(f"• **开平**　{oc_line.split('：', 1)[-1]}")
    lines.extend(
        [
            "",
            "条件单与即时挂单不同；触发前不会在盘口展示为普通挂单。",
            "",
            "请核对后点击下方按钮。",
        ]
    )
    return "\n".join(lines)


def _format_margin_phase1_confirmation(
    slots: dict[str, str],
    *,
    order_type: str,
    base_asset: str | None,
    quote_asset: str | None,
    notional_quote: Decimal | None,
) -> str:
    sym = slots.get("symbol", "?")
    side = (slots.get("side") or "?").upper()
    qty = slots.get("quantity", "?")
    side_zh = "借钱买入" if side == "BUY" else "卖出/还款" if side == "SELL" else side
    qty_line = (
        f"数量：`{qty}` {base_asset}"
        if base_asset
        else f"数量（base）：`{qty}`"
    )
    lines = [
        f"—— 全仓杠杆{'市价' if order_type == 'MARKET' else '限价'} · 第一次确认 ——",
        "模式：`全仓 cross`",
        f"交易对：`{sym}`",
        f"方向：`{side_zh}`（`{side}`）",
        qty_line,
    ]
    if order_type == "LIMIT":
        lines.append(f"限价：`{slots.get('price', '?')}`")
    lines.append("借币计息：默认自动借入（浮动利率，以所内为准）。")
    if quote_asset and notional_quote is not None:
        lines.append(_format_quote_estimate_amount(quote_asset, notional_quote))
    lines.extend(
        [
            "",
            "下方确认后，还将有一张摘要卡进行二次确认，再向交易所提交下单。",
            "",
            "请核对以上参数，并通过下方按钮进入第二次确认。",
        ]
    )
    return "\n".join(lines)


def _format_flash_type_a_confirmation(
    slots: dict[str, str],
    *,
    base_asset: str | None,
    quote_asset: str | None,
    notional_quote: Decimal | None,
) -> str:
    sym = slots.get("symbol", "?")
    side = slots.get("side", "?")
    qty = slots.get("quantity", "?")
    side_zh = "买入" if side == "BUY" else "卖出" if side == "SELL" else side
    qty_line = f"数量：`{qty}` {base_asset}" if base_asset else f"数量：`{qty}`"
    lines = [
        "—— 现货闪兑（市价）参数确认 ——",
        f"交易对：`{sym}`",
        f"方向：`{side_zh}`（`{side}`）",
        qty_line,
    ]
    if quote_asset and notional_quote is not None:
        lines.append(_format_quote_estimate_amount(quote_asset, notional_quote))
    lines.append("")
    lines.append("请核对以上参数，并通过下方按钮完成二次确认。")
    return "\n".join(lines)


def _format_faq_hint(
    settings: Settings,
    best_sid: str | None,
    confidence: float,
    ranked: list[tuple[str, float]],
) -> str:
    lines = (
        "你还可以试着发送：\n"
        "• 「BTC-USDT 行情」或「看看 BTC 行情」\n"
        "• 「BTC-USDT 盘口」或「ETH 买卖盘」\n"
        "• 「BTC-USDT 近期成交」\n"
        "• 「账户余额」或「资产有多少」\n\n"
    )
    if settings.telegram_intent_preview_in_reply:
        alt = ranked[1][0] if len(ranked) > 1 else None
        alt_note = f" · 备选 `{alt}`" if alt else ""
        sid_disp = best_sid or "unknown"
        lines += f"（编排预览）粗略意图：`{sid_disp}` （confidence≈{confidence:.2f}{alt_note}）。"
    return lines


def _format_gate_denied(elig: EligibilityEnvelope) -> str:
    code = elig.code or "UNKNOWN"
    reason = elig.reason or "暂时无法继续。"
    return f"门禁未通过（`{code}`）。\n{reason}"


def _lines_from_ticker_preview(prev: dict[str, Any]) -> list[str]:
    labels: dict[str, str] = {
        "symbol": "交易所原始 symbol",
        "symbolRequested": "请求交易对",
        "lastPrice": "最新价",
        "bidPrice": "买一",
        "askPrice": "卖一",
        "volume": "成交量（base）",
        "quoteVolume": "成交额（quote）",
        "highPrice": "24h 高",
        "lowPrice": "24h 低",
        "openPrice": "开盘价",
        "prevClosePrice": "昨收",
        "priceChangePercent": "涨跌幅",
        "lastQty": "最新成交量",
    }
    lines: list[str] = ["—— 现货行情（只读 GET /sapi/v2/ticker）——"]
    for key, zh in labels.items():
        if key not in prev:
            continue
        val = prev[key]
        lines.append(f"{zh}：`{val}`")
    return lines


def _lines_from_balance_preview(prev: dict[str, Any]) -> list[str]:
    lines: list[str] = ["—— 现货账户余额摘要（只读 GET /sapi/v1/account）——"]
    at = prev.get("accountTypeHint")
    if isinstance(at, str) and at.strip():
        lines.append(f"账户类型提示：`{at.strip()}`")
    ct = prev.get("canTradeHint")
    if isinstance(ct, bool):
        lines.append(f"可交易：`{'是' if ct else '否'}`")

    items = prev.get("items")
    if not isinstance(items, list) or not items:
        lines.append("暂无余额条目或未返回 balances。")
        lines.append("场景 ID：`read.account.balance`")
        return lines

    def nz_score(it: dict[str, Any]) -> tuple[int, str]:
        asset = str(it.get("asset", ""))
        free_s = str(it.get("free", "0"))
        locked_s = str(it.get("locked", "0"))
        try:
            fz = float(free_s)
            lz = float(locked_s)
        except ValueError:
            return (1, asset)
        if fz != 0 or lz != 0:
            return (0, asset)
        return (2, asset)

    dict_rows = [x for x in items if isinstance(x, dict)]
    dict_rows.sort(key=lambda r: nz_score(r))
    shown = 0
    for it in dict_rows[:28]:
        asset = str(it.get("asset", "")).strip().upper()
        if not asset:
            continue
        free_s = str(it.get("free", "0"))[:48]
        locked_s = str(it.get("locked", "0"))[:48]
        lines.append(f"{asset} —— 可用 `{free_s}` · 冻结 `{locked_s}`")
        shown += 1
    if shown == 0:
        lines.append("暂无余额条目。")
    if len(dict_rows) > shown:
        lines.append(f"… 其余 {len(dict_rows) - shown} 条已省略（摘要上限）。")

    lines.append("场景 ID：`read.account.balance`")
    return lines


def _lines_from_wealth_holdings_preview(prev: dict[str, Any]) -> list[str]:
    """Telegram 文本化 ``wealth.holdings_read`` — balances 形状复用现货摘要逻辑。"""
    if isinstance(prev.get("items"), list):
        shadow = {**prev, "kind": "spot_account_balances_filtered"}
        lines = _lines_from_balance_preview(shadow)
        lines[0] = "—— 理财/OTC 持仓摘要（只读 POST /sapi/v1/asset/account/by_type）——"
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].startswith("场景 ID："):
                lines[i] = "场景 ID：`wealth.holdings_read`"
                break
        else:
            lines.append("场景 ID：`wealth.holdings_read`")
        return lines

    lines = ["—— 理财/OTC 持仓摘要（只读 POST /sapi/v1/asset/account/by_type）——"]
    if prev.get("accountTypeRequested") is not None:
        lines.append(f"请求 accountType：`{prev.get('accountTypeRequested')}`")
    samples = prev.get("assetsSample")
    if isinstance(samples, list) and samples:
        lines.append("资产抽样：")
        for row in samples[:16]:
            if not isinstance(row, dict):
                continue
            bits = " · ".join(f"{k} `{v}`" for k, v in row.items())
            if bits:
                lines.append(bits)
    else:
        lines.append("暂无可展示条目（响应 shape 与预期不一致时可查 OpenAPI 原始字段）。")
    lines.append("场景 ID：`wealth.holdings_read`")
    return lines


def _lines_from_depth_preview(prev: dict[str, Any]) -> list[str]:
    lim = prev.get("limitRequested")
    lim_s = str(lim) if lim is not None else "?"
    lines: list[str] = [f"—— 现货盘口深度（只读 GET /sapi/v2/depth，每侧最多 {lim_s} 档）——"]
    for label, key in (("卖盘 asks", "asks"), ("买盘 bids", "bids")):
        rows = prev.get(key)
        if not isinstance(rows, list) or not rows:
            lines.append(f"{label}：暂无数据")
            continue
        bits: list[str] = []
        for pair in rows[:20]:
            if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                bits.append(f"{pair[0]} × {pair[1]}")
        lines.append(f"{label}：`{' | '.join(bits)}`" if bits else f"{label}：暂无有效档位")
    return lines


def _lines_from_open_orders_preview(prev: dict[str, Any]) -> list[str]:
    lines = ["**现货当前委托**"]
    sym_f = prev.get("symbolFilter") or prev.get("symbolOrderFilter")
    if sym_f:
        lines.append(f"筛选交易对：`{sym_f}`")
    items = prev.get("items")
    if not isinstance(items, list) or not items:
        lines.append("当前无未完成委托。")
        return lines
    oc = prev.get("orderCount")
    if isinstance(oc, int) and oc > len(items):
        lines.append(f"共 {oc} 笔，以下展示前 {len(items)} 笔：")
    for i, row in enumerate(items[:12], start=1):
        if not isinstance(row, dict):
            continue
        oid = row.get("orderIdString") or row.get("orderId") or "—"
        sym = row.get("symbol") or "—"
        side = row.get("side") or "—"
        typ = row.get("type") or "—"
        price = row.get("price") or "—"
        qty = row.get("origQty") or row.get("quantity") or "—"
        status = row.get("status") or "—"
        lines.append(
            f"{i}. `{sym}` {side} {typ} 价 {price} 量 {qty} · 单号 `{oid}` · {status}"
        )
    if len(items) > 12:
        lines.append(f"… 另有 {len(items) - 12} 笔未展开。")
    return lines


def _format_spot_cancel_success(out: dict[str, Any]) -> str:
    oid = out.get("orderIdString") or out.get("orderId") or "—"
    sym = out.get("symbol") or "—"
    status = out.get("status") or "—"
    return (
        f"撤单已提交。\n"
        f"交易对：`{sym}`\n"
        f"订单号：`{oid}`\n"
        f"状态：`{status}`\n"
        f"场景 ID：`trade.spot.cancel_order`"
    )


def _format_futures_cancel_success(out: dict[str, Any]) -> str:
    oid = out.get("orderIdString") or out.get("orderId") or "—"
    sym = out.get("symbol") or out.get("contractName") or "—"
    status = out.get("status") or "—"
    sid = out.get("scenarioId") or "trade.futures.cancel_order"
    return (
        f"合约撤单已提交。\n"
        f"标的：`{sym}`\n"
        f"订单号：`{oid}`\n"
        f"状态：`{status}`\n"
        f"场景 ID：`{sid}`"
    )


def _lines_from_condition_orders_payload(payload: dict[str, Any]) -> list[str]:
    lines: list[str] = ["—— 合约条件单 / 计划委托（只读）——"]
    items = payload.get("orders")
    if not isinstance(items, list) or not items:
        lines.append("暂无条件单在途委托。")
        return lines
    for i, it in enumerate(items[:12], start=1):
        if not isinstance(it, dict):
            continue
        cn = it.get("contractName") or it.get("symbol") or "—"
        side = it.get("side") or "—"
        tp = it.get("triggerPrice") or "—"
        tt = it.get("triggerType") or "—"
        oid = it.get("orderIdString") or it.get("orderId") or "—"
        status = it.get("status") or "—"
        lines.append(
            f"{i}. `{cn}` {side} 触发 {tp}（{tt}）· 单号 `{oid}` · {status}"
        )
    if len(items) > 12:
        lines.append(f"… 另有 {len(items) - 12} 笔未展开。")
    total = payload.get("totalOpenOrders")
    if total is not None:
        lines.append(f"（开放委托合计 {total} 笔，上表仅条件/计划单。）")
    return lines


def _lines_from_trades_preview(prev: dict[str, Any]) -> list[str]:
    lines: list[str] = ["—— 现货近期成交（只读 GET /sapi/v2/trades）——"]
    items = prev.get("items")
    if not isinstance(items, list) or not items:
        lines.append("暂无成交记录。")
        return lines
    shown = 0
    for it in items[:18]:
        if not isinstance(it, dict):
            continue
        price = it.get("price", "?")
        qty = it.get("qty") if it.get("qty") is not None else it.get("quantity", "?")
        side = it.get("side", "")
        tid = it.get("id", "")
        tail = f" · id `{tid}`" if tid else ""
        side_s = f" `{side}`" if side else ""
        lines.append(f"价 `{price}` · 量 `{qty}`{side_s}{tail}")
        shown += 1
    if shown == 0:
        lines.append("暂无成交记录。")
    if len(items) > shown:
        lines.append(f"… 其余 {len(items) - shown} 条已省略（摘要上限）。")
    return lines


async def build_telegram_bound_user_reply(
    *,
    settings: Settings,
    session: AsyncSession,
    anchor_id: int,
    chat_id: int,
    user_text: str,
) -> tuple[str, dict[str, Any] | None]:
    from chainup_agent.core.config import get_effective_settings

    settings = get_effective_settings(settings)
    elig = await evaluate_eligibility(
        session=session,
        settings=settings,
        body=EvaluateEligibilityRequest(
            user_id=str(anchor_id),
            channel="telegram",
            scenario_id=None,
            telegram_chat_id=chat_id,
        ),
    )
    if not elig.allowed:
        denied = _format_gate_denied(elig)
        return _lead(denied), None

    caps_raw = elig.capabilities
    caps = caps_raw if isinstance(caps_raw, dict) else None
    allow_hint = _allowlist_binding_hint(caps)

    tg_sid = telegram_session_id(chat_id)
    mem_cmd = try_memory_command_intent(user_text)
    if mem_cmd:

        async def _memory_compute(turn_eid: str) -> tuple[str, dict[str, Any] | None, bool]:
            body = await handle_telegram_memory_command(
                session,
                intent=mem_cmd,
                user_id=str(anchor_id),
                session_id=tg_sid,
                execution_id=turn_eid,
            )
            return body + allow_hint, None, False

        raw, markup = await run_telegram_turn_execution(
            session,
            user_id=str(anchor_id),
            scenario_id="agent.runtime.memory",
            compute=_memory_compute,
        )
        record_telegram_stm_turn(
            session_id=tg_sid,
            user_id=str(anchor_id),
            user_text=user_text,
            assistant_text=raw,
        )
        return _lead(raw), markup

    merged_defaults, _gw_ver = await read_gateway_defaults_merged(session)
    narrate_effective = build_effective_telegram_llm_narrate_map(settings, merged_defaults)

    from chainup_agent.application.memory_session_store import (
        get_session_context_preview as _mem_ctx,
        register_pending_type_a,
    )
    from chainup_agent.application.clarify_inbound import preprocess_clarify_inbound
    from chainup_agent.application.session_concurrency import (
        block_second_write_message,
        register_active_write_execution,
    )
    from chainup_agent.application.session_execution_gate import (
        telegram_user_has_pending_type_a_confirm,
        telegram_user_has_unknown_write_execution,
    )

    mem_preview = _mem_ctx(tg_sid, str(anchor_id))
    pending_type_a = bool(mem_preview.get("pendingTypeAValid")) or (
        await telegram_user_has_pending_type_a_confirm(session, anchor_id)
    )
    unknown_pending = await telegram_user_has_unknown_write_execution(session, anchor_id)
    pre = preprocess_clarify_inbound(
        session_id=tg_sid,
        user_text=user_text,
        settings=settings,
        pending_type_a=pending_type_a,
    )
    if not pre.proceed_to_intent and pre.early_reply:
        record_telegram_stm_turn(
            session_id=tg_sid,
            user_id=str(anchor_id),
            user_text=user_text,
            assistant_text=pre.early_reply,
        )
        return _lead(pre.early_reply), None
    block_msg = block_second_write_message(
        session_id=tg_sid,
        user_text=user_text,
        settings=settings,
        pending_type_a=pending_type_a,
        unknown_pending=unknown_pending,
    )
    resume_obs = pre.resume_observability
    if block_msg:
        record_telegram_stm_turn(
            session_id=tg_sid,
            user_id=str(anchor_id),
            user_text=user_text,
            assistant_text=block_msg,
        )
        return _lead(block_msg), None

    ir = await recognize_intent_full(
        settings=settings,
        text=user_text,
        session_id=tg_sid,
        user_id=str(anchor_id),
        previous_scenario_id=previous_scenario_for_session(tg_sid),
        session=session,
    )
    plan = ir.plan
    nlu = ir.nlu
    exec_sid = (plan.resolved_scenario_id if plan else None) or ir.scenario_id or "chat.faq"
    remember_resolved_scenario(tg_sid, exec_sid)

    from chainup_agent.application.clarify_inbound import (
        maybe_start_read_clarify,
        read_clarify_reply_after_intent,
    )

    maybe_start_read_clarify(
        session_id=tg_sid,
        scenario_id=exec_sid,
        slots=dict(nlu.slots) if nlu and nlu.slots else None,
        settings=settings,
        user_text=user_text,
    )
    read_early = read_clarify_reply_after_intent(
        session_id=tg_sid,
        effective_locale=ir.effective_locale,
    )
    if read_early is not None:
        read_body, read_markup = read_early
        record_telegram_stm_turn(
            session_id=tg_sid,
            user_id=str(anchor_id),
            user_text=user_text,
            assistant_text=read_body,
        )
        return _lead(read_body), read_markup

    async def _compose_allowed_reply(turn_eid: str) -> tuple[str, dict[str, Any] | None, bool]:
        if resume_obs:
            await append_execution_timeline_event(
                session,
                execution_id=resume_obs.get("executionId") or turn_eid,
                user_id=str(anchor_id),
                event_name="agent.memory.resume_classified",
                step_kind="memory",
                outcome="success",
                payload={
                    **resume_obs,
                    "sessionId": tg_sid,
                    "transitionTrigger": "memory.resume_classified",
                },
            )
        await _append_intent_nlu_prompt_timeline(
            session,
            settings,
            execution_id=turn_eid,
            user_id=str(anchor_id),
            ir=ir,
            plan=plan,
            exec_scenario_id=exec_sid,
        )
        if not plan:
            body = _format_faq_hint(settings, None, 0.0, []) + allow_hint
            return body, None, False

        step = plan.next_step
        nlu_slots_resolved: dict[str, str] | None = None
        if step == "CLARIFY":
            from chainup_agent.application.telegram_clarify_outbound import (
                build_clarify_reply_markup,
            )

            slots_for_clarify = dict(nlu.slots) if nlu and nlu.slots else {}
            body = await _telegram_clarify_reply_body(
                session,
                settings,
                user_text=user_text,
                plan=plan,
                nlu_slots=slots_for_clarify,
                turn_eid=turn_eid,
                anchor_id=anchor_id,
                chat_id=chat_id,
                effective_locale=ir.effective_locale,
            )
            markup = build_clarify_reply_markup(
                scenario_id=plan.resolved_scenario_id or exec_sid,
                slots=slots_for_clarify,
                policy_codes=list(plan.policy_codes or []),
                effective_locale=ir.effective_locale,
                session_id=tg_sid,
                settings=settings,
            )
            register_active_write_execution(tg_sid, turn_eid)
            return body + allow_hint, markup, False
        if step in ("RESOLVE_FLASH_NOTIONAL", "RESOLVE_TRADE_NOTIONAL"):
            rid_nf = plan.resolved_scenario_id or ""
            if rid_nf not in SCENARIOS_USING_SPOT_NOTIONAL_RESOLVE:
                from chainup_agent.application.telegram_clarify_outbound import (
                    build_clarify_reply_markup,
                )

                nf_slots = dict(nlu.slots) if nlu and nlu.slots else {}
                body = await _telegram_clarify_reply_body(
                    session,
                    settings,
                    user_text=user_text,
                    plan=plan,
                    nlu_slots=nf_slots,
                    turn_eid=turn_eid,
                    anchor_id=anchor_id,
                    chat_id=chat_id,
                    effective_locale=ir.effective_locale,
                )
                nf_markup = build_clarify_reply_markup(
                    scenario_id=plan.resolved_scenario_id or exec_sid,
                    slots=nf_slots,
                    policy_codes=list(plan.policy_codes or []),
                    effective_locale=ir.effective_locale,
                    session_id=tg_sid,
                    settings=settings,
                )
                return body + allow_hint, nf_markup, False
            slots_try = dict(nlu.slots) if nlu and nlu.slots else {}
            resolved_slots, err_nf = await resolve_trade_notional_slots(
                session=session,
                settings=settings,
                user_id=str(anchor_id),
                slots=slots_try,
            )
            if err_nf:
                return err_nf + allow_hint, None, False
            clear_pending_clarify(tg_sid)
            step = "CONFIRM_TYPE_A"
            nlu_slots_resolved = resolved_slots
        if step == "UNKNOWN":
            if plan.clarify:
                return _format_plan_clarify(plan) + allow_hint, None, False
            return "暂时无法识别意图，请换种说法。" + allow_hint, None, False
        if step == "BLOCKED_FEATURE":
            return _format_blocked_feature(plan) + allow_hint, None, False
        if step == "STUB_NOT_EXECUTABLE":
            sid = plan.resolved_scenario_id or "trade.unknown"
            return _format_trade_stub(sid) + allow_hint, None, False
        if step == "ROUTE_CHAT_FAQ":
            faq_sid = plan.resolved_scenario_id or "chat.faq"
            faq_rtc = merge_stm_runtime_context(
                session_id=tg_sid,
                user_id=str(anchor_id),
            )
            assistant, llm_err, llm_obs = await invoke_llm_chat_for_telegram(
                session=session,
                settings=settings,
                user_text=user_text,
                scenario_id=faq_sid,
                execution_id=turn_eid,
                session_id=tg_sid,
                runtime_context=faq_rtc,
            )
            faq_ver, faq_bind = await effective_prompt_snapshot_for_scenario(
                session, scenario_id=faq_sid
            )
            outcome = "success" if assistant else "failure"
            await append_execution_timeline_event(
                session,
                execution_id=turn_eid,
                user_id=str(anchor_id),
                event_name="llm.chat.faq",
                step_kind="chat_faq",
                outcome=outcome,
                payload={
                    "scenarioId": faq_sid,
                    "promptPackVersion": faq_ver,
                    "resolvedPromptBinding": faq_bind,
                    **(llm_obs or {}),
                    "userVisibleError": (llm_err or "")[:500] if not assistant else None,
                },
            )
            if assistant:
                return assistant + allow_hint, None, False
            msg = llm_err or "暂时无法调用 LLM。"
            body = msg + "\n\n" + _format_faq_hint(settings, faq_sid, ir.confidence, [])
            return body + allow_hint, None, False
        if step == "ROUTE_READ_SKILL":
            sid = plan.resolved_scenario_id
            if sid == "read.market.ticker":
                sym = _resolve_read_symbol_for_telegram(
                    nlu=nlu, user_text=user_text, session_id=tg_sid
                )
                if not sym:
                    hint = (
                        "如需查询现货行情，请在消息里带上交易对，例如：`BTC-USDT`、"
                        "`ETH/USDT` 或单独写 `BTC`（默认按 BTC-USDT）。\n\n"
                        + _format_faq_hint(settings, sid, ir.confidence, [])
                    )
                    return hint + allow_hint, None, False
                req = routing_telegram_read_request(
                    telegram_user_id=anchor_id,
                    user_text=user_text,
                    scenario_id=sid or "read.market.ticker",
                    symbol=sym,
                )
                try:
                    routed = await routing_execute_exchange_reads(
                        session=session,
                        settings=settings,
                        body=req,
                    )
                except AppError as exc:
                    await append_routing_execute_timeline(
                        session,
                        execution_id=turn_eid,
                        user_id=str(anchor_id),
                        body=req,
                        response=None,
                        outcome="failure",
                        app_error=exc,
                    )
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc),
                        None,
                        False,
                    )
                await append_routing_execute_timeline(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    body=req,
                    response=routed,
                    outcome="success",
                )
                prev = routed.exchange_read_preview or {}
                prev_d = prev if isinstance(prev, dict) else {}
                narr = await _try_telegram_public_read_llm_narration(
                    session=session,
                    settings=settings,
                    enabled=narrate_effective["readMarketTicker"],
                    scenario_id="read.market.ticker",
                    user_text=user_text,
                    turn_eid=turn_eid,
                    chat_id=chat_id,
                    anchor_id=anchor_id,
                    effective_locale=ir.effective_locale,
                    exchange_read_preview=prev_d,
                    routing_note=routed.note,
                    event_name="llm.read.market.ticker",
                    step_kind="read_market_ticker_llm",
                    source_attribution_footer=(
                        "\n\n—\n数据来源：现货公共 ticker（只读）；\n"
                        "场景 **`read.market.ticker`**。\n"
                        "若数据与盘面不一致，请以交易所客户端为准。"
                    ),
                )
                if narr:
                    remember_pending_clarify(
                        tg_sid,
                        scenario_id="read.market.ticker",
                        slots={"symbol": sym},
                    )
                    return narr + allow_hint, None, False
                lines = _lines_from_ticker_preview(prev_d)
                lines.append("场景 ID：`read.market.ticker`")
                note = routed.note or ""
                if note:
                    lines.append(note)
                remember_pending_clarify(
                    tg_sid,
                    scenario_id="read.market.ticker",
                    slots={"symbol": sym},
                )
                return "\n".join(lines) + allow_hint, None, False
            if sid == "read.market.depth":
                sym = _resolve_read_symbol_for_telegram(
                    nlu=nlu, user_text=user_text, session_id=tg_sid
                )
                if not sym:
                    hint = (
                        "如需查询现货盘口深度，请在消息里带上交易对，例如：`BTC-USDT`、"
                        "`ETH/USDT` 或单独写 `BTC`（默认按 BTC-USDT）。\n\n"
                        + _format_faq_hint(settings, sid, ir.confidence, [])
                    )
                    return hint + allow_hint, None, False
                req = routing_telegram_read_request(
                    telegram_user_id=anchor_id,
                    user_text=user_text,
                    scenario_id=sid or "read.market.depth",
                    symbol=sym,
                )
                try:
                    routed = await routing_execute_exchange_reads(
                        session=session,
                        settings=settings,
                        body=req,
                    )
                except AppError as exc:
                    await append_routing_execute_timeline(
                        session,
                        execution_id=turn_eid,
                        user_id=str(anchor_id),
                        body=req,
                        response=None,
                        outcome="failure",
                        app_error=exc,
                    )
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc),
                        None,
                        False,
                    )
                await append_routing_execute_timeline(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    body=req,
                    response=routed,
                    outcome="success",
                )
                prev = routed.exchange_read_preview or {}
                prev_d = prev if isinstance(prev, dict) else {}
                narr = await _try_telegram_public_read_llm_narration(
                    session=session,
                    settings=settings,
                    enabled=narrate_effective["readMarketDepth"],
                    scenario_id="read.market.depth",
                    user_text=user_text,
                    turn_eid=turn_eid,
                    chat_id=chat_id,
                    anchor_id=anchor_id,
                    effective_locale=ir.effective_locale,
                    exchange_read_preview=prev_d,
                    routing_note=routed.note,
                    event_name="llm.read.market.depth",
                    step_kind="read_market_depth_llm",
                    source_attribution_footer=(
                        "\n\n—\n数据来源：现货公开盘口深度（只读）；\n"
                        "场景 **`read.market.depth`**。\n"
                        "若数据与盘面不一致，请以交易所客户端为准。"
                    ),
                )
                if narr:
                    remember_pending_clarify(
                        tg_sid,
                        scenario_id="read.market.depth",
                        slots={"symbol": sym},
                    )
                    return narr + allow_hint, None, False
                lines = _lines_from_depth_preview(prev_d)
                lines.append("场景 ID：`read.market.depth`")
                note = routed.note or ""
                if note:
                    lines.append(note)
                remember_pending_clarify(
                    tg_sid,
                    scenario_id="read.market.depth",
                    slots={"symbol": sym},
                )
                return "\n".join(lines) + allow_hint, None, False
            if sid == "read.market.trades":
                sym = _resolve_read_symbol_for_telegram(
                    nlu=nlu, user_text=user_text, session_id=tg_sid
                )
                if not sym:
                    hint = (
                        "如需查询现货近期成交，请在消息里带上交易对，例如：`BTC-USDT`、"
                        "`ETH/USDT` 或单独写 `BTC`（默认按 BTC-USDT）。\n\n"
                        + _format_faq_hint(settings, sid, ir.confidence, [])
                    )
                    return hint + allow_hint, None, False
                req = routing_telegram_read_request(
                    telegram_user_id=anchor_id,
                    user_text=user_text,
                    scenario_id=sid or "read.market.trades",
                    symbol=sym,
                )
                try:
                    routed = await routing_execute_exchange_reads(
                        session=session,
                        settings=settings,
                        body=req,
                    )
                except AppError as exc:
                    await append_routing_execute_timeline(
                        session,
                        execution_id=turn_eid,
                        user_id=str(anchor_id),
                        body=req,
                        response=None,
                        outcome="failure",
                        app_error=exc,
                    )
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc),
                        None,
                        False,
                    )
                await append_routing_execute_timeline(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    body=req,
                    response=routed,
                    outcome="success",
                )
                prev = routed.exchange_read_preview or {}
                prev_d = prev if isinstance(prev, dict) else {}
                narr = await _try_telegram_public_read_llm_narration(
                    session=session,
                    settings=settings,
                    enabled=narrate_effective["readMarketTrades"],
                    scenario_id="read.market.trades",
                    user_text=user_text,
                    turn_eid=turn_eid,
                    chat_id=chat_id,
                    anchor_id=anchor_id,
                    effective_locale=ir.effective_locale,
                    exchange_read_preview=prev_d,
                    routing_note=routed.note,
                    event_name="llm.read.market.trades",
                    step_kind="read_market_trades_llm",
                    source_attribution_footer=(
                        "\n\n—\n数据来源：现货公开近期成交（只读）；\n"
                        "场景 **`read.market.trades`**。\n"
                        "若数据与盘面不一致，请以交易所客户端为准。"
                    ),
                )
                if narr:
                    remember_pending_clarify(
                        tg_sid,
                        scenario_id="read.market.trades",
                        slots={"symbol": sym},
                    )
                    return narr + allow_hint, None, False
                lines = _lines_from_trades_preview(prev_d)
                lines.append("场景 ID：`read.market.trades`")
                note = routed.note or ""
                if note:
                    lines.append(note)
                remember_pending_clarify(
                    tg_sid,
                    scenario_id="read.market.trades",
                    slots={"symbol": sym},
                )
                return "\n".join(lines) + allow_hint, None, False
            if sid == "read.account.balance":
                req = routing_telegram_read_request(
                    telegram_user_id=anchor_id,
                    user_text=user_text,
                    scenario_id=sid or "read.account.balance",
                )
                try:
                    routed = await routing_execute_exchange_reads(
                        session=session,
                        settings=settings,
                        body=req,
                    )
                except AppError as exc:
                    await append_routing_execute_timeline(
                        session,
                        execution_id=turn_eid,
                        user_id=str(anchor_id),
                        body=req,
                        response=None,
                        outcome="failure",
                        app_error=exc,
                    )
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc),
                        None,
                        False,
                    )
                await append_routing_execute_timeline(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    body=req,
                    response=routed,
                    outcome="success",
                )
                prev = routed.exchange_read_preview or {}
                prev_d = prev if isinstance(prev, dict) else {}
                narr = await _try_telegram_public_read_llm_narration(
                    session=session,
                    settings=settings,
                    enabled=narrate_effective["readAccountBalance"],
                    scenario_id="read.account.balance",
                    user_text=user_text,
                    turn_eid=turn_eid,
                    chat_id=chat_id,
                    anchor_id=anchor_id,
                    effective_locale=ir.effective_locale,
                    exchange_read_preview=prev_d,
                    routing_note=routed.note,
                    event_name="llm.read.account.balance",
                    step_kind="read_account_balance_llm",
                    source_attribution_footer=(
                        "\n\n—\n数据来源：账户余额只读摘要；\n"
                        "场景 **`read.account.balance`**。\n"
                        "若与交易所客户端不一致，请以官方界面为准。"
                    ),
                )
                if narr:
                    return narr + allow_hint, None, False
                lines = _lines_from_balance_preview(prev_d)
                note = routed.note or ""
                if note:
                    lines.append(note)
                return "\n".join(lines) + allow_hint, None, False
            if sid == "wealth.holdings_read":
                req = routing_telegram_read_request(
                    telegram_user_id=anchor_id,
                    user_text=user_text,
                    scenario_id=sid or "wealth.holdings_read",
                )
                try:
                    routed = await routing_execute_exchange_reads(
                        session=session,
                        settings=settings,
                        body=req,
                    )
                except AppError as exc:
                    await append_routing_execute_timeline(
                        session,
                        execution_id=turn_eid,
                        user_id=str(anchor_id),
                        body=req,
                        response=None,
                        outcome="failure",
                        app_error=exc,
                    )
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc),
                        None,
                        False,
                    )
                await append_routing_execute_timeline(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    body=req,
                    response=routed,
                    outcome="success",
                )
                prev = routed.exchange_read_preview or {}
                prev_d = prev if isinstance(prev, dict) else {}
                narr = await _try_telegram_public_read_llm_narration(
                    session=session,
                    settings=settings,
                    enabled=narrate_effective["wealthHoldingsRead"],
                    scenario_id="wealth.holdings_read",
                    user_text=user_text,
                    turn_eid=turn_eid,
                    chat_id=chat_id,
                    anchor_id=anchor_id,
                    effective_locale=ir.effective_locale,
                    exchange_read_preview=prev_d,
                    routing_note=routed.note,
                    event_name="llm.wealth.holdings_read",
                    step_kind="wealth_holdings_read_llm",
                    source_attribution_footer=(
                        "\n\n—\n数据来源：理财/OTC 持仓只读摘要；\n"
                        "场景 **`wealth.holdings_read`**。\n"
                        "若与交易所客户端不一致，请以官方界面为准。"
                    ),
                )
                if narr:
                    return narr + allow_hint, None, False
                lines = _lines_from_wealth_holdings_preview(prev_d)
                note = routed.note or ""
                if note:
                    lines.append(note)
                return "\n".join(lines) + allow_hint, None, False
            if sid == "trade.spot.open_orders":
                sym = (nlu.slots.get("symbol") if nlu and nlu.slots else None) or None
                req = routing_telegram_read_request(
                    telegram_user_id=anchor_id,
                    user_text=user_text,
                    scenario_id=sid or "trade.spot.open_orders",
                    symbol=sym,
                    market_data_limit=50,
                )
                try:
                    routed = await routing_execute_exchange_reads(
                        session=session,
                        settings=settings,
                        body=req,
                    )
                except AppError as exc:
                    await append_routing_execute_timeline(
                        session,
                        execution_id=turn_eid,
                        user_id=str(anchor_id),
                        body=req,
                        response=None,
                        outcome="failure",
                        app_error=exc,
                    )
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc),
                        None,
                        False,
                    )
                await append_routing_execute_timeline(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    body=req,
                    response=routed,
                    outcome="success",
                )
                prev_d = routed.exchange_read_preview or {}
                prev_dict = prev_d if isinstance(prev_d, dict) else {}
                lines = _lines_from_open_orders_preview(prev_dict)
                lines.append("场景 ID：`trade.spot.open_orders`")
                note = routed.note or ""
                if note:
                    lines.append(note)
                return "\n".join(lines) + allow_hint, None, False
            if sid == "automation.condition_orders_read":
                slots_dict = dict(nlu.slots) if nlu and nlu.slots else {}
                sym = (slots_dict.get("symbol") or "").strip() or None
                try:
                    payload = await futures_condition_orders_for_bound_user(
                        session=session,
                        settings=settings,
                        user_id=str(anchor_id),
                        symbol=sym,
                    )
                except AppError as exc:
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc),
                        None,
                        False,
                    )
                lines = _lines_from_condition_orders_payload(payload)
                lines.append("场景 ID：`automation.condition_orders_read`")
                return "\n".join(lines) + allow_hint, None, False
            return _format_faq_hint(settings, sid, ir.confidence, []) + allow_hint, None, False
        if step == "EXECUTE_SPOT_CANCEL":
            slots_dict = dict(nlu.slots) if nlu and nlu.slots else {}
            sym = (slots_dict.get("symbol") or "").strip()
            oid = (slots_dict.get("orderId") or "").strip() or None
            ncid = (slots_dict.get("newClientOrderId") or "").strip() or None
            if not sym or (not oid and not ncid):
                return _format_plan_clarify(plan) + allow_hint, None, False
            try:
                out = await spot_cancel_order_for_bound_user(
                    session=session,
                    settings=settings,
                    user_id=str(anchor_id),
                    symbol=sym,
                    order_id=oid,
                    new_client_order_id=ncid,
                    timeline_execution_id=turn_eid,
                    timeline_channel="telegram",
                )
            except AppError as exc:
                return (
                    await format_app_error_reply_for_telegram(session, settings, exc),
                    None,
                    False,
                )
            return _format_spot_cancel_success(out) + allow_hint, None, False
        if step == "EXECUTE_FUTURES_CANCEL":
            slots_dict = dict(nlu.slots) if nlu and nlu.slots else {}
            sym = (slots_dict.get("symbol") or "").strip()
            oid = (slots_dict.get("orderId") or "").strip() or None
            if not sym or not oid:
                return _format_plan_clarify(plan) + allow_hint, None, False
            try:
                out = await futures_cancel_order_for_bound_user(
                    session=session,
                    settings=settings,
                    user_id=str(anchor_id),
                    symbol=sym,
                    order_id=oid,
                    timeline_execution_id=turn_eid,
                    timeline_channel="telegram",
                )
            except AppError as exc:
                return (
                    await format_app_error_reply_for_telegram(session, settings, exc),
                    None,
                    False,
                )
            return _format_futures_cancel_success(out) + allow_hint, None, False
        if step == "CONFIRM_TYPE_A":
            slots_dict = (
                nlu_slots_resolved
                if nlu_slots_resolved is not None
                else (dict(nlu.slots) if nlu and nlu.slots else {})
            )
            sym = (slots_dict.get("symbol") or "").strip()
            side = (slots_dict.get("side") or "").strip().upper()
            qty = (slots_dict.get("quantity") or "").strip()
            rid = plan.resolved_scenario_id or ""

            if write_path_has_skill_spec(rid):
                try:
                    await ensure_write_path_skill_spec_read(
                        session,
                        execution_id=turn_eid,
                        user_id=str(anchor_id),
                        scenario_id=rid,
                        channel="telegram",
                    )
                except AppError as exc:
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc)
                    ) + allow_hint, None, False

            if rid == "trade.spot.limit_order":
                price = (slots_dict.get("price") or "").strip()
                tif = (slots_dict.get("timeInForce") or "GTC").strip().upper() or "GTC"
                quote_qty_lim = (slots_dict.get("quoteQty") or "").strip()
                if not qty and quote_qty_lim and side == "BUY" and price:
                    px_d = _positive_decimal(price)
                    if px_d is None:
                        return (
                            "限价须为有效正数，请重新输入价格。"
                            + allow_hint,
                            None,
                            False,
                        )
                    try:
                        qty = quote_qty_to_base_at_limit_price(
                            quote_qty=quote_qty_lim,
                            limit_price=px_d,
                        )
                        slots_dict = {**slots_dict, "quantity": qty}
                    except AppError as exc:
                        return (
                            await format_app_error_reply_for_telegram(
                                session, settings, exc
                            )
                        ) + allow_hint, None, False
                if not sym or side not in ("BUY", "SELL") or not qty or not price:
                    return (
                        (
                            _format_plan_clarify(plan)
                            if plan.clarify
                            else (
                                "限价单参数不完整，请补充交易对、方向（买/卖）、"
                                "数量（base）与限价。"
                            )
                        )
                        + allow_hint,
                        None,
                        False,
                    )
                try:
                    qp = await spot_quote_for_bound_user(
                        session=session,
                        settings=settings,
                        user_id=str(anchor_id),
                        symbol=sym,
                    )
                except AppError as exc:
                    return (
                        (await format_app_error_reply_for_telegram(session, settings, exc))
                        + allow_hint
                    ), None, False
                qp_prev = qp.get("quotePreview") if isinstance(qp.get("quotePreview"), dict) else {}
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="quote",
                    outcome="success",
                    payload={
                        "scenarioId": "trade.spot.limit_order",
                        "channel": "telegram",
                        "symbol": qp.get("symbol"),
                        "symbolOrder": qp.get("symbolOrder"),
                        "lastPrice": qp_prev.get("lastPrice"),
                        "limitPrice": price,
                        "transitionTrigger": "limit.quote.public_ticker",
                    },
                )
                price_dec = _positive_decimal(price)
                if price_dec is None:
                    return (
                        "限价须为有效正数，请重新输入价格。"
                        + allow_hint,
                        None,
                        False,
                    )
                if settings.trade_spot_limit_price_band_enabled:
                    last_dec = _last_price_decimal_from_ticker_preview(qp_prev)
                    if last_dec is None:
                        return (
                            "无法从行情快照读取有效最新价，暂不能校验限价偏离，请稍后重试。"
                            + allow_hint,
                            None,
                            False,
                        )
                    try:
                        band_obs = check_spot_limit_price_agent_band(
                            settings=settings,
                            limit_price=price_dec,
                            last_price=last_dec,
                        )
                    except AppError as exc:
                        d = exc.details or {}
                        await append_execution_timeline_event(
                            session,
                            execution_id=turn_eid,
                            user_id=str(anchor_id),
                            event_name="agent.execution.step",
                            step_kind="band_check",
                            outcome="failure",
                            payload={
                                "scenarioId": "trade.spot.limit_order",
                                "channel": "telegram",
                                "symbol": qp.get("symbol"),
                                "lastPrice": d.get("lastPrice"),
                                "limitPrice": d.get("limitPrice"),
                                "deviationPct": d.get("deviationPct"),
                                "appErrorCode": exc.code,
                                "transitionTrigger": "limit.price_band_rejected_pre_confirm",
                            },
                        )
                        return (
                            await format_app_error_reply_for_telegram(
                                session, settings, exc
                            )
                            + allow_hint,
                            None,
                            False,
                        )
                    await append_execution_timeline_event(
                        session,
                        execution_id=turn_eid,
                        user_id=str(anchor_id),
                        event_name="agent.execution.step",
                        step_kind="band_check",
                        outcome="success",
                        payload={
                            "scenarioId": "trade.spot.limit_order",
                            "channel": "telegram",
                            "symbol": qp.get("symbol"),
                            "lastPrice": band_obs.get("lastPrice"),
                            "limitPrice": band_obs.get("limitPrice"),
                            "deviationPct": band_obs.get("deviationPct"),
                            "maxBandPct": band_obs.get("maxBandPct"),
                            "transitionTrigger": "limit.price_band_passed_pre_confirm",
                        },
                    )
                base_a, quote_a = _spot_base_quote_assets(sym)
                qty_d = _positive_decimal(qty)
                px_d = price_dec
                notion_l = (
                    qty_d * px_d
                    if qty_d is not None and px_d is not None and quote_a
                    else None
                )
                block_msg, rule_preamble = await _eval_confirmation_rules_for_type_a(
                    session,
                    scenario_id="trade.spot.limit_order",
                    nominal_usdt=notion_l,
                    turn_eid=turn_eid,
                    anchor_id=anchor_id,
                )
                if block_msg:
                    return block_msg + allow_hint, None, False
                await append_trading_write_prompt_snapshot_if_missing(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    scenario_id="trade.spot.limit_order",
                )
                mark_type_a_pending(tg_sid)
                token = await create_spot_limit_pending(
                    session,
                    telegram_user_id=anchor_id,
                    chat_id=chat_id,
                    symbol=sym,
                    side=side,
                    quantity=qty,
                    price=price,
                    time_in_force=tif,
                    execution_id=turn_eid,
                )
                await append_confirmation_required(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    scenario_id="trade.spot.limit_order",
                    channel="telegram",
                    extra={
                        "symbol": sym,
                        "side": side,
                        "quantityRequested": qty,
                        "limitPrice": price,
                        "timeInForce": tif,
                    },
                )
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="confirm_prompt",
                    outcome="success",
                    payload={
                        "scenarioId": "trade.spot.limit_order",
                        "channel": "telegram",
                        "confirmKind": "type_a_inline",
                        "symbol": sym,
                        "side": side,
                        "quantityRequested": qty,
                        "limitPrice": price,
                        "timeInForce": tif,
                        "transitionTrigger": "limit.confirm.type_a_offered",
                    },
                )
                preamble = await _try_telegram_trade_type_a_llm_preamble(
                    session=session,
                    settings=settings,
                    enabled=narrate_effective["spotLimitConfirm"],
                    scenario_id="trade.spot.limit_order",
                    user_text=user_text,
                    turn_eid=turn_eid,
                    chat_id=chat_id,
                    anchor_id=anchor_id,
                    effective_locale=ir.effective_locale,
                    slots_dict=slots_dict,
                    quote_preview=qp_prev,
                    event_name="llm.trade.spot.limit_order",
                )
                body = rule_preamble + (preamble or "")
                body += (
                    _format_limit_type_a_confirmation(
                        slots_dict,
                        base_asset=base_a,
                        quote_asset=quote_a,
                        notional_quote=notion_l,
                    )
                    + "\n\n"
                )
                body += "（15 分钟内有效；重复发起会以最新一次为准。）"
                markup = {
                    "inline_keyboard": [
                        [
                            {"text": "确认下单", "callback_data": f"{CB_LIMIT_CONFIRM}{token}"},
                            {"text": "取消", "callback_data": f"{CB_LIMIT_CANCEL}{token}"},
                        ],
                    ],
                }
                return body + allow_hint, markup, True

            if rid == "trade.spot.amend_limit_order":
                oid = (slots_dict.get("orderId") or "").strip()
                new_price = (slots_dict.get("price") or "").strip()
                new_qty = (slots_dict.get("quantity") or "").strip()
                if not sym or not oid:
                    return (
                        (
                            _format_plan_clarify(plan)
                            if plan.clarify
                            else "改单参数不完整，请补充交易对与订单号。"
                        )
                        + allow_hint,
                        None,
                        False,
                    )
                if not new_price and not new_qty:
                    return (
                        "改单须至少提供新限价或新数量之一。"
                        + allow_hint,
                        None,
                        False,
                    )
                try:
                    oo = await spot_open_orders_for_bound_user(
                        session=session,
                        settings=settings,
                        user_id=str(anchor_id),
                        symbol=sym,
                        limit=100,
                    )
                except AppError as exc:
                    return (
                        (await format_app_error_reply_for_telegram(session, settings, exc))
                        + allow_hint
                    ), None, False
                orders = oo.get("orders") if isinstance(oo.get("orders"), list) else []
                prior_row: dict[str, Any] | None = None
                for row in orders:
                    if not isinstance(row, dict):
                        continue
                    row_oid = row.get("orderIdString") or row.get("orderId")
                    if row_oid is not None and str(row_oid).strip() == oid:
                        prior_row = row
                        break
                if prior_row is None:
                    return (
                        f"未找到订单号 `{oid}` 的在途委托，请核对交易对后重试。"
                        + allow_hint,
                        None,
                        False,
                    )
                side_amend = str(prior_row.get("side") or "").strip().upper()
                if side_amend not in ("BUY", "SELL"):
                    return (
                        "无法在途委托中读取买卖方向，请查单后重试。"
                        + allow_hint,
                        None,
                        False,
                    )
                prior_price = str(prior_row.get("price") or "").strip()
                prior_qty = str(
                    prior_row.get("origQty") or prior_row.get("executedQty") or ""
                ).strip()
                price_out = new_price or prior_price
                qty_out = new_qty or prior_qty
                tif = (
                    (slots_dict.get("timeInForce") or prior_row.get("timeInForce") or "GTC")
                    .strip()
                    .upper()
                    or "GTC"
                )
                if not price_out or not qty_out:
                    return (
                        "无法确定新限价或新数量，请显式提供。"
                        + allow_hint,
                        None,
                        False,
                    )
                if prior_price == price_out and prior_qty == qty_out:
                    return (
                        "新参数与原委托相同，无需改单。"
                        + allow_hint,
                        None,
                        False,
                    )
                price_dec = _positive_decimal(price_out)
                if price_dec is None:
                    return (
                        "新限价须为有效正数，请重新输入。"
                        + allow_hint,
                        None,
                        False,
                    )
                if settings.trade_spot_limit_price_band_enabled:
                    try:
                        qp = await spot_quote_for_bound_user(
                            session=session,
                            settings=settings,
                            user_id=str(anchor_id),
                            symbol=sym,
                        )
                    except AppError as exc:
                        return (
                            (await format_app_error_reply_for_telegram(session, settings, exc))
                            + allow_hint
                        ), None, False
                    qp_prev = (
                        qp.get("quotePreview")
                        if isinstance(qp.get("quotePreview"), dict)
                        else {}
                    )
                    last_dec = _last_price_decimal_from_ticker_preview(qp_prev)
                    if last_dec is None:
                        return (
                            "无法从行情快照读取有效最新价，暂不能校验限价偏离，请稍后重试。"
                            + allow_hint,
                            None,
                            False,
                        )
                    try:
                        check_spot_limit_price_agent_band(
                            settings=settings,
                            limit_price=price_dec,
                            last_price=last_dec,
                        )
                    except AppError as exc:
                        await append_execution_timeline_event(
                            session,
                            execution_id=turn_eid,
                            user_id=str(anchor_id),
                            event_name="agent.execution.step",
                            step_kind="band_check",
                            outcome="fail",
                            payload={
                                "scenarioId": "trade.spot.amend_limit_order",
                                "channel": "telegram",
                                "symbol": sym,
                                "limitPrice": price_out,
                                "appErrorCode": exc.code,
                                "transitionTrigger": "amend.price_band_rejected_pre_confirm",
                            },
                        )
                        return (
                            (await format_app_error_reply_for_telegram(session, settings, exc))
                            + allow_hint
                        ), None, False
                await append_trading_write_prompt_snapshot_if_missing(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    scenario_id="trade.spot.amend_limit_order",
                )
                mark_type_a_pending(tg_sid)
                token = await create_spot_amend_pending(
                    session,
                    telegram_user_id=anchor_id,
                    chat_id=chat_id,
                    symbol=sym,
                    order_id=oid,
                    side=side_amend,
                    prior_price=prior_price,
                    prior_quantity=prior_qty,
                    price=price_out,
                    quantity=qty_out,
                    time_in_force=tif,
                    execution_id=turn_eid,
                )
                await append_confirmation_required(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    scenario_id="trade.spot.amend_limit_order",
                    channel="telegram",
                    extra={
                        "symbol": sym,
                        "orderId": oid,
                        "limitPrice": price_out,
                        "quantityRequested": qty_out,
                    },
                )
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="confirm_prompt",
                    outcome="success",
                    payload={
                        "scenarioId": "trade.spot.amend_limit_order",
                        "channel": "telegram",
                        "confirmKind": "type_a_inline",
                        "symbol": sym,
                        "orderId": oid,
                        "priorPrice": prior_price,
                        "priorQuantity": prior_qty,
                        "limitPrice": price_out,
                        "quantityRequested": qty_out,
                        "transitionTrigger": "amend.confirm.type_a_offered",
                    },
                )
                body = _format_spot_amend_type_a_confirmation(
                    symbol=sym,
                    side=side_amend,
                    order_id=oid,
                    prior_price=prior_price,
                    prior_quantity=prior_qty,
                    new_price=price_out,
                    new_quantity=qty_out,
                    time_in_force=tif,
                )
                body += "\n\n（15 分钟内有效；重复发起会以最新一次为准。）"
                markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "确认修改",
                                "callback_data": f"{CB_AMEND_CONFIRM}{token}",
                            },
                            {"text": "取消", "callback_data": f"{CB_AMEND_CANCEL}{token}"},
                        ],
                    ],
                }
                return body + allow_hint, markup, True

            if rid == "margin.cross.limit_order":
                price = (slots_dict.get("price") or "").strip()
                if not sym or side not in ("BUY", "SELL") or not qty or not price:
                    return (
                        (
                            _format_plan_clarify(plan)
                            if plan.clarify
                            else (
                                "全仓杠杆限价单参数不完整，请补充交易对、方向、数量与限价。"
                            )
                        )
                        + allow_hint,
                        None,
                        False,
                    )
                try:
                    qp = await spot_quote_for_bound_user(
                        session=session,
                        settings=settings,
                        user_id=str(anchor_id),
                        symbol=sym,
                    )
                except AppError as exc:
                    return (
                        (await format_app_error_reply_for_telegram(session, settings, exc))
                        + allow_hint
                    ), None, False
                qp_prev = qp.get("quotePreview") if isinstance(qp.get("quotePreview"), dict) else {}
                price_dec = _positive_decimal(price)
                if price_dec is None:
                    return (
                        "限价须为有效正数，请重新输入价格。" + allow_hint,
                        None,
                        False,
                    )
                base_a, quote_a = _spot_base_quote_assets(sym)
                qty_d = _positive_decimal(qty)
                notion_l = (
                    qty_d * price_dec
                    if qty_d is not None and price_dec is not None and quote_a
                    else None
                )
                block_msg, rule_preamble = await _eval_confirmation_rules_for_type_a(
                    session,
                    scenario_id="margin.cross.limit_order",
                    nominal_usdt=notion_l,
                    turn_eid=turn_eid,
                    anchor_id=anchor_id,
                )
                if block_msg:
                    return block_msg + allow_hint, None, False
                token = await create_margin_limit_pending_phase1(
                    session,
                    telegram_user_id=anchor_id,
                    chat_id=chat_id,
                    symbol=sym,
                    side=side,
                    quantity=qty,
                    price=price,
                    execution_id=turn_eid,
                )
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="confirm_prompt",
                    outcome="success",
                    payload={
                        "scenarioId": "margin.cross.limit_order",
                        "channel": "telegram",
                        "confirmKind": "type_a_dual_inline",
                        "confirmPhase": 1,
                        "symbol": sym,
                        "side": side,
                        "quantityRequested": qty,
                        "limitPrice": price,
                        "transitionTrigger": "margin.limit.confirm.phase1_offered",
                    },
                )
                body = rule_preamble
                body += _format_margin_phase1_confirmation(
                    slots_dict,
                    order_type="LIMIT",
                    base_asset=base_a,
                    quote_asset=quote_a,
                    notional_quote=notion_l,
                )
                body += "\n\n（15 分钟内有效；重复发起会以最新一次为准。）"
                markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "进入二次确认",
                                "callback_data": f"{CB_MARGIN_LIMIT_P1_CONFIRM}{token}",
                            },
                            {
                                "text": "取消",
                                "callback_data": f"{CB_MARGIN_LIMIT_P1_CANCEL}{token}",
                            },
                        ],
                    ],
                }
                return body + allow_hint, markup, True

            if rid == "margin.cross.market_order":
                if not sym or side not in ("BUY", "SELL") or not qty:
                    return (
                        (
                            _format_plan_clarify(plan)
                            if plan.clarify
                            else "全仓杠杆市价单参数不完整，请补充交易对、方向与数量。"
                        )
                        + allow_hint,
                        None,
                        False,
                    )
                try:
                    qp = await spot_quote_for_bound_user(
                        session=session,
                        settings=settings,
                        user_id=str(anchor_id),
                        symbol=sym,
                    )
                except AppError as exc:
                    return (
                        (await format_app_error_reply_for_telegram(session, settings, exc))
                        + allow_hint
                    ), None, False
                qp_prev = qp.get("quotePreview") if isinstance(qp.get("quotePreview"), dict) else {}
                base_a, quote_a = _spot_base_quote_assets(sym)
                last_px = _last_price_decimal_from_ticker_preview(qp_prev)
                qty_d = _positive_decimal(qty)
                notion_f = (
                    qty_d * last_px
                    if qty_d is not None and last_px is not None and quote_a
                    else None
                )
                block_msg, rule_preamble = await _eval_confirmation_rules_for_type_a(
                    session,
                    scenario_id="margin.cross.market_order",
                    nominal_usdt=notion_f,
                    turn_eid=turn_eid,
                    anchor_id=anchor_id,
                )
                if block_msg:
                    return block_msg + allow_hint, None, False
                token = await create_margin_market_pending_phase1(
                    session,
                    telegram_user_id=anchor_id,
                    chat_id=chat_id,
                    symbol=sym,
                    side=side,
                    quantity=qty,
                    execution_id=turn_eid,
                )
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="confirm_prompt",
                    outcome="success",
                    payload={
                        "scenarioId": "margin.cross.market_order",
                        "channel": "telegram",
                        "confirmKind": "type_a_dual_inline",
                        "confirmPhase": 1,
                        "symbol": sym,
                        "side": side,
                        "quantityRequested": qty,
                        "transitionTrigger": "margin.market.confirm.phase1_offered",
                    },
                )
                body = rule_preamble
                body += _format_margin_phase1_confirmation(
                    slots_dict,
                    order_type="MARKET",
                    base_asset=base_a,
                    quote_asset=quote_a,
                    notional_quote=notion_f,
                )
                body += "\n\n（15 分钟内有效；重复发起会以最新一次为准。）"
                markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "进入二次确认",
                                "callback_data": f"{CB_MARGIN_MARKET_P1_CONFIRM}{token}",
                            },
                            {
                                "text": "取消",
                                "callback_data": f"{CB_MARGIN_MARKET_P1_CANCEL}{token}",
                            },
                        ],
                    ],
                }
                return body + allow_hint, markup, True

            if rid == "trade.futures.limit_order":
                price = (slots_dict.get("price") or "").strip()
                open_close = (slots_dict.get("openClose") or "").strip().upper() or None
                if not sym or side not in ("BUY", "SELL") or not qty or not price:
                    return (
                        (
                            _format_plan_clarify(plan)
                            if plan.clarify
                            else (
                                "合约限价单参数不完整，请补充合约、方向（买/卖）、"
                                "数量与限价。"
                            )
                        )
                        + allow_hint,
                        None,
                        False,
                    )
                try:
                    qp = await spot_quote_for_bound_user(
                        session=session,
                        settings=settings,
                        user_id=str(anchor_id),
                        symbol=sym,
                    )
                except AppError as exc:
                    return (
                        (await format_app_error_reply_for_telegram(session, settings, exc))
                        + allow_hint
                    ), None, False
                qp_prev = qp.get("quotePreview") if isinstance(qp.get("quotePreview"), dict) else {}
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="quote",
                    outcome="success",
                    payload={
                        "scenarioId": "trade.futures.limit_order",
                        "channel": "telegram",
                        "symbol": qp.get("symbol"),
                        "symbolOrder": qp.get("symbolOrder"),
                        "lastPrice": qp_prev.get("lastPrice"),
                        "limitPrice": price,
                        "transitionTrigger": "futures.limit.quote.public_ticker",
                    },
                )
                price_dec = _positive_decimal(price)
                if price_dec is None:
                    return (
                        "限价须为有效正数，请重新输入价格。"
                        + allow_hint,
                        None,
                        False,
                    )
                base_a, quote_a = _spot_base_quote_assets(sym)
                qty_d = _positive_decimal(qty)
                notion_l = (
                    qty_d * price_dec
                    if qty_d is not None and price_dec is not None and quote_a
                    else None
                )
                block_msg, rule_preamble = await _eval_confirmation_rules_for_type_a(
                    session,
                    scenario_id="trade.futures.limit_order",
                    nominal_usdt=notion_l,
                    turn_eid=turn_eid,
                    anchor_id=anchor_id,
                )
                if block_msg:
                    return block_msg + allow_hint, None, False
                token = await create_futures_limit_pending(
                    session,
                    telegram_user_id=anchor_id,
                    chat_id=chat_id,
                    symbol=sym,
                    side=side,
                    quantity=qty,
                    price=price,
                    open_close=open_close,
                    execution_id=turn_eid,
                )
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="confirm_prompt",
                    outcome="success",
                    payload={
                        "scenarioId": "trade.futures.limit_order",
                        "channel": "telegram",
                        "confirmKind": "type_a_inline",
                        "symbol": sym,
                        "side": side,
                        "quantityRequested": qty,
                        "limitPrice": price,
                        "openClose": open_close,
                        "transitionTrigger": "futures.limit.confirm.type_a_offered",
                    },
                )
                preamble = await _try_telegram_trade_type_a_llm_preamble(
                    session=session,
                    settings=settings,
                    enabled=narrate_effective["futuresLimitConfirm"],
                    scenario_id="trade.futures.limit_order",
                    user_text=user_text,
                    turn_eid=turn_eid,
                    chat_id=chat_id,
                    anchor_id=anchor_id,
                    effective_locale=ir.effective_locale,
                    slots_dict=slots_dict,
                    quote_preview=qp_prev,
                    event_name="llm.trade.futures.limit_order",
                )
                body = rule_preamble + (preamble or "")
                body += (
                    _format_futures_limit_type_a_confirmation(
                        slots_dict,
                        base_asset=base_a,
                        quote_asset=quote_a,
                        notional_quote=notion_l,
                    )
                    + "\n\n"
                )
                body += "（15 分钟内有效；重复发起会以最新一次为准。）"
                markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "确认下单",
                                "callback_data": f"{CB_FUTURES_LIMIT_CONFIRM}{token}",
                            },
                            {
                                "text": "取消",
                                "callback_data": f"{CB_FUTURES_LIMIT_CANCEL}{token}",
                            },
                        ],
                    ],
                }
                return body + allow_hint, markup, True

            if rid == "trade.futures.market_order":
                open_close = (slots_dict.get("openClose") or "").strip().upper() or None
                if not sym or side not in ("BUY", "SELL") or not qty:
                    return (
                        (
                            _format_plan_clarify(plan)
                            if plan.clarify
                            else "合约市价单参数不完整，请补充合约、方向（买/卖）与数量。"
                        )
                        + allow_hint,
                        None,
                        False,
                    )
                try:
                    qp = await spot_quote_for_bound_user(
                        session=session,
                        settings=settings,
                        user_id=str(anchor_id),
                        symbol=sym,
                    )
                except AppError as exc:
                    return (
                        (await format_app_error_reply_for_telegram(session, settings, exc))
                        + allow_hint
                    ), None, False
                qp_prev = qp.get("quotePreview") if isinstance(qp.get("quotePreview"), dict) else {}
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="quote",
                    outcome="success",
                    payload={
                        "scenarioId": "trade.futures.market_order",
                        "channel": "telegram",
                        "symbol": qp.get("symbol"),
                        "symbolOrder": qp.get("symbolOrder"),
                        "lastPrice": qp_prev.get("lastPrice"),
                        "transitionTrigger": "futures.market.quote.public_ticker",
                    },
                )
                base_a, quote_a = _spot_base_quote_assets(sym)
                last_px = _last_price_decimal_from_ticker_preview(qp_prev)
                qty_d = _positive_decimal(qty)
                notion_f = (
                    qty_d * last_px
                    if qty_d is not None and last_px is not None and quote_a
                    else None
                )
                block_msg, rule_preamble = await _eval_confirmation_rules_for_type_a(
                    session,
                    scenario_id="trade.futures.market_order",
                    nominal_usdt=notion_f,
                    turn_eid=turn_eid,
                    anchor_id=anchor_id,
                )
                if block_msg:
                    return block_msg + allow_hint, None, False
                token = await create_futures_market_pending(
                    session,
                    telegram_user_id=anchor_id,
                    chat_id=chat_id,
                    symbol=sym,
                    side=side,
                    quantity=qty,
                    open_close=open_close,
                    execution_id=turn_eid,
                )
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="confirm_prompt",
                    outcome="success",
                    payload={
                        "scenarioId": "trade.futures.market_order",
                        "channel": "telegram",
                        "confirmKind": "type_a_inline",
                        "symbol": sym,
                        "side": side,
                        "quantityRequested": qty,
                        "openClose": open_close,
                        "transitionTrigger": "futures.market.confirm.type_a_offered",
                    },
                )
                preamble = await _try_telegram_trade_type_a_llm_preamble(
                    session=session,
                    settings=settings,
                    enabled=narrate_effective["futuresMarketConfirm"],
                    scenario_id="trade.futures.market_order",
                    user_text=user_text,
                    turn_eid=turn_eid,
                    chat_id=chat_id,
                    anchor_id=anchor_id,
                    effective_locale=ir.effective_locale,
                    slots_dict=slots_dict,
                    quote_preview=qp_prev,
                    event_name="llm.trade.futures.market_order",
                )
                body = rule_preamble + (preamble or "")
                body += (
                    _format_futures_market_type_a_confirmation(
                        slots_dict,
                        base_asset=base_a,
                        quote_asset=quote_a,
                        notional_quote=notion_f,
                    )
                    + "\n\n"
                )
                body += "（15 分钟内有效；重复发起会以最新一次为准。）"
                markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "确认下单",
                                "callback_data": f"{CB_FUTURES_MARKET_CONFIRM}{token}",
                            },
                            {
                                "text": "取消",
                                "callback_data": f"{CB_FUTURES_MARKET_CANCEL}{token}",
                            },
                        ],
                    ],
                }
                return body + allow_hint, markup, True

            if rid == "automation.condition_order_cancel":
                sym_c = (slots_dict.get("symbol") or "").strip()
                oid_c = (slots_dict.get("orderId") or "").strip()
                if not sym_c or not oid_c:
                    return (
                        (
                            _format_plan_clarify(plan)
                            if plan.clarify
                            else "条件单撤销须提供合约标的与订单号。"
                        )
                        + allow_hint,
                        None,
                        False,
                    )
                block_msg, rule_preamble = await _eval_confirmation_rules_for_type_a(
                    session,
                    scenario_id="automation.condition_order_cancel",
                    nominal_usdt=None,
                    turn_eid=turn_eid,
                    anchor_id=anchor_id,
                )
                if block_msg:
                    return block_msg + allow_hint, None, False
                token = await create_condition_cancel_pending(
                    session,
                    telegram_user_id=anchor_id,
                    chat_id=chat_id,
                    symbol=sym_c,
                    order_id=oid_c,
                    execution_id=turn_eid,
                )
                body = rule_preamble + (
                    "【触发条件 · 撤销确认】\n"
                    f"合约：`{sym_c}`\n"
                    f"订单号：`{oid_c}`\n"
                    "确认后将调用交易所 `POST /fapi/v1/cancel` 撤销该条件/计划委托。\n\n"
                    "（15 分钟内有效。）"
                )
                markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "确认撤销",
                                "callback_data": f"{CB_CONDITION_CANCEL_CONFIRM}{token}",
                            },
                            {
                                "text": "取消",
                                "callback_data": f"{CB_CONDITION_CANCEL_DISMISS}{token}",
                            },
                        ],
                    ],
                }
                return body + allow_hint, markup, True

            if rid == "automation.condition_order":
                tp = (slots_dict.get("triggerPrice") or "").strip()
                tt = (slots_dict.get("triggerType") or "").strip().upper()
                oc = (slots_dict.get("openClose") or "").strip().upper() or None
                triggered_ot = "LIMIT" if (nlu and nlu.order_type_hint == "limit") else "MARKET"
                exec_price = (slots_dict.get("price") or "").strip() or None
                if (
                    not sym
                    or side not in ("BUY", "SELL")
                    or not qty
                    or not tp
                    or tt not in ("3UP", "4DOWN")
                ):
                    return (
                        (
                            _format_plan_clarify(plan)
                            if plan.clarify
                            else (
                                "条件单参数不完整，请补充合约、方向、数量、"
                                "触发价与触发方向（上涨 3UP / 下跌 4DOWN）。"
                            )
                        )
                        + allow_hint,
                        None,
                        False,
                    )
                if triggered_ot == "LIMIT" and not exec_price:
                    return (
                        "触发后限价单须提供委托价（price）。"
                        + allow_hint,
                        None,
                        False,
                    )
                block_msg, rule_preamble = await _eval_confirmation_rules_for_type_a(
                    session,
                    scenario_id="automation.condition_order",
                    nominal_usdt=None,
                    turn_eid=turn_eid,
                    anchor_id=anchor_id,
                )
                if block_msg:
                    return block_msg + allow_hint, None, False
                token = await create_condition_pending(
                    session,
                    telegram_user_id=anchor_id,
                    chat_id=chat_id,
                    symbol=sym,
                    side=side,
                    quantity=qty,
                    trigger_price=tp,
                    trigger_type=tt,
                    order_type=triggered_ot,
                    price=exec_price,
                    open_close=oc,
                    execution_id=turn_eid,
                )
                await append_execution_timeline_event(
                    session,
                    execution_id=turn_eid,
                    user_id=str(anchor_id),
                    event_name="agent.execution.step",
                    step_kind="confirm_gate",
                    outcome="success",
                    payload={
                        "scenarioId": "automation.condition_order",
                        "channel": "telegram",
                        "symbol": sym,
                        "triggerPrice": tp,
                        "triggerType": tt,
                        "orderType": triggered_ot,
                        "transitionTrigger": "condition.confirm.type_a_offered",
                    },
                )
                base_a, _quote_a = _spot_base_quote_assets(sym)
                body = rule_preamble
                body += _format_condition_type_a_confirmation(
                    slots_dict,
                    base_asset=base_a,
                    order_type=triggered_ot,
                )
                body += "\n\n（15 分钟内有效；重复发起会以最新一次为准。）"
                markup = {
                    "inline_keyboard": [
                        [
                            {
                                "text": "确认创建",
                                "callback_data": f"{CB_CONDITION_CONFIRM}{token}",
                            },
                            {
                                "text": "取消",
                                "callback_data": f"{CB_CONDITION_CANCEL}{token}",
                            },
                        ],
                    ],
                }
                return body + allow_hint, markup, True

            quote_qty_s = (slots_dict.get("quoteQty") or "").strip()
            if not qty and quote_qty_s and side == "BUY":
                try:
                    qp_pre = await spot_quote_for_bound_user(
                        session=session,
                        settings=settings,
                        user_id=str(anchor_id),
                        symbol=sym,
                    )
                except AppError as exc:
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc)
                    ) + allow_hint, None, False
                qp_prev_pre = (
                    qp_pre.get("quotePreview")
                    if isinstance(qp_pre.get("quotePreview"), dict)
                    else {}
                )
                lp_pre = _last_price_decimal_from_ticker_preview(qp_prev_pre)
                if lp_pre is None:
                    return (
                        "无法读取有效最新价，暂不能按 USDT 金额换算买入数量，请稍后重试。"
                        + allow_hint,
                        None,
                        False,
                    )
                try:
                    qty = quote_qty_to_base_quantity(
                        quote_qty=quote_qty_s,
                        last_price=lp_pre,
                    )
                    slots_dict = {**slots_dict, "quantity": qty}
                except AppError as exc:
                    return (
                        await format_app_error_reply_for_telegram(session, settings, exc)
                    ) + allow_hint, None, False

            if not sym or side not in ("BUY", "SELL") or not qty:
                return (
                    (
                        _format_plan_clarify(plan)
                        if plan.clarify
                        else "闪兑参数不完整，请补充交易对、方向（买/卖）与数量或 USDT 花费。"
                    )
                    + allow_hint,
                    None,
                    False,
                )
            try:
                qp = await spot_quote_for_bound_user(
                    session=session,
                    settings=settings,
                    user_id=str(anchor_id),
                    symbol=sym,
                )
            except AppError as exc:
                return (
                    (await format_app_error_reply_for_telegram(session, settings, exc))
                    + allow_hint
                ), None, False
            qp_prev = qp.get("quotePreview") if isinstance(qp.get("quotePreview"), dict) else {}
            await append_execution_timeline_event(
                session,
                execution_id=turn_eid,
                user_id=str(anchor_id),
                event_name="agent.execution.step",
                step_kind="quote",
                outcome="success",
                payload={
                    "scenarioId": "trade.spot.flash_convert",
                    "channel": "telegram",
                    "symbol": qp.get("symbol"),
                    "symbolOrder": qp.get("symbolOrder"),
                    "lastPrice": qp_prev.get("lastPrice"),
                    "transitionTrigger": "flash.quote.public_ticker",
                },
            )
            base_a, quote_a = _spot_base_quote_assets(sym)
            last_px = _last_price_decimal_from_ticker_preview(qp_prev)
            qty_d = _positive_decimal(qty)
            notion_f = (
                qty_d * last_px
                if qty_d is not None and last_px is not None and quote_a
                else None
            )
            block_msg, rule_preamble = await _eval_confirmation_rules_for_type_a(
                session,
                scenario_id="trade.spot.flash_convert",
                nominal_usdt=notion_f,
                turn_eid=turn_eid,
                anchor_id=anchor_id,
            )
            if block_msg:
                return block_msg + allow_hint, None, False
            await append_trading_write_prompt_snapshot_if_missing(
                session,
                execution_id=turn_eid,
                user_id=str(anchor_id),
                scenario_id="trade.spot.flash_convert",
            )
            await append_confirmation_required(
                session,
                execution_id=turn_eid,
                user_id=str(anchor_id),
                scenario_id="trade.spot.flash_convert",
                channel="telegram",
                extra={
                    "symbol": sym,
                    "side": side,
                    "quantityRequested": qty,
                },
            )
            mark_type_a_pending(tg_sid)
            token = await create_flash_convert_pending(
                session,
                telegram_user_id=anchor_id,
                chat_id=chat_id,
                symbol=sym,
                side=side,
                quantity=qty,
                execution_id=turn_eid,
            )
            await append_execution_timeline_event(
                session,
                execution_id=turn_eid,
                user_id=str(anchor_id),
                event_name="agent.execution.step",
                step_kind="confirm_prompt",
                outcome="success",
                payload={
                    "scenarioId": "trade.spot.flash_convert",
                    "channel": "telegram",
                    "confirmKind": "type_a_inline",
                    "symbol": sym,
                    "side": side,
                    "quantityRequested": qty,
                    "transitionTrigger": "flash.confirm.type_a_offered",
                },
            )
            preamble = await _try_telegram_trade_type_a_llm_preamble(
                session=session,
                settings=settings,
                enabled=narrate_effective["spotFlashConfirm"],
                scenario_id="trade.spot.flash_convert",
                user_text=user_text,
                turn_eid=turn_eid,
                chat_id=chat_id,
                anchor_id=anchor_id,
                effective_locale=ir.effective_locale,
                slots_dict=slots_dict,
                quote_preview=qp_prev,
                event_name="llm.trade.spot.flash_convert",
            )
            body = rule_preamble + (preamble or "")
            body += (
                _format_flash_type_a_confirmation(
                    slots_dict,
                    base_asset=base_a,
                    quote_asset=quote_a,
                    notional_quote=notion_f,
                )
                + "\n\n"
            )
            body += "（15 分钟内有效；重复发起会以最新一次为准。）"
            markup = {
                "inline_keyboard": [
                    [
                        {"text": "确认下单", "callback_data": f"{CB_FLASH_CONFIRM}{token}"},
                        {"text": "取消", "callback_data": f"{CB_FLASH_CANCEL}{token}"},
                    ],
                ],
            }
            return body + allow_hint, markup, True

        return (
            _format_faq_hint(settings, plan.resolved_scenario_id, ir.confidence, []) + allow_hint,
            None,
            False,
        )

    raw, markup = await run_telegram_turn_execution(
        session,
        user_id=str(anchor_id),
        scenario_id=exec_sid,
        compute=_compose_allowed_reply,
    )
    if _markup_is_type_a_confirm(markup):
        register_pending_type_a(tg_sid, waiting=True)
    record_telegram_stm_turn(
        session_id=tg_sid,
        user_id=str(anchor_id),
        user_text=user_text,
        assistant_text=raw,
    )
    return _lead(raw), markup
