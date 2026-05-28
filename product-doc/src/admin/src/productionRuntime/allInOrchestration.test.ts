import { describe, expect, it } from "vitest";
import {
  buildAllInOrchestrationNextSteps,
  isAllInSemanticIntent,
  resolveAllInSemantic,
  utteranceSuggestsAllIn,
} from "./allInOrchestration";

describe("allInOrchestration · INV-010", () => {
  it("semanticIntent ALL_IN + 缺 quantity_or_quoteQty + BUY → read_balance → quoteQty", () => {
    const steps = buildAllInOrchestrationNextSteps({
      mode: "flash_convert",
      missing: ["quantity_or_quoteQty"],
      semanticIntent: "ALL_IN",
      side: "BUY",
      symbol: "BNBUSDT",
    });
    expect(steps).toEqual([
      {
        stepKind: "slot_fill_read_balance",
        reason: "INV-010_ALL_IN",
        targetSlot: "quoteQty",
        readAssetHint: "USDT",
      },
    ]);
  });

  it("话束「全部买入 BNB」+ BUY → read_balance", () => {
    expect(
      resolveAllInSemantic({
        userUtterance: "我想全部买入BNB",
        side: "BUY",
      }),
    ).toBe(true);
    const steps = buildAllInOrchestrationNextSteps({
      mode: "flash_convert",
      missing: ["quantity_or_quoteQty"],
      userUtterance: "全部买入BNB",
      side: "BUY",
      symbol: "BNBUSDT",
    });
    expect(steps[0]?.stepKind).toBe("slot_fill_read_balance");
  });

  it("SELL ALL_IN → read_position → quantity", () => {
    const steps = buildAllInOrchestrationNextSteps({
      mode: "flash_convert",
      missing: ["quantity_or_quoteQty"],
      semanticIntent: "SELL_ALL",
      side: "SELL",
      symbol: "BNBUSDT",
    });
    expect(steps[0]).toMatchObject({
      stepKind: "slot_fill_read_position",
      targetSlot: "quantity",
    });
  });

  it("非 ALL_IN 缺参 → 无 orchestrationNextSteps", () => {
    expect(
      buildAllInOrchestrationNextSteps({
        mode: "flash_convert",
        missing: ["quantity_or_quoteQty"],
        side: "BUY",
        userUtterance: "买 0.1 个 BNB",
      }),
    ).toEqual([]);
  });

  it("limit_order 模式 → 不产出 ALL_IN 步", () => {
    expect(
      buildAllInOrchestrationNextSteps({
        mode: "limit_order",
        missing: ["quantity_or_quoteQty"],
        semanticIntent: "ALL_IN",
        side: "BUY",
      }),
    ).toEqual([]);
  });

  it("isAllInSemanticIntent", () => {
    expect(isAllInSemanticIntent("ALL_IN")).toBe(true);
    expect(isAllInSemanticIntent("buy_all")).toBe(true);
    expect(isAllInSemanticIntent(undefined)).toBe(false);
  });

  it("utteranceSuggestsAllIn", () => {
    expect(utteranceSuggestsAllIn("卖掉全部 BNB")).toBe(true);
    expect(utteranceSuggestsAllIn("限价 95000 买")).toBe(false);
  });
});
