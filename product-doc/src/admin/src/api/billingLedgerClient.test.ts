import { describe, expect, it } from "vitest";
import { mapBillingTraceItemToLedgerRow } from "./billingLedgerClient";

describe("billingLedgerClient", () => {
  it("mapBillingTraceItemToLedgerRow maps API-shaped items", () => {
    const row = mapBillingTraceItemToLedgerRow({
      recordedAt: "2026-05-07T01:00:00Z",
      billingTraceId: "bt-1",
      userId: "u-1",
      executionId: "20260501000001",
      capabilitySkuId: "cap.agent.trade",
      debitStatus: "SUCCESS",
      failureReason: "none",
      consumedUnits: 1,
      intentType: "交易",
      executionStatus: "COMPLETED",
    });
    expect(row.userIdMasked).toBe("u-1");
    expect(row.commercialSettlementType).toBe("ENTITLEMENT_DEBIT");
  });
});
