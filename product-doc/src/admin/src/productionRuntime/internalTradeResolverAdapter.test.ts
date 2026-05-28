import { describe, expect, it } from "vitest";
import { postInternalAgentOrchestrationTradeResolver } from "./internalTradeResolverAdapter";

describe("postInternalAgentOrchestrationTradeResolver", () => {
  it("flash_convert：槽齐可得 skillId", () => {
    const r = postInternalAgentOrchestrationTradeResolver({
      mode: "flash_convert",
      slots: {
        symbol: "BTCUSDT",
        side: "BUY",
        type: "MARKET",
        quoteQty: "10",
      },
    });
    expect(r.output.skillId).toBe("skill.spot.flash_convert");
    expect(r.output.missing).toEqual([]);
    expect(r.routingHints).toBeUndefined();
  });

  it("limit_order：缺 price → missing + 无 skillId", () => {
    const r = postInternalAgentOrchestrationTradeResolver({
      mode: "limit_order",
      slots: {
        symbol: "BTCUSDT",
        side: "BUY",
        type: "LIMIT",
        quantity: "0.01",
      },
    });
    expect(r.output.missing).toContain("price");
    expect(r.output.skillId).toBeUndefined();
  });

  it("limit + MARKET type → routingHints", () => {
    const r = postInternalAgentOrchestrationTradeResolver({
      mode: "limit_order",
      slots: {
        symbol: "BTCUSDT",
        side: "BUY",
        type: "MARKET",
        price: "1",
        quantity: "0.1",
      },
    });
    expect(r.output.missing).toContain("type_must_be_LIMIT");
    expect(r.routingHints?.length).toBeGreaterThan(0);
  });

  it("全部买入 BNB + 缺 quoteQty → orchestrationNextSteps 读余额", () => {
    const r = postInternalAgentOrchestrationTradeResolver({
      mode: "flash_convert",
      slots: {
        symbol: "BNBUSDT",
        side: "BUY",
        type: "MARKET",
      },
      userUtterance: "我想全部买入BNB",
    });
    expect(r.output.missing).toContain("quantity_or_quoteQty");
    expect(r.orchestrationNextSteps).toEqual([
      {
        stepKind: "slot_fill_read_balance",
        reason: "INV-010_ALL_IN",
        targetSlot: "quoteQty",
        readAssetHint: "USDT",
      },
    ]);
  });
});
