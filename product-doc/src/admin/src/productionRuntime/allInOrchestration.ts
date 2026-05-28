/**
 * INV-010 · 语义满仓/买满/清仓 — 编排下一步（只读补槽）
 *
 * 规格：specs/requirements/flows/trade-via-agent.md · 专节 INV-010
 *       specs/requirements/Runtime/runtime-invariants.md · INV-010
 */

import type { InternalTradeResolverMode } from "./internalTradeResolverAdapter";

export const ALL_IN_SEMANTIC_INTENTS = new Set([
  "ALL_IN",
  "FULL_BOOK",
  "BUY_ALL",
  "SELL_ALL",
]);

/** 用户话束启发式（Parser 未打 semanticIntent 时的兜底）。 */
const ALL_IN_UTTERANCE =
  /全部(?:买入|买|卖出|卖|卖光|卖完|清仓|取出)?|买满|用全部|全仓卖|清仓/i;

export type OrchestrationNextStepKind =
  | "slot_fill_read_balance"
  | "slot_fill_read_position";

export type OrchestrationNextStep = {
  stepKind: OrchestrationNextStepKind;
  reason: "INV-010_ALL_IN";
  /** 只读落盘后填入的 L0 槽 */
  targetSlot: "quoteQty" | "quantity";
  /** 读侧资产提示（如 USDT / 标的 base）— 供 BFF 选 PATH */
  readAssetHint?: string;
};

export function isAllInSemanticIntent(
  semanticIntent: string | null | undefined,
): boolean {
  if (semanticIntent == null || String(semanticIntent).trim() === "") {
    return false;
  }
  return ALL_IN_SEMANTIC_INTENTS.has(String(semanticIntent).trim().toUpperCase());
}

export function utteranceSuggestsAllIn(
  userUtterance: string | null | undefined,
): boolean {
  if (userUtterance == null || String(userUtterance).trim() === "") {
    return false;
  }
  return ALL_IN_UTTERANCE.test(String(userUtterance));
}

export function resolveAllInSemantic(params: {
  semanticIntent?: string | null;
  userUtterance?: string | null;
  side?: string | null;
}): boolean {
  if (isAllInSemanticIntent(params.semanticIntent)) return true;
  if (!utteranceSuggestsAllIn(params.userUtterance)) return false;
  const s = String(params.side ?? "").trim().toUpperCase();
  return s === "BUY" || s === "SELL";
}

/**
 * `missing` 含 `quantity_or_quoteQty` 且为 ALL_IN 语义时，建议编排插入只读步（非用户可见 routingHints）。
 */
export function buildAllInOrchestrationNextSteps(params: {
  mode: InternalTradeResolverMode;
  missing: readonly string[];
  semanticIntent?: string | null;
  userUtterance?: string | null;
  side?: string | null;
  symbol?: string | null;
}): OrchestrationNextStep[] {
  const { mode, missing } = params;
  if (mode !== "flash_convert") return [];
  if (!missing.includes("quantity_or_quoteQty")) return [];
  if (!resolveAllInSemantic(params)) return [];

  const side = String(params.side ?? "").trim().toUpperCase();
  if (side === "BUY") {
    return [
      {
        stepKind: "slot_fill_read_balance",
        reason: "INV-010_ALL_IN",
        targetSlot: "quoteQty",
        readAssetHint: "USDT",
      },
    ];
  }
  if (side === "SELL") {
    return [
      {
        stepKind: "slot_fill_read_position",
        reason: "INV-010_ALL_IN",
        targetSlot: "quantity",
        readAssetHint: params.symbol ?? undefined,
      },
    ];
  }
  return [];
}
