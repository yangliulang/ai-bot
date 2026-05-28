import { describe, expect, it } from "vitest";
import { buildClarifyInlineKeyboard, clarifyCallbackDataWithinLimit } from "./clarifyKeyboard";
import { runClarifyOrchestrationPipeline } from "./clarifyOrchestrationPipeline";
import { applyOrchestrationNextStepsToSlots } from "./orchestrationReadBalanceFill";
import { postInternalAgentOrchestrationTradeResolver } from "./internalTradeResolverAdapter";

describe("clarifyKeyboard", () => {
  it("spot_trade_mode · zh-Hans 闪兑/限价", () => {
    const kb = buildClarifyInlineKeyboard({
      kind: "spot_trade_mode",
      effectiveLocale: "zh-Hans",
    });
    expect(kb.rows[0]!.map((b) => b.text)).toEqual(["闪兑", "限价"]);
    for (const btn of kb.rows.flat()) {
      expect(clarifyCallbackDataWithinLimit(btn.callback_data)).toBe(true);
    }
  });
});

describe("orchestrationReadBalanceFill", () => {
  it("ALL_IN 读余额后 quoteQty 齐备", () => {
    const first = postInternalAgentOrchestrationTradeResolver({
      mode: "flash_convert",
      slots: { symbol: "BNBUSDT", side: "BUY", type: "MARKET" },
      userUtterance: "全部买入BNB",
    });
    expect(first.orchestrationNextSteps?.length).toBe(1);
    const filled = applyOrchestrationNextStepsToSlots({
      steps: first.orchestrationNextSteps!,
      slots: { symbol: "BNBUSDT", side: "BUY", type: "MARKET" },
    });
    expect(filled.quoteQty).toBe("1234.56");
    const second = postInternalAgentOrchestrationTradeResolver({
      mode: "flash_convert",
      slots: filled,
      userUtterance: "全部买入BNB",
    });
    expect(second.output.missing).not.toContain("quantity_or_quoteQty");
  });
});

describe("runClarifyOrchestrationPipeline", () => {
  it("买入 BNB · 方式未定 → inline_keyboard 闪兑/限价", () => {
    const r = runClarifyOrchestrationPipeline({
      mode: "flash_convert",
      slots: { symbol: "BNBUSDT", side: "BUY", type: "MARKET" },
      userUtterance: "我想买入BNB",
      routingClarify: "spot_trade_mode",
      resolvedSymbolLabel: "BNB",
    });
    expect(r.telegramOutbound?.clarifyInlineKeyboard?.kind).toBe("spot_trade_mode");
    expect(r.initialTyping?.sendTyping).toBe(true);
  });

  it("全部买入 BNB → 读余额后 missing 清空", () => {
    const r = runClarifyOrchestrationPipeline({
      mode: "flash_convert",
      slots: { symbol: "BNBUSDT", side: "BUY", type: "MARKET" },
      userUtterance: "全部买入BNB",
    });
    expect(r.appliedReadBalanceFill).toBe(true);
    expect(r.output.missing).toEqual([]);
    expect(r.telegramOutbound?.progressHint).toMatch(/余额/);
  });
});
