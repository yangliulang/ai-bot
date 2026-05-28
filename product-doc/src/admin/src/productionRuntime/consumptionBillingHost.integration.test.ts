import { describe, expect, it } from "vitest";
import {
  runConsumeAndBillS2CommerceGate,
  runConsumeAndBillS5Settlement,
} from "./consumptionBillingHost";
import type { InternalEntitlementDebitResultBody, InternalEntitlementsBalanceResponseBody } from "./internalBillingEntitlementsAdapter";

/** MR-BILL-B1/B2 · 宿主 + mock fetch（模拟 staging BFF 响应形状） */
describe("consumptionBillingHost integration (mock fetch)", () => {
  const config = {
    phase2CommerceRailsEnabled: true,
    internalBillingBaseUrl: "http://bff.mock",
  };

  it("S2 blocks when remaining is 0", async () => {
    const fetchImpl = async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/entitlements/balance")) {
        return new Response(
          JSON.stringify({
            userId: "u-1",
            buckets: [{ capabilitySkuId: "cap.agent.trade", remaining: 0 }],
          } satisfies InternalEntitlementsBalanceResponseBody),
          { status: 200 },
        );
      }
      return new Response("not found", { status: 404 });
    };

    const out = await runConsumeAndBillS2CommerceGate(
      { ...config, fetchImpl },
      { userId: "u-1", scenarioId: "trade.spot.limit_order" },
    );
    expect(out.ok).toBe(false);
    if (!out.ok) {
      expect(out.capabilitySkuId).toBe("cap.agent.trade");
      expect(out.stableReason).toBe("BUDGET_OR_QUOTA");
    }
  });

  it("S5 debit succeeds with idempotent billingTraceId", async () => {
    const debitBody: InternalEntitlementDebitResultBody = {
      billingTraceId: "bt-20260501999999",
      commercialSettlementType: "ENTITLEMENT_DEBIT",
      status: "SUCCESS",
      consumedUnits: 1,
    };
    const fetchImpl = async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.includes("/entitlements/debit") && init?.method === "POST") {
        return new Response(JSON.stringify(debitBody), { status: 200 });
      }
      if (url.includes("/entitlements/balance")) {
        return new Response(
          JSON.stringify({
            userId: "u-1",
            buckets: [{ capabilitySkuId: "cap.agent.trade", remaining: 5 }],
          }),
          { status: 200 },
        );
      }
      return new Response("not found", { status: 404 });
    };

    const out = await runConsumeAndBillS5Settlement(
      { ...config, fetchImpl },
      { executionId: "20260501999999", scenarioId: "trade.spot.limit_order" },
    );
    expect(out.ok).toBe(true);
    if (out.ok) {
      expect(out.result.entitlementDebit?.billingTraceId).toBe("bt-20260501999999");
      expect(out.result.entitlementDebit?.commercialSettlementType).toBe("ENTITLEMENT_DEBIT");
    }
  });
});
