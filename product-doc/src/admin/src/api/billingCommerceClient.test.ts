import { describe, expect, it } from "vitest";
import {
  mapCatalogAndQuotaToSnapshot,
  mapUserOverviewToBucketRows,
} from "./billingCommerceClient";

describe("billingCommerceClient mappers", () => {
  it("mapCatalogAndQuotaToSnapshot merges OpenAPI-shaped payloads", () => {
    const snap = mapCatalogAndQuotaToSnapshot(
      {
        catalogVersion: "v-test",
        items: [
          {
            capabilitySkuId: "cap.agent.trade",
            displayLabel: "交易",
            remaining: 10,
            resetsAt: "2026-06-01T00:00:00Z",
          },
        ],
      },
      {
        window: "24h",
        blockedEventCountByCapability: { "cap.agent.trade": 3 },
        topUsersSample: [{ userId: "u-1", blockCount: 2 }],
      },
    );
    expect(snap.catalogVersion).toBe("v-test");
    expect(snap.capabilityBuckets).toHaveLength(1);
    expect(snap.quotaBlockedSummary.topUsersSample[0]?.userIdMasked).toBe("u-1");
  });

  it("mapUserOverviewToBucketRows prefers packGrants", () => {
    const rows = mapUserOverviewToBucketRows({
      packGrants: [{ capabilitySkuId: "cap.agent.analyze", remaining: 5 }],
    });
    expect(rows[0]?.capabilitySkuId).toBe("cap.agent.analyze");
    expect(rows[0]?.remaining).toBe(5);
  });
});
