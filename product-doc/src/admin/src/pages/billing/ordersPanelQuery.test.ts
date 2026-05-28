import { describe, expect, it } from "vitest";
import { MOCK_COMMERCE_CRYPTO_ORDERS } from "../../data/subscriptionCatalogMock";
import { filterCommerceOrders, parseOrdersPanelQuery } from "./ordersPanelQuery";

describe("ordersPanelQuery", () => {
  it("parses status from URL", () => {
    const q = parseOrdersPanelQuery(new URLSearchParams("status=SETTLED&userId=u-1"));
    expect(q.status).toBe("SETTLED");
    expect(q.userId).toBe("u-1");
  });

  it("filters by numeric order id substring", () => {
    const sample = MOCK_COMMERCE_CRYPTO_ORDERS[0];
    const rows = filterCommerceOrders(MOCK_COMMERCE_CRYPTO_ORDERS, {
      orderId: sample.orderId.slice(-4),
      userId: "",
      productId: "",
      kind: "",
      status: "",
      network: "",
    });
    expect(rows.some((r) => r.orderId === sample.orderId)).toBe(true);
  });
});
