/**
 * 交易写路径 · Resolver 缺参门（INV-008 / confirmation-flow §1 步骤 2）
 * `missing` 非空时不得发出「载货」类型 A、不得进入 Gateway 写扩张。
 *
 * 规格：`specs/requirements/skill-specs/spot/skill.spot.flash_convert.md`、
 * `skill.spot.limit_order.md`
 */

import type {
  AgentTradeResolverOutput,
  FlashConvertResolverInput,
  SpotLimitOrderResolverInput,
  SpotLimitOrderResolverOptions,
} from "./tradeResolverTypes";

export type {
  AgentTradeResolverOutput,
  FlashConvertResolverInput,
  SpotLimitOrderResolverInput,
  SpotLimitOrderResolverOptions,
} from "./tradeResolverTypes";

export function resolverSlotPresent(v: string | null | undefined): boolean {
  return v != null && String(v).trim() !== "";
}

/**
 * 返回仍缺的 L0 业务槽（不含 newClientOrderId 等编排生成项）。
 * `quantity_or_quoteQty` 表示互斥二选一均未提供。
 */
export function resolveFlashConvertMissingSlots(
  input: FlashConvertResolverInput,
): string[] {
  const missing: string[] = [];
  if (!resolverSlotPresent(input.symbol)) missing.push("symbol");
  if (!resolverSlotPresent(input.side)) missing.push("side");
  if (!resolverSlotPresent(input.type)) missing.push("type");
  if (!resolverSlotPresent(input.quantity) && !resolverSlotPresent(input.quoteQty)) {
    missing.push("quantity_or_quoteQty");
  }
  return missing;
}

/**
 * 现货限价 L0：`price` **与** `quantity|quoteQty` **均须**齐备；`type` 缺省视为缺 `LIMIT` 锚点（须追问）。
 * `timeInForce` 仅当 `requireTimeInForce` 为真时进入 missing。
 */
export function resolveSpotLimitOrderMissingSlots(
  input: SpotLimitOrderResolverInput,
  options?: SpotLimitOrderResolverOptions,
): string[] {
  const missing: string[] = [];
  if (!resolverSlotPresent(input.symbol)) missing.push("symbol");
  if (!resolverSlotPresent(input.side)) missing.push("side");
  if (!resolverSlotPresent(input.type)) missing.push("type");
  else if (String(input.type).trim().toUpperCase() !== "LIMIT") {
    missing.push("type_must_be_LIMIT");
  }
  if (!resolverSlotPresent(input.price)) missing.push("price");
  if (!resolverSlotPresent(input.quantity) && !resolverSlotPresent(input.quoteQty)) {
    missing.push("quantity_or_quoteQty");
  }
  if (options?.requireTimeInForce && !resolverSlotPresent(input.timeInForce)) {
    missing.push("timeInForce");
  }
  return missing;
}

function pickResolvedStringFields(
  input: Record<string, string | null | undefined>,
  keys: string[],
): Record<string, string | number | boolean | null> {
  const out: Record<string, string | number | boolean | null> = {};
  for (const k of keys) {
    const v = input[k];
    if (resolverSlotPresent(v)) out[k] = String(v).trim();
  }
  return out;
}

/** 拼装 `AgentTradeResolverOutput`，便于编排落 JSON / SSE。 */
export function buildFlashConvertResolverOutput(params: {
  input: FlashConvertResolverInput;
  intent?: string;
  semanticIntent?: string;
  /** 已由路由定下时使用；未定可省略 */
  routedSkillId?: string;
}): AgentTradeResolverOutput {
  const { input, intent = "trade", semanticIntent, routedSkillId } = params;
  const missing = resolveFlashConvertMissingSlots(input);
  const resolved = pickResolvedStringFields(
    input as Record<string, string | null | undefined>,
    ["symbol", "side", "type", "quantity", "quoteQty"],
  );
  return {
    intent,
    semanticIntent,
    skillId:
      routedSkillId ??
      (missing.length === 0 ? "skill.spot.flash_convert" : undefined),
    resolved,
    missing,
  };
}

export function buildSpotLimitOrderResolverOutput(params: {
  input: SpotLimitOrderResolverInput;
  options?: SpotLimitOrderResolverOptions;
  intent?: string;
  semanticIntent?: string;
  routedSkillId?: string;
}): AgentTradeResolverOutput {
  const { input, options, intent = "trade", semanticIntent, routedSkillId } =
    params;
  const missing = resolveSpotLimitOrderMissingSlots(input, options);
  const resolved = pickResolvedStringFields(
    input as Record<string, string | null | undefined>,
    ["symbol", "side", "type", "price", "quantity", "quoteQty", "timeInForce"],
  );
  return {
    intent,
    semanticIntent,
    skillId:
      routedSkillId ??
      (missing.length === 0 ? "skill.spot.limit_order" : undefined),
    resolved,
    missing,
  };
}

/**
 * `willEmitTypeAWithExecutableWritePackage`：将推送的 Telegram 类型 A **携带** 拟用于 call_exchange_write 的完整参数包时为 true。
 * 缺参而仍为 true → 对应 eval.gateway.missing_qty_blocks_trade_type_a。
 */
export function assertNoExecutableWriteTypeAWhenMissing(params: {
  missingSlots: string[];
  willEmitTypeAWithExecutableWritePackage: boolean;
}): void {
  const { missingSlots, willEmitTypeAWithExecutableWritePackage } = params;
  if (
    missingSlots.length > 0 &&
    willEmitTypeAWithExecutableWritePackage
  ) {
    throw new Error(
      `INV-008：缺参 ${missingSlots.join(", ")} 时不得发出载货类型 A（须先澄清）。`,
    );
  }
}
