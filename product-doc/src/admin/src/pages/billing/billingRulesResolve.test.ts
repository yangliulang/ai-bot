import { describe, expect, it } from "vitest";
import type { BillingScenarioMappingRow } from "../../data/billingRulesSeed";
import { resolveCapabilityForScenario } from "./billingRulesResolve";

const explicit: BillingScenarioMappingRow[] = [
  { scenarioId: "trade.spot.limit_order", capabilitySkuId: "cap.agent.trade" },
];

describe("resolveCapabilityForScenario", () => {
  it("returns explicit mapping first", () => {
    expect(resolveCapabilityForScenario("trade.spot.limit_order", explicit)).toBe("cap.agent.trade");
  });

  it("falls back to analysis prefix", () => {
    expect(resolveCapabilityForScenario("analysis.portfolio", explicit)).toBe("cap.agent.analyze");
  });

  it("falls back to monitor contains", () => {
    expect(resolveCapabilityForScenario("custom.monitor.alert", explicit)).toBe("cap.agent.monitoring");
  });

  it("returns undefined when unmatched", () => {
    expect(resolveCapabilityForScenario("unknown.scenario", explicit)).toBeUndefined();
  });
});
