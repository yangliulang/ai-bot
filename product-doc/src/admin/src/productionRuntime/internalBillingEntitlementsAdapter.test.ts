import { describe, expect, it, vi } from "vitest";
import {
  BillingEntitlementsHttpError,
  getInternalBillingEntitlementsBalance,
  INTERNAL_BILLING_ENTITLEMENTS_PATHS,
  postInternalBillingEntitlementsDebit,
  postInternalCommercePackGrantsApply,
} from "./internalBillingEntitlementsAdapter";

describe("internalBillingEntitlementsAdapter", () => {
  it("getInternalBillingEntitlementsBalance：URL 与 query", async () => {
    const fetchImpl = vi.fn(async (url: string | URL) => {
      expect(String(url)).toBe(
        "https://gw.example/api/v1/internal/billing/entitlements/balance?userId=u-demo",
      );
      return new Response(
        JSON.stringify({
          userId: "u-demo",
          buckets: [{ capabilitySkuId: "cap.x", remaining: 2 }],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      );
    });

    const out = await getInternalBillingEntitlementsBalance(
      { baseUrl: "https://gw.example/", fetchImpl },
      { userId: "u-demo" },
    );

    expect(out.buckets).toHaveLength(1);
    expect(out.buckets[0].remaining).toBe(2);
    expect(fetchImpl).toHaveBeenCalledTimes(1);
  });

  it("baseUrl 去尾随斜杠", async () => {
    const fetchImpl = vi.fn(async () =>
      new Response(JSON.stringify({ userId: "u", buckets: [] }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    await getInternalBillingEntitlementsBalance(
      { baseUrl: "https://gw.example///", fetchImpl },
      { userId: "u" },
    );
    const called = String(vi.mocked(fetchImpl).mock.calls[0]?.[0] ?? "");
    expect(called.startsWith("https://gw.example/")).toBe(true);
  });

  it("postInternalBillingEntitlementsDebit · body JSON", async () => {
    const fetchImpl = vi.fn(async (_url: string | URL, init?: RequestInit) => {
      expect(init?.method).toBe("POST");
      expect(init?.headers).toMatchObject({
        Accept: "application/json",
        "Content-Type": "application/json",
      });
      expect(JSON.parse(String(init?.body))).toMatchObject({
        executionId: "20260501000001",
        idempotencyKey: "idem-1",
        capabilitySkuId: "cap.y",
      });
      return new Response(
        JSON.stringify({
          billingTraceId: "00000000-0000-4000-8000-000000000001",
          commercialSettlementType: "ENTITLEMENT_DEBIT",
          status: "SUCCESS",
        }),
        { status: 200 },
      );
    });

    await postInternalBillingEntitlementsDebit(
      { baseUrl: "https://gw.example", fetchImpl },
      {
        executionId: "20260501000001",
        idempotencyKey: "idem-1",
        capabilitySkuId: "cap.y",
      },
    );
    expect(fetchImpl).toHaveBeenCalledWith(
      expect.stringContaining(INTERNAL_BILLING_ENTITLEMENTS_PATHS.debit),
      expect.anything(),
    );
  });

  it("非 2xx → BillingEntitlementsHttpError", async () => {
    const fetchImpl = vi.fn(
      async () =>
        new Response(JSON.stringify({ code: "BAD", message: "nope" }), {
          status: 400,
        }),
    );

    await expect(
      postInternalCommercePackGrantsApply(
        { baseUrl: "https://gw.example", fetchImpl },
        {
          userId: "u",
          packSkuId: "pack.a",
          quantity: 1,
          purchaseRef: "psp-r",
          idempotencyKey: "idem-p",
        },
      ),
    ).rejects.toMatchObject({
      status: 400,
      problem: { message: "nope" },
    });
  });

  it("BillingEntitlementsHttpError 可被 instanceof 捕获", async () => {
    const fetchImpl = vi.fn(async () => new Response("", { status: 502 }));
    try {
      await getInternalBillingEntitlementsBalance({ baseUrl: "https://gw", fetchImpl }, { userId: "z" });
      expect.fail("expected throw");
    } catch (e) {
      expect(e).toBeInstanceOf(BillingEntitlementsHttpError);
      expect((e as BillingEntitlementsHttpError).status).toBe(502);
    }
  });
});
