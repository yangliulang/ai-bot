import { describe, expect, it } from "vitest";
import {
  runCommerceEntitlementPreflight,
  type CommerceEntitlementPreflightInput,
} from "./commerceEntitlementPreflightGate";

describe("runCommerceEntitlementPreflight", () => {
  it("相位关：轨 B 未启用恒通过", () => {
    const input: CommerceEntitlementPreflightInput = {
      phase2CommerceRailsEnabled: false,
      capabilitySkuId: "cap.llm.turn",
      remainingForSku: 0,
    };
    expect(runCommerceEntitlementPreflight(input)).toEqual({ ok: true });
  });

  it("轨 B 开 + SKU + remaining>0 → 通过", () => {
    expect(
      runCommerceEntitlementPreflight({
        phase2CommerceRailsEnabled: true,
        capabilitySkuId: "cap.llm.turn",
        remainingForSku: 3,
      }),
    ).toEqual({ ok: true });
  });

  it("轨 B 开 + SKU + remaining=0 → 阻断", () => {
    expect(
      runCommerceEntitlementPreflight({
        phase2CommerceRailsEnabled: true,
        capabilitySkuId: "cap.llm.turn",
        remainingForSku: 0,
      }),
    ).toEqual({
      ok: false,
      code: "COMMERCE_ENTITLEMENT_EXHAUSTED",
      capabilitySkuId: "cap.llm.turn",
    });
  });

  it("轨 B 开 + SKU + remaining undefined → 小样放行（所内可 fail-closed）", () => {
    expect(
      runCommerceEntitlementPreflight({
        phase2CommerceRailsEnabled: true,
        capabilitySkuId: "cap.llm.turn",
        remainingForSku: undefined,
      }),
    ).toEqual({ ok: true });
  });

  it("轨 B 开 + 无 SKU → 放行", () => {
    expect(
      runCommerceEntitlementPreflight({
        phase2CommerceRailsEnabled: true,
        capabilitySkuId: undefined,
        remainingForSku: 0,
      }),
    ).toEqual({ ok: true });
  });
});
