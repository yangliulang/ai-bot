/**
 * 同窗 `internal/agent-orchestration.yaml` · `POST .../trade-resolver`
 * 将内部请求映射为 `AgentTradeResolverOutput` + `routingHints`。
 */

import { buildAllInOrchestrationNextSteps } from "./allInOrchestration";
import type { OrchestrationNextStep } from "./allInOrchestration";
import type { AgentTradeResolverOutput } from "./tradeResolverTypes";
import {
  buildFlashConvertResolverOutput,
  buildSpotLimitOrderResolverOutput,
} from "./tradeWriteResolverGate";
import {
  buildTelegramClarifyOutboundHints,
  type RoutingClarifyKind,
} from "./telegramClarifyOutbound";
import type { EffectiveLocale } from "./clarifyKeyboard";

export type InternalTradeResolverMode = "flash_convert" | "limit_order";

export type TradeResolverSlotBag = {
  symbol?: string | null;
  side?: string | null;
  type?: string | null;
  price?: string | null;
  quantity?: string | null;
  quoteQty?: string | null;
  timeInForce?: string | null;
};

export type InternalTradeResolverRequestLike = {
  mode: InternalTradeResolverMode;
  slots: TradeResolverSlotBag;
  options?: { requireTimeInForce?: boolean };
  intent?: string;
  semanticIntent?: string | null;
  routedSkillId?: string | null;
  /** 可选原文 — 不参与缺参计算；ALL_IN 启发式见 `allInOrchestration`。 */
  userUtterance?: string | null;
  /** BFF/Parser：现货方式未定时须澄清键盘 — 见 `clarifyKeyboard` */
  routingClarify?: RoutingClarifyKind | null;
  effectiveLocale?: EffectiveLocale;
  resolvedSymbolLabel?: string | null;
};

export type InternalTradeResolverResponsePayload = {
  output: AgentTradeResolverOutput;
  routingHints?: string[];
  /** INV-010：编排须插入的只读补槽步（**非** Telegram 正文）。 */
  orchestrationNextSteps?: OrchestrationNextStep[];
  /** Telegram 澄清出站（键盘/进度/typing 期望）— BFF 消费，非 LLM JSON 直出。 */
  telegramOutbound?: ReturnType<typeof buildTelegramClarifyOutboundHints>;
};

/** 生成 `routingHints`（不向用户直连吐字；仅供 BFF/日志编排）。 */
function inferRoutingHints(missing: string[]): string[] {
  const hints: string[] = [];
  if (missing.includes("type_must_be_LIMIT")) {
    hints.push(
      "missing 含 type_must_be_LIMIT：可考虑改路由 skill.spot.flash_convert（市价/闪兑）或让用户确认限价语义。",
    );
  }
  return hints;
}

/** 对齐 OpenAPI · `operationId` postInternalAgentOrchestrationTradeResolver */
export function postInternalAgentOrchestrationTradeResolver(
  body: InternalTradeResolverRequestLike,
): InternalTradeResolverResponsePayload {
  const {
    mode,
    slots,
    options,
    intent,
    semanticIntent,
    routedSkillId,
    userUtterance,
  } = body;

  let output: AgentTradeResolverOutput;
  if (mode === "flash_convert") {
    output = buildFlashConvertResolverOutput({
      input: slots,
      intent,
      semanticIntent: semanticIntent ?? undefined,
      routedSkillId: routedSkillId ?? undefined,
    });
  } else {
    output = buildSpotLimitOrderResolverOutput({
      input: slots,
      options,
      intent,
      semanticIntent: semanticIntent ?? undefined,
      routedSkillId: routedSkillId ?? undefined,
    });
  }

  const routingHints = inferRoutingHints(output.missing);
  const orchestrationNextSteps = buildAllInOrchestrationNextSteps({
    mode,
    missing: output.missing,
    semanticIntent,
    userUtterance,
    side: slots.side,
    symbol: slots.symbol,
  });

  const payload: InternalTradeResolverResponsePayload = { output };
  if (routingHints.length > 0) payload.routingHints = routingHints;
  if (orchestrationNextSteps.length > 0) {
    payload.orchestrationNextSteps = orchestrationNextSteps;
  }
  const telegramOutbound = buildTelegramClarifyOutboundHints({
    output,
    routingClarify: body.routingClarify,
    orchestrationNextSteps,
    effectiveLocale: body.effectiveLocale,
    resolvedSymbolLabel: body.resolvedSymbolLabel,
  });
  if (telegramOutbound) payload.telegramOutbound = telegramOutbound;
  return payload;
}
