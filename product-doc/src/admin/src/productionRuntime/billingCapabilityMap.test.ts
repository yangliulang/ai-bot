import { describe, expect, it } from "vitest";
import {
  DEMO_BILLING_CAPABILITY_MAP,
  resolveCapabilitySkuForScenario,
} from "./billingCapabilityMap";

describe("resolveCapabilitySkuForScenario", () => {
  it("写路径 scenario · 映射 cap.agent.trade", () => {
    expect(resolveCapabilitySkuForScenario("trade.spot.limit_order")).toBe(
      "cap.agent.trade",
    );
    expect(resolveCapabilitySkuForScenario("wealth.subscribe")).toBe(
      "cap.agent.trade",
    );
  });

  it("分析前缀 · cap.agent.analyze", () => {
    expect(resolveCapabilitySkuForScenario("analysis.summary")).toBe(
      "cap.agent.analyze",
    );
    expect(resolveCapabilitySkuForScenario("market.query.ticker")).toBe(
      "cap.agent.analyze",
    );
  });

  it("monitor 关键字 · cap.agent.monitoring", () => {
    expect(resolveCapabilitySkuForScenario("agent.monitor.price_alert")).toBe(
      "cap.agent.monitoring",
    );
  });

  it("未归类 · undefined", () => {
    expect(resolveCapabilitySkuForScenario("unknown.scenario")).toBeUndefined();
    expect(resolveCapabilitySkuForScenario(undefined)).toBeUndefined();
    expect(resolveCapabilitySkuForScenario("  ")).toBeUndefined();
  });

  it("自定义 map 覆盖", () => {
    expect(
      resolveCapabilitySkuForScenario("custom.x", {
        "custom.x": { capabilitySkuId: "cap.custom" },
      }),
    ).toBe("cap.custom");
    expect(DEMO_BILLING_CAPABILITY_MAP["trade.spot.limit_order"]).toEqual({
      capabilitySkuId: "cap.agent.trade",
    });
  });
});
