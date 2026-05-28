import { describe, expect, it } from "vitest";

/** 与 CommerceCapabilityCatalogEditor 内联逻辑同窗 */
function rowsToCatalogBody(
  catalogVersion: string,
  rows: Array<{
    capabilitySkuId: string;
    displayLabel: string;
    remaining: number;
    resetsAt: string | null;
  }>,
) {
  return {
    catalogVersion,
    items: rows.map((r) => ({
      capabilitySkuId: r.capabilitySkuId,
      displayLabel: r.displayLabel,
      remaining: r.remaining,
      resetsAt: r.resetsAt?.trim() ? r.resetsAt : null,
    })),
  };
}

describe("commerce catalog PATCH body", () => {
  it("maps form rows to OpenAPI catalog shape", () => {
    const body = rowsToCatalogBody("v1", [
      {
        capabilitySkuId: "cap.agent.trade",
        displayLabel: "交易",
        remaining: 10,
        resetsAt: "",
      },
    ]);
    expect(body.items[0]?.resetsAt).toBeNull();
    expect(body.catalogVersion).toBe("v1");
  });
});
