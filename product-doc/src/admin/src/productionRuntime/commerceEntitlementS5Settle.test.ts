import { describe, expect, it, vi } from "vitest";
import {
  deriveEntitlementDebitIdempotencyKey,
  executeConsumptionSettlement,
} from "./commerceEntitlementS5Settle";
import { INTERNAL_BILLING_ENTITLEMENTS_PATHS } from "./internalBillingEntitlementsAdapter";

describe("commerceEntitlementS5Settle idempotency keys", () => {
  it("SC-B20 · 同窗 executionId · rail-b 后缀", () => {
    expect(deriveEntitlementDebitIdempotencyKey("20260501000009")).toBe(
      "20260501000009:rail-b:entitlement-debit",
    );
  });
});

describe("executeConsumptionSettlement", () => {
  it("phase2 关 · 不发 debit", async () => {
    const fetchImpl = vi.fn();
    const out = await executeConsumptionSettlement(
      { baseUrl: "https://gw", fetchImpl },
      {
        phase2CommerceRailsEnabled: false,
        executionId: "20260501000001",
        entitlementDebit: { capabilitySkuId: "cap.x" },
      },
    );
    expect(out.ok).toBe(true);
    if (out.ok) {
      expect(out.result.entitlementDebit).toBeUndefined();
    }
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("phase2 开 · debit SUCCESS", async () => {
    const fetchImpl = vi.fn(async (url: string | URL, init?: RequestInit) => {
      expect(String(url)).toContain(INTERNAL_BILLING_ENTITLEMENTS_PATHS.debit);
      expect(JSON.parse(String(init?.body)).idempotencyKey).toBe(
        "20260501000002:rail-b:entitlement-debit",
      );
      return new Response(
        JSON.stringify({
          billingTraceId: "bt-b",
          commercialSettlementType: "ENTITLEMENT_DEBIT",
          status: "SUCCESS",
        }),
        { status: 200 },
      );
    });

    const out = await executeConsumptionSettlement(
      { baseUrl: "https://gw", fetchImpl },
      {
        phase2CommerceRailsEnabled: true,
        executionId: "20260501000002",
        entitlementDebit: { capabilitySkuId: "cap.x" },
      },
    );

    expect(out.ok).toBe(true);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("debit INSUFFICIENT", async () => {
    const fetchImpl = vi.fn(async () =>
      new Response(
        JSON.stringify({
          billingTraceId: "bt-b",
          commercialSettlementType: "ENTITLEMENT_DEBIT",
          status: "INSUFFICIENT",
        }),
        { status: 200 },
      ),
    );

    const out = await executeConsumptionSettlement(
      { baseUrl: "https://gw", fetchImpl },
      {
        phase2CommerceRailsEnabled: true,
        executionId: "20260501000003",
        entitlementDebit: { capabilitySkuId: "cap.y" },
      },
    );

    expect(out).toMatchObject({
      ok: false,
      code: "CONSUMPTION_SETTLEMENT_ENTITLEMENT_INSUFFICIENT",
      capabilitySkuId: "cap.y",
    });
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });
});
