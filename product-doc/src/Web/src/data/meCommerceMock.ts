/** 同窗 `getMockMeCommerceEntitlementsSummary`（admin mock · FR-B17） */
export type MeCommerceBucket = {
  capabilitySkuId: string;
  displayLabel: string;
  remaining: number;
  /** 周期配额上限（演示） */
  quotaTotal: number;
  resetsAt: string | null;
};

export type MeCommerceEntitlementsSummary = {
  subscriptionTierDisplay: string | null;
  subscriptionTierSku: string | null;
  subscriptionStatus: "active" | "expired" | "none";
  periodStart: string | null;
  periodEnd: string | null;
  buckets: MeCommerceBucket[];
};

export const MOCK_ME_COMMERCE_SUMMARY: MeCommerceEntitlementsSummary = {
  subscriptionTierDisplay: "Pro",
  subscriptionTierSku: "tier_pro",
  subscriptionStatus: "active",
  periodStart: "2026-05-01T00:00:00Z",
  periodEnd: "2026-06-01T00:00:00Z",
  buckets: [
    {
      capabilitySkuId: "cap.agent.analyze",
      displayLabel: "AI 分析 · 月度配额",
      remaining: 1280,
      quotaTotal: 3000,
      resetsAt: "2026-06-01T00:00:00Z",
    },
    {
      capabilitySkuId: "cap.agent.trade",
      displayLabel: "自动交易 · 月度配额",
      remaining: 0,
      quotaTotal: 1500,
      resetsAt: "2026-06-01T00:00:00Z",
    },
    {
      capabilitySkuId: "cap.pack.execution.100",
      displayLabel: "加购包 · 100 次执行",
      remaining: 37,
      quotaTotal: 100,
      resetsAt: null,
    },
  ],
};

export function labelCapabilitySku(sku: string): string {
  const map: Record<string, string> = {
    "cap.agent.analyze": "AI 分析",
    "cap.agent.trade": "自动交易",
    "cap.agent.monitoring": "监控类",
    "cap.pack.execution.100": "加购包",
  };
  return map[sku] ?? sku;
}
