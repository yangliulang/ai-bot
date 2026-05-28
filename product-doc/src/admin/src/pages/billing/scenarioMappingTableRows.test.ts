import { describe, expect, it } from "vitest";
import { buildScenarioMappingTableRows } from "./scenarioMappingTableRows";

describe("buildScenarioMappingTableRows", () => {
  it("places auto rules before custom rows", () => {
    const rows = buildScenarioMappingTableRows([
      { scenarioId: "trade.spot.limit_order", capabilitySkuId: "cap.agent.trade" },
    ]);
    expect(rows[0]?.source).toBe("auto");
    expect(rows.at(-1)?.source).toBe("custom");
  });
});
