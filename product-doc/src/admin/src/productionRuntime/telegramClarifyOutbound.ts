/**
 * Telegram 澄清出站提示（规则/BFF 结构化 · LLM 只润色正文）
 *
 * 规格：clarify-user-visible.md §0 · telegram/overview §2.3.1～§2.3.2
 */

import type { ClarifyInlineKeyboard, ClarifyKeyboardKind, EffectiveLocale } from "./clarifyKeyboard";
import { buildClarifyInlineKeyboard } from "./clarifyKeyboard";
import type { OrchestrationNextStep } from "./allInOrchestration";
import type { AgentTradeResolverOutput } from "./tradeResolverTypes";

export type RoutingClarifyKind = ClarifyKeyboardKind;

export type TelegramClarifyOutboundHints = {
  /** BFF 须 sendChatAction(typing) — 见 telegramInboundFeedback */
  expectsTypingUntilReply: boolean;
  /** 结构化键盘；BFF 贴到 sendMessage reply_markup */
  clarifyInlineKeyboard?: ClarifyInlineKeyboard;
  /** 给 LLM 的润色锚点（非最终正文） */
  userVisibleHint?: string;
  /** 只读补槽进行中提示 */
  progressHint?: string;
};

export function inferRoutingClarifyKind(params: {
  routingClarify?: RoutingClarifyKind | null;
  output: AgentTradeResolverOutput;
  orchestrationNextSteps?: readonly OrchestrationNextStep[];
}): RoutingClarifyKind | null {
  if (params.routingClarify) return params.routingClarify;
  if (params.orchestrationNextSteps?.length) return null;
  if (params.output.missing.length === 0) return null;
  return null;
}

export function buildTelegramClarifyOutboundHints(params: {
  output: AgentTradeResolverOutput;
  routingClarify?: RoutingClarifyKind | null;
  orchestrationNextSteps?: readonly OrchestrationNextStep[];
  effectiveLocale?: EffectiveLocale;
  resolvedSymbolLabel?: string | null;
}): TelegramClarifyOutboundHints | null {
  const locale = params.effectiveLocale ?? "zh-Hans";

  if (params.orchestrationNextSteps?.some((s) => s.stepKind === "slot_fill_read_balance")) {
    return {
      expectsTypingUntilReply: true,
      progressHint:
        locale === "en"
          ? "Checking your USDT available balance…"
          : "稍等，我在查你子账户的 USDT 可用余额…",
    };
  }

  const keyboardKind = inferRoutingClarifyKind({
    routingClarify: params.routingClarify,
    output: params.output,
    orchestrationNextSteps: params.orchestrationNextSteps,
  });

  if (keyboardKind) {
    const symbol = params.resolvedSymbolLabel ?? "BNB";
    const hintByKind: Record<ClarifyKeyboardKind, string> = {
      spot_trade_mode:
        locale === "en"
          ? `Buy ${symbol}. Flash convert or limit order?`
          : `买入 ${symbol}。市价闪兑还是挂限价？`,
      spot_side:
        locale === "en" ? "Buy or sell?" : "买入还是卖出？",
      confirm_symbol_default:
        locale === "en"
          ? `Continue with ${symbol}/USDT?`
          : `继续 ${symbol}/USDT，对吗？`,
    };
    return {
      expectsTypingUntilReply: true,
      clarifyInlineKeyboard: buildClarifyInlineKeyboard({
        kind: keyboardKind,
        effectiveLocale: locale,
      }),
      userVisibleHint: hintByKind[keyboardKind],
    };
  }

  if (params.output.missing.length > 0) {
    return {
      expectsTypingUntilReply: true,
      userVisibleHint:
        locale === "en"
          ? "Need a bit more info to continue."
          : "还差一项信息，我继续帮你确认。",
    };
  }

  return null;
}
