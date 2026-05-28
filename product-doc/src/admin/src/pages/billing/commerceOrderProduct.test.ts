import { describe, expect, it } from "vitest";
import { RESOURCE_PACK_SEED, SUBSCRIPTION_TIER_SEED } from "../../data/subscriptionCatalogMock";
import { resolveCommerceOrderProduct } from "./commerceOrderProduct";

describe("resolveCommerceOrderProduct", () => {
  it("resolves tier name for upgrade orders", () => {
    const view = resolveCommerceOrderProduct("upgrade", "1002", SUBSCRIPTION_TIER_SEED, RESOURCE_PACK_SEED);
    expect(view.productKind).toBe("tier");
    expect(view.title).not.toBe("未知套餐");
  });

  it("resolves pack name for addon orders", () => {
    const view = resolveCommerceOrderProduct("pack", "3001", SUBSCRIPTION_TIER_SEED, RESOURCE_PACK_SEED);
    expect(view.productKind).toBe("resource");
    expect(view.title).not.toBe("未知资源");
  });
});
