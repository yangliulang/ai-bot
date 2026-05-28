import type { MockCommerceResourcePack, MockCommerceSubscriptionTier } from "../../data/types";

export type CommerceOrderProductView = {
  title: string;
  productId: string;
  productKind: "tier" | "resource" | "unknown";
  listPriceUsdt: string;
  periodLabel?: string;
  capabilitySkuId?: string;
  quotaUnits?: number;
  tierDisplayName?: string;
};

export function resolveCommerceOrderProduct(
  orderKind: "upgrade" | "pack",
  productId: string,
  tiers: MockCommerceSubscriptionTier[],
  packs: MockCommerceResourcePack[],
): CommerceOrderProductView {
  if (orderKind === "upgrade") {
    const tier = tiers.find((t) => t.tierId === productId);
    return {
      title: tier?.name ?? "未知套餐",
      productId,
      productKind: tier ? "tier" : "unknown",
      listPriceUsdt: tier?.priceUsdt ?? "—",
      periodLabel: tier?.periodLabel,
      tierDisplayName: tier?.name,
    };
  }
  const pack = packs.find((p) => p.resourceId === productId);
  return {
    title: pack?.name ?? "未知资源",
    productId,
    productKind: pack ? "resource" : "unknown",
    listPriceUsdt: pack?.priceUsdt ?? "—",
    periodLabel: pack?.periodLabel,
    capabilitySkuId: pack?.capabilitySkuId,
    quotaUnits: pack?.quotaUnits,
  };
}
