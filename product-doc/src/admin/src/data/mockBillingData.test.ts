import { describe, expect, it } from "vitest";
import { lookupBillingCorrelate, mockBillingLedger, mockObsBilling } from "./mockBillingData";

describe("mockBillingData · 轨 B 演示数据", () => {
  it("ledger 与 obs 行数一致且含 capabilitySkuId", () => {
    expect(mockBillingLedger.length).toBeGreaterThan(0);
    expect(mockObsBilling.length).toBe(mockBillingLedger.length);
    for (const row of mockBillingLedger) {
      expect(row.capabilitySkuId).toBeTruthy();
      expect(row.commercialSettlementType).toBe("ENTITLEMENT_DEBIT");
      expect(row.debitStatus).toBeTruthy();
    }
  });

  it("lookupBillingCorrelate 可按 executionId 命中", () => {
    const hits = lookupBillingCorrelate("20260501001001");
    expect(hits.some((r) => r.executionId === "20260501001001")).toBe(true);
  });
});
