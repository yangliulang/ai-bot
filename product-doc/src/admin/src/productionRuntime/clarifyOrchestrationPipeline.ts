/**
 * 澄清编排管线 · Resolver → 只读补槽 → 再 Resolver（Demo）
 */

import { applyOrchestrationNextStepsToSlots } from "./orchestrationReadBalanceFill";
import {
  postInternalAgentOrchestrationTradeResolver,
  type InternalTradeResolverRequestLike,
  type InternalTradeResolverResponsePayload,
} from "./internalTradeResolverAdapter";
import {
  buildTelegramClarifyOutboundHints,
  type RoutingClarifyKind,
} from "./telegramClarifyOutbound";
import type { EffectiveLocale } from "./clarifyKeyboard";
import { planTelegramTypingAction } from "./telegramInboundFeedback";

export type ClarifyOrchestrationRequest = InternalTradeResolverRequestLike & {
  routingClarify?: RoutingClarifyKind | null;
  effectiveLocale?: EffectiveLocale;
  resolvedSymbolLabel?: string | null;
};

export type ClarifyOrchestrationResult = InternalTradeResolverResponsePayload & {
  telegramOutbound?: ReturnType<typeof buildTelegramClarifyOutboundHints>;
  /** Demo 观测：是否执行了只读补槽 */
  appliedReadBalanceFill?: boolean;
  /** Demo 观测：typing 调度（入站后 t=0） */
  initialTyping?: ReturnType<typeof planTelegramTypingAction>;
};

/**
 * 一步澄清编排：若 `orchestrationNextSteps` 含读余额，先填槽再 Resolver。
 */
export function runClarifyOrchestrationPipeline(
  body: ClarifyOrchestrationRequest,
): ClarifyOrchestrationResult {
  const first = postInternalAgentOrchestrationTradeResolver(body);
  let appliedReadBalanceFill = false;
  let merged = first;

  if (first.orchestrationNextSteps?.length) {
    const filledSlots = applyOrchestrationNextStepsToSlots({
      steps: first.orchestrationNextSteps,
      slots: body.slots,
    });
    appliedReadBalanceFill = filledSlots.quoteQty !== body.slots.quoteQty;
    merged = postInternalAgentOrchestrationTradeResolver({
      ...body,
      slots: filledSlots,
    });
  }

  const telegramOutbound = buildTelegramClarifyOutboundHints({
    output: merged.output,
    routingClarify: body.routingClarify,
    orchestrationNextSteps: first.orchestrationNextSteps,
    effectiveLocale: body.effectiveLocale,
    resolvedSymbolLabel: body.resolvedSymbolLabel,
  });

  const initialTyping = planTelegramTypingAction({
    updateKind: "message",
    expectsUserVisibleReply: true,
    elapsedSinceInboundMs: 0,
    lastTypingSentSinceInboundMs: null,
    firstUserVisibleReplySent: false,
  });

  const result: ClarifyOrchestrationResult = { ...merged, initialTyping };
  if (telegramOutbound) result.telegramOutbound = telegramOutbound;
  if (appliedReadBalanceFill) result.appliedReadBalanceFill = true;
  return result;
}

/** 入站话束启发式 · Demo Parser 替身 */
export function inferDemoRoutingClarifyFromUtterance(
  userUtterance: string | null | undefined,
): RoutingClarifyKind | null {
  if (userUtterance == null || !String(userUtterance).trim()) return null;
  const t = String(userUtterance);
  if (/闪兑|限价|limit|flash/i.test(t)) return null;
  if (/买入|买进|买\s*\w+|buy/i.test(t)) return "spot_trade_mode";
  return null;
}

export function inferDemoSymbolLabelFromUtterance(
  userUtterance: string | null | undefined,
): string | null {
  if (userUtterance == null) return null;
  const m = String(userUtterance).match(/\b(BNB|BTC|ETH|SOL|USDT)\b/i);
  return m ? m[1]!.toUpperCase() : null;
}
