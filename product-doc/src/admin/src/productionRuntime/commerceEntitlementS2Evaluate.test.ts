import { describe, expect, it, vi } from "vitest";
import {
  INTERNAL_BILLING_ENTITLEMENTS_PATHS,
  pickRemainingForCapabilitySku,
} from "./internalBillingEntitlementsAdapter";
import { evaluateCommerceEntitlementS2Gate } from "./commerceEntitlementS2Evaluate";

describe("pickRemainingForCapabilitySku", () => {
  it("精确匹配 capabilitySkuId", () => {
    expect(
      pickRemainingForCapabilitySku(
        {
          userId: "u",
          buckets: [
            { capabilitySkuId: "cap.a", remaining: 10 },
            { capabilitySkuId: "cap.b", remaining: 0 },
          ],
        },
        "cap.b",
      ),
    ).toBe(0);
  });

  it("无桶或为 undefined · 返回 undefined", () => {
    expect(
      pickRemainingForCapabilitySku(
        { userId: "u", buckets: [{ capabilitySkuId: "cap.a" }] },
        "cap.a",
      ),
    ).toBeUndefined();
    expect(
      pickRemainingForCapabilitySku({ userId: "u", buckets: [] }, "cap.a"),
    ).toBeUndefined();
  });

  it("trim capabilitySkuId", () => {
    expect(
      pickRemainingForCapabilitySku(
        {
          userId: "u",
          buckets: [{ capabilitySkuId: "x", remaining: 1 }],
        },
        " x ",
      ),
    ).toBe(1);
  });
});

describe("evaluateCommerceEntitlementS2Gate", () => {
  it("phase2 关 · 不发请求", async () => {
    const fetchImpl = vi.fn();
    const out = await evaluateCommerceEntitlementS2Gate(
      { baseUrl: "https://gw.example", fetchImpl },
      {
        phase2CommerceRailsEnabled: false,
        userId: "u1",
        capabilitySkuId: "cap.z",
      },
    );
    expect(out).toEqual({ ok: true });
    expect(fetchImpl).not.toHaveBeenCalled();
  });

  it("phase2 开 · balance remaining=0 → 阻断", async () => {
    const fetchImpl = vi.fn(async (url: string | URL, init?: RequestInit) => {
      expect(init?.method ?? "GET").toBe("GET");
      expect(String(url)).toContain(
        INTERNAL_BILLING_ENTITLEMENTS_PATHS.balance,
      );
      return new Response(
        JSON.stringify({
          userId: "u1",
          buckets: [{ capabilitySkuId: "cap.z", remaining: 0 }],
        }),
        { status: 200 },
      );
    });

    const out = await evaluateCommerceEntitlementS2Gate(
      { baseUrl: "https://gw.example", fetchImpl },
      {
        phase2CommerceRailsEnabled: true,
        userId: "u1",
        capabilitySkuId: "cap.z",
      },
    );

    expect(out).toEqual({
      ok: false,
      code: "COMMERCE_ENTITLEMENT_EXHAUSTED",
      capabilitySkuId: "cap.z",
    });
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("phase2 开 · remaining 正 · 通过", async () => {
    const fetchImpl = vi.fn(
      async () =>
        new Response(
          JSON.stringify({
            userId: "u1",
            buckets: [{ capabilitySkuId: "cap.z", remaining: 99 }],
          }),
          { status: 200 },
        ),
    );
    await expect(
      evaluateCommerceEntitlementS2Gate(
        { baseUrl: "https://gw", fetchImpl },
        {
          phase2CommerceRailsEnabled: true,
          userId: "u1",
          capabilitySkuId: "cap.z",
        },
      ),
    ).resolves.toEqual({ ok: true });
  });
});
