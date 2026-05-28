import { describe, expect, it, vi } from "vitest";
import {
  parseConsumptionBillingHostConfigFromEnv,
  runConsumeAndBillS2CommerceGate,
  runConsumeAndBillS5Settlement,
} from "./consumptionBillingHost";
import {
  INTERNAL_BILLING_ENTITLEMENTS_PATHS,
} from "./internalBillingEntitlementsAdapter";
const hostBase = {
  internalBillingBaseUrl: "https://gw.internal",
  requestHeaders: { "X-Internal-Auth": "demo" },
} as const;

describe("parseConsumptionBillingHostConfigFromEnv", () => {
  it("PHASE2 开关与 baseUrl", () => {
    expect(
      parseConsumptionBillingHostConfigFromEnv({
        PHASE2_COMMERCE_RAILS_ENABLED: "true",
        INTERNAL_BILLING_BASE_URL: "https://bff/",
      }),
    ).toEqual({
      phase2CommerceRailsEnabled: true,
      internalBillingBaseUrl: "https://bff/",
      requestHeaders: undefined,
    });
    expect(
      parseConsumptionBillingHostConfigFromEnv({}),
    ).toMatchObject({ phase2CommerceRailsEnabled: false, internalBillingBaseUrl: "" });
  });
});

describe("runConsumeAndBillS2CommerceGate", () => {
  it("phase2 关 · 不发 HTTP", async () => {
    const fetchImpl = vi.fn();
    const out = await runConsumeAndBillS2CommerceGate(
      { ...hostBase, phase2CommerceRailsEnabled: false, fetchImpl },
      { userId: "u1", scenarioId: "trade.spot.limit_order" },
    );
    expect(out).toEqual({ ok: true });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("trade scenario · remaining=0 → S2 阻断 + stableReason", async () => {
    const fetchImpl = vi.fn(async (url: string | URL, init?: RequestInit) => {
      expect(init?.headers).toMatchObject({ "X-Internal-Auth": "demo" });
      expect(String(url)).toContain(INTERNAL_BILLING_ENTITLEMENTS_PATHS.balance);
      return new Response(
        JSON.stringify({
          userId: "u1",
          buckets: [{ capabilitySkuId: "cap.agent.trade", remaining: 0 }],
        }),
        { status: 200 },
      );
    });

    const out = await runConsumeAndBillS2CommerceGate(
      { ...hostBase, phase2CommerceRailsEnabled: true, fetchImpl },
      { userId: "u1", scenarioId: "trade.spot.limit_order" },
    );

    expect(out).toEqual({
      ok: false,
      stage: "S2",
      code: "COMMERCE_ENTITLEMENT_EXHAUSTED",
      capabilitySkuId: "cap.agent.trade",
      stableReason: "BUDGET_OR_QUOTA",
    });
  });
});

describe("runConsumeAndBillS5Settlement", () => {
  it("phase2 开 · trade scenario · ENTITLEMENT_DEBIT", async () => {
    const fetchImpl = vi.fn(async (url: string | URL, init?: RequestInit) => {
      expect(String(url)).toContain(INTERNAL_BILLING_ENTITLEMENTS_PATHS.debit);
      expect(JSON.parse(String(init?.body)).capabilitySkuId).toBe(
        "cap.agent.trade",
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

    const out = await runConsumeAndBillS5Settlement(
      { ...hostBase, phase2CommerceRailsEnabled: true, fetchImpl },
      {
        executionId: "20260501007001",
        scenarioId: "trade.spot.limit_order",
      },
    );

    expect(out.ok).toBe(true);
    if (out.ok) {
      expect(out.result.entitlementDebit?.billingTraceId).toBe("bt-b");
    }
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("未映射 scenario · phase2 开 · 跳过 debit", async () => {
    const fetchImpl = vi.fn();

    const out = await runConsumeAndBillS5Settlement(
      { ...hostBase, phase2CommerceRailsEnabled: true, fetchImpl },
      {
        executionId: "20260501007002",
        scenarioId: "unknown.scenario",
      },
    );

    expect(out.ok).toBe(true);
    if (out.ok) expect(out.result.entitlementDebit).toBeUndefined();
    expect(fetchImpl).not.toHaveBeenCalled();
  });

});
