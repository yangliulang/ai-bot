/**
 * **`BILLING_CAPABILITY_MAP`** 小样 · **scenarioId → Capability SKU**
 *
 * **规格**：[`keys.md` §5](../../../../specs/requirements/domains/admin/trading-agent-config/keys.md) ·
 * [`commerce-model.md` §3](../../../../specs/requirements/domains/admin/billing-management/commerce-model.md)。
 *
 * 生产真源为 **配置服务 / CMS**；本文件 **Demo 映射** 与 Admin **mockCommercePhase2AdminSnapshot** 同窗。
 */

export type BillingCapabilityMapEntry = {
  capabilitySkuId: string;
};

/** 与 [`scenarioSkillMap`](../skillPublish/scenarioSkillMap.ts) 写路径行 **同窗索引** */
export const DEMO_BILLING_CAPABILITY_MAP: Record<string, BillingCapabilityMapEntry> =
  {
    "trade.spot.flash_convert": { capabilitySkuId: "cap.agent.trade" },
    "trade.spot.limit_order": { capabilitySkuId: "cap.agent.trade" },
    "trade.spot.amend_limit_order": { capabilitySkuId: "cap.agent.trade" },
    "trade.futures.market_order": { capabilitySkuId: "cap.agent.trade" },
    "trade.futures.limit_order": { capabilitySkuId: "cap.agent.trade" },
    "trade.futures.amend_limit_order": { capabilitySkuId: "cap.agent.trade" },
    "trade.futures.take_profit_stop": { capabilitySkuId: "cap.agent.trade" },
    "futures.condition.order_create": { capabilitySkuId: "cap.agent.trade" },
    "margin.cross.market_order": { capabilitySkuId: "cap.agent.trade" },
    "margin.cross.limit_order": { capabilitySkuId: "cap.agent.trade" },
    "wealth.subscribe": { capabilitySkuId: "cap.agent.trade" },
    "wealth.redeem": { capabilitySkuId: "cap.agent.trade" },
  };

const ANALYSIS_SCENARIO_PREFIXES = ["analysis.", "market.query", "qa."] as const;

/**
 * 解析本笔请求应消耗的 **Capability SKU**；未归类 → **`undefined`**（小样 **放行**，所内可 fail-closed）。
 */
export function resolveCapabilitySkuForScenario(
  scenarioId: string | undefined,
  map: Record<string, BillingCapabilityMapEntry> = DEMO_BILLING_CAPABILITY_MAP,
): string | undefined {
  const key = scenarioId?.trim();
  if (!key) return undefined;

  const direct = map[key];
  if (direct) return direct.capabilitySkuId;

  for (const prefix of ANALYSIS_SCENARIO_PREFIXES) {
    if (key.startsWith(prefix)) return "cap.agent.analyze";
  }
  if (key.includes("monitor")) return "cap.agent.monitoring";

  return undefined;
}
