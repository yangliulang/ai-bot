import { describe, expect, it } from "vitest";
import { formatCommerceOrderIdDisplay, isCommerceOrderId } from "./commerceOrderId";

describe("commerceOrderId", () => {
  it("accepts numeric order ids", () => {
    expect(isCommerceOrderId("202605111420001")).toBe(true);
  });

  it("rejects legacy string ids", () => {
    expect(isCommerceOrderId("ord_demo_01")).toBe(false);
  });

  it("formats display as digits only", () => {
    expect(formatCommerceOrderIdDisplay("202605111420001")).toBe("202605111420001");
  });
});
