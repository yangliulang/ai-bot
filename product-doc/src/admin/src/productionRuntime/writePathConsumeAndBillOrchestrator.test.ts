import { describe, expect, it, vi } from "vitest";
import {
  COMMERCE_ENTITLEMENT_BALANCE_HTTP_ERROR,
  runWritePathConsumeAndBill,
} from "./writePathConsumeAndBillOrchestrator";
import { INTERNAL_BILLING_ENTITLEMENTS_PATHS } from "./internalBillingEntitlementsAdapter";

const hostBase = {
  internalBillingBaseUrl: "https://gw.internal",
  requestHeaders: { "X-Internal-Auth": "demo" },
} as const;

describe("runWritePathConsumeAndBill", () => {
  it("phase2 关 · S2/S5 均不发 HTTP · railsSkipped", async () => {
    const fetchImpl = vi.fn();
    const out = await runWritePathConsumeAndBill(
      { ...hostBase, phase2CommerceRailsEnabled: false, fetchImpl },
      {
        userId: "u1",
        scenarioId: "trade.spot.limit_order",
        executionId: "20260501006001",
      },
    );
    expect(out).toMatchObject({
      ok: true,
      executionId: "20260501006001",
      billingTraceId: "",
      railsSkipped: true,
    });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("S2 remaining=0 → 阻断 · 不调 debit", async () => {
    const fetchImpl = vi.fn(async (url: string | URL) => {
      expect(String(url)).toContain(INTERNAL_BILLING_ENTITLEMENTS_PATHS.balance);
      return new Response(
        JSON.stringify({
          userId: "u1",
          buckets: [{ capabilitySkuId: "cap.agent.trade", remaining: 0 }],
        }),
        { status: 200 },
      );
    });

    const out = await runWritePathConsumeAndBill(
      { ...hostBase, phase2CommerceRailsEnabled: true, fetchImpl },
      {
        userId: "u1",
        scenarioId: "trade.spot.limit_order",
        executionId: "20260501006002",
      },
    );

    expect(out).toMatchObject({
      ok: false,
      stage: "S2",
      code: "COMMERCE_ENTITLEMENT_EXHAUSTED",
      stableReason: "BUDGET_OR_QUOTA",
    });
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("S2 balance 502 → fail-closed · 不静默放行", async () => {
    const fetchImpl = vi.fn(async () => new Response("", { status: 502 }));

    const out = await runWritePathConsumeAndBill(
      { ...hostBase, phase2CommerceRailsEnabled: true, fetchImpl },
      {
        userId: "u1",
        scenarioId: "trade.spot.limit_order",
        executionId: "20260501060502",
      },
    );

    expect(out).toEqual({
      ok: false,
      stage: "S2",
      code: COMMERCE_ENTITLEMENT_BALANCE_HTTP_ERROR,
      stableReason: "BUDGET_OR_QUOTA",
      httpStatus: 502,
    });
  });

  it("S2 通过 · S5 仅轨 B debit SUCCESS", async () => {
    const calls: string[] = [];
    const fetchImpl = vi.fn(async (url: string | URL, init?: RequestInit) => {
      calls.push(String(url));
      if (String(url).includes(INTERNAL_BILLING_ENTITLEMENTS_PATHS.balance)) {
        return new Response(
          JSON.stringify({
            userId: "u1",
            buckets: [{ capabilitySkuId: "cap.agent.trade", remaining: 3 }],
          }),
          { status: 200 },
        );
      }
      if (String(url).includes(INTERNAL_BILLING_ENTITLEMENTS_PATHS.debit)) {
        expect(JSON.parse(String(init?.body)).idempotencyKey).toBe(
          "20260501006003:rail-b:entitlement-debit",
        );
        return new Response(
          JSON.stringify({
            billingTraceId: "bt-rail-b",
            commercialSettlementType: "ENTITLEMENT_DEBIT",
            status: "SUCCESS",
          }),
          { status: 200 },
        );
      }
      return new Response("", { status: 500 });
    });

    const out = await runWritePathConsumeAndBill(
      { ...hostBase, phase2CommerceRailsEnabled: true, fetchImpl },
      {
        userId: "u1",
        scenarioId: "trade.spot.limit_order",
        executionId: "20260501006003",
      },
    );

    expect(out).toEqual({
      ok: true,
      executionId: "20260501006003",
      billingTraceId: "bt-rail-b",
      commercialSettlementType: "ENTITLEMENT_DEBIT",
      railsSkipped: false,
    });
    expect(calls).toHaveLength(2);
    expect(calls[1]).toContain("entitlements/debit");
    expect(calls.some((u) => u.includes("/billing/charges"))).toBe(false);
  });

  it("S5 debit INSUFFICIENT → 终止", async () => {
    const fetchImpl = vi.fn(async (url: string | URL) => {
      if (String(url).includes("balance")) {
        return new Response(
          JSON.stringify({
            userId: "u1",
            buckets: [{ capabilitySkuId: "cap.agent.trade", remaining: 1 }],
          }),
          { status: 200 },
        );
      }
      return new Response(
        JSON.stringify({
          billingTraceId: "bt-fail",
          commercialSettlementType: "ENTITLEMENT_DEBIT",
          status: "INSUFFICIENT",
        }),
        { status: 200 },
      );
    });

    const out = await runWritePathConsumeAndBill(
      { ...hostBase, phase2CommerceRailsEnabled: true, fetchImpl },
      {
        userId: "u1",
        scenarioId: "trade.spot.limit_order",
        executionId: "20260501006004",
      },
    );

    expect(out).toMatchObject({
      ok: false,
      stage: "S5",
      code: "CONSUMPTION_SETTLEMENT_ENTITLEMENT_INSUFFICIENT",
      executionId: "20260501006004",
    });
  });
});
