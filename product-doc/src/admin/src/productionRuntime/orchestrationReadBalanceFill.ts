/**
 * INV-010 · 只读补槽执行小样（Demo · 非生产交易所读）
 *
 * 规格：flows/trade-via-agent.md S11.1 · orchestrationNextSteps
 */

import type { OrchestrationNextStep } from "./allInOrchestration";
import type { TradeResolverSlotBag } from "./internalTradeResolverAdapter";

export type MockBalanceReadResult = {
  asset: string;
  available: string;
  provenance: "runtime_read_balance";
};

/** Demo：固定 USDT 可用余额；生产须 call_exchange_read。 */
export function mockReadQuoteAvailableBalance(
  readAssetHint?: string | null,
): MockBalanceReadResult {
  const asset = (readAssetHint ?? "USDT").trim() || "USDT";
  return {
    asset,
    available: "1234.56",
    provenance: "runtime_read_balance",
  };
}

/**
 * 应用 `slot_fill_read_balance` → 填 `quoteQty`（买侧 ALL_IN）。
 */
export function applySlotFillReadBalance(params: {
  step: OrchestrationNextStep;
  slots: TradeResolverSlotBag;
  balance?: MockBalanceReadResult;
}): TradeResolverSlotBag {
  if (params.step.stepKind !== "slot_fill_read_balance") {
    return { ...params.slots };
  }
  const balance =
    params.balance ??
    mockReadQuoteAvailableBalance(params.step.readAssetHint);
  return {
    ...params.slots,
    quoteQty: balance.available,
  };
}

export function applyOrchestrationNextStepsToSlots(params: {
  steps: readonly OrchestrationNextStep[];
  slots: TradeResolverSlotBag;
}): TradeResolverSlotBag {
  let slots = { ...params.slots };
  for (const step of params.steps) {
    if (step.stepKind === "slot_fill_read_balance") {
      slots = applySlotFillReadBalance({ step, slots });
    }
    // slot_fill_read_position：Demo 暂不扩面
  }
  return slots;
}
