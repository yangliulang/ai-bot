import { describe, expect, it } from "vitest";
import {
  assertNoExecutableWriteTypeAWhenMissing,
  buildFlashConvertResolverOutput,
  buildSpotLimitOrderResolverOutput,
  resolveFlashConvertMissingSlots,
  resolveSpotLimitOrderMissingSlots,
} from "./tradeWriteResolverGate";

describe("resolveFlashConvertMissingSlots（闪兑 L0）", () => {
  it("全缺 → symbol side type + quantity_or_quoteQty", () => {
    expect(resolveFlashConvertMissingSlots({})).toEqual([
      "symbol",
      "side",
      "type",
      "quantity_or_quoteQty",
    ]);
  });

  it("仅有 symbol → 仍缺 side type qty", () => {
    expect(resolveFlashConvertMissingSlots({ symbol: "BTCUSDT" })).toEqual([
      "side",
      "type",
      "quantity_or_quoteQty",
    ]);
  });

  it("quantity 满足互斥之一 → 不再缺 quantity_or_quoteQty", () => {
    const m = resolveFlashConvertMissingSlots({
      symbol: "BTCUSDT",
      side: "BUY",
      type: "MARKET",
      quantity: "0.1",
    });
    expect(m).toEqual([]);
  });

  it("quoteQty 满足互斥之一", () => {
    const m = resolveFlashConvertMissingSlots({
      symbol: "ETHUSDT",
      side: "BUY",
      type: "MARKET",
      quoteQty: "100",
    });
    expect(m).toEqual([]);
  });
});

describe("resolveSpotLimitOrderMissingSlots（现货限价 L0）", () => {
  it("全缺 → symbol side type price + quantity_or_quoteQty", () => {
    expect(resolveSpotLimitOrderMissingSlots({})).toEqual([
      "symbol",
      "side",
      "type",
      "price",
      "quantity_or_quoteQty",
    ]);
  });

  it("限价齐备 → missing 空", () => {
    expect(
      resolveSpotLimitOrderMissingSlots({
        symbol: "BTCUSDT",
        side: "SELL",
        type: "LIMIT",
        price: "68000",
        quantity: "0.01",
      }),
    ).toEqual([]);
  });

  it("MARKET → type_must_be_LIMIT（供改路由 flash）", () => {
    expect(
      resolveSpotLimitOrderMissingSlots({
        symbol: "BTCUSDT",
        side: "BUY",
        type: "MARKET",
        price: "1",
        quantity: "0.01",
      }),
    ).toContain("type_must_be_LIMIT");
  });

  it("requireTimeInForce → 缺 TIF", () => {
    expect(
      resolveSpotLimitOrderMissingSlots(
        {
          symbol: "BTCUSDT",
          side: "BUY",
          type: "LIMIT",
          price: "68000",
          quantity: "0.01",
        },
        { requireTimeInForce: true },
      ),
    ).toContain("timeInForce");
  });
});

describe("build*ResolverOutput", () => {
  it("buildFlashConvertResolverOutput 槽齐带出 skillId", () => {
    const o = buildFlashConvertResolverOutput({
      input: {
        symbol: "BTCUSDT",
        side: "BUY",
        type: "MARKET",
        quoteQty: "50",
      },
    });
    expect(o.missing).toEqual([]);
    expect(o.skillId).toBe("skill.spot.flash_convert");
    expect(o.resolved).toMatchObject({ symbol: "BTCUSDT", quoteQty: "50" });
  });

  it("buildSpotLimitOrderResolverOutput 缺价格为 missing", () => {
    const o = buildSpotLimitOrderResolverOutput({
      input: {
        symbol: "BTCUSDT",
        side: "BUY",
        type: "LIMIT",
        quantity: "1",
      },
    });
    expect(o.missing).toContain("price");
    expect(o.skillId).toBeUndefined();
  });
});

describe("assertNoExecutableWriteTypeAWhenMissing（INV-008）", () => {
  it("缺参且将发载货类型 A → 抛错", () => {
    expect(() =>
      assertNoExecutableWriteTypeAWhenMissing({
        missingSlots: ["quantity_or_quoteQty"],
        willEmitTypeAWithExecutableWritePackage: true,
      }),
    ).toThrow(/INV-008/);
  });

  it("缺参但仅澄清话术（不载货）→ 不抛错", () => {
    expect(() =>
      assertNoExecutableWriteTypeAWhenMissing({
        missingSlots: ["quantity_or_quoteQty"],
        willEmitTypeAWithExecutableWritePackage: false,
      }),
    ).not.toThrow();
  });

  it("槽齐 → 载货允许", () => {
    expect(() =>
      assertNoExecutableWriteTypeAWhenMissing({
        missingSlots: [],
        willEmitTypeAWithExecutableWritePackage: true,
      }),
    ).not.toThrow();
  });
});
