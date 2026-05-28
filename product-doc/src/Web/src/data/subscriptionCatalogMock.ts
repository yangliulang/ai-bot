/** 订阅商品目录（演示 · 生产由 commerce 目录 API 承接） */

export type SubscriptionPlan = {
  sku: string;
  name: string;
  tagline: string;
  priceUsdt: string;
  periodLabel: string;
  highlights: string[];
  analyzeQuota: number;
  tradeQuota: number;
  recommended?: boolean;
};

export type AddOnPack = {
  sku: string;
  name: string;
  description: string;
  priceUsdt: string;
  capabilitySkuId: string;
  units: number;
};

export const SUBSCRIPTION_PLANS: SubscriptionPlan[] = [
  {
    sku: "tier_starter",
    name: "Starter",
    tagline: "体验 Agent 分析与轻量交易",
    priceUsdt: "29",
    periodLabel: "月",
    highlights: ["分析 500 次/月", "交易 200 次/月"],
    analyzeQuota: 500,
    tradeQuota: 200,
  },
  {
    sku: "tier_pro",
    name: "Pro",
    tagline: "主力交易与深度分析",
    priceUsdt: "99",
    periodLabel: "月",
    highlights: ["分析 3,000 次/月", "交易 1,500 次/月", "优先队列"],
    analyzeQuota: 3000,
    tradeQuota: 1500,
    recommended: true,
  },
  {
    sku: "tier_enterprise",
    name: "Enterprise",
    tagline: "团队与高并发场景",
    priceUsdt: "299",
    periodLabel: "月",
    highlights: ["分析 15,000 次/月", "交易 8,000 次/月", "专属支持"],
    analyzeQuota: 15000,
    tradeQuota: 8000,
  },
];

export const ADD_ON_PACKS: AddOnPack[] = [
  {
    sku: "pack_trade_100",
    name: "交易加购包",
    description: "自动交易 Capability +100 次，用完即止",
    priceUsdt: "19",
    capabilitySkuId: "cap.agent.trade",
    units: 100,
  },
  {
    sku: "pack_analyze_50",
    name: "分析加购包",
    description: "AI 分析 Capability +50 次",
    priceUsdt: "12",
    capabilitySkuId: "cap.agent.analyze",
    units: 50,
  },
  {
    sku: "pack_execution_100",
    name: "通用执行包",
    description: "跨场景执行额度 +100 次",
    priceUsdt: "25",
    capabilitySkuId: "cap.pack.execution.100",
    units: 100,
  },
];

export function findPlan(sku: string): SubscriptionPlan | undefined {
  return SUBSCRIPTION_PLANS.find((p) => p.sku === sku);
}

export function findPack(sku: string): AddOnPack | undefined {
  return ADD_ON_PACKS.find((p) => p.sku === sku);
}
