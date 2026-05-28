import { zhCapabilitySku } from "../../copy/billingLabels";
import { normalizeResourceId } from "../../data/resourcePackLegacy";
import type { MockCommerceResourcePack, MockCommerceSubscriptionTier } from "../../data/types";

const CAPABILITY_ORDER = [
  "cap.agent.analyze",
  "cap.agent.trade",
  "cap.agent.monitoring",
] as const;

export function packsByResourceIdMap(packs: MockCommerceResourcePack[]): Map<string, MockCommerceResourcePack> {
  return new Map(packs.map((p) => [p.resourceId, p]));
}

export function resolvePacksForTier(
  tier: Pick<MockCommerceSubscriptionTier, "resourcePackIds">,
  allPacks: MockCommerceResourcePack[],
): MockCommerceResourcePack[] {
  const map = packsByResourceIdMap(allPacks);
  return tier.resourcePackIds
    .map((id) => normalizeResourceId(id))
    .map((id) => map.get(id))
    .filter((p): p is MockCommerceResourcePack => !!p);
}

/** 同 Capability 多资源时累加配额 */
export function aggregateQuotaByCapability(
  packs: MockCommerceResourcePack[],
): Record<string, number> {
  const out: Record<string, number> = {};
  for (const pack of packs) {
    out[pack.capabilitySkuId] = (out[pack.capabilitySkuId] ?? 0) + pack.quotaUnits;
  }
  return out;
}

export function formatEffectiveQuotaSummary(
  packs: MockCommerceResourcePack[],
  periodLabel?: string,
): string {
  const agg = aggregateQuotaByCapability(packs);
  const parts = CAPABILITY_ORDER.filter((id) => agg[id] != null).map((id) => {
    const short = zhCapabilitySku(id).replace(/^Agent\s*/, "");
    return `${short} ${agg[id]!.toLocaleString("zh-CN")}`;
  });
  if (parts.length === 0) return "未关联资源";
  const suffix = periodLabel ? ` / ${periodLabel}` : "";
  return `${parts.join(" · ")}${suffix}`;
}
