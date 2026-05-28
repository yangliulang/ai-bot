import {
  BILLING_SCENARIO_PREFIX_RULES,
  type BillingScenarioMappingRow,
} from "../../data/billingRulesSeed";

/** 与 Runtime Demo 同窗：显式映射 → 前缀 → 监控包含 → 未命中 */
export function resolveCapabilityForScenario(
  scenarioId: string | undefined,
  explicitMap: BillingScenarioMappingRow[],
): string | undefined {
  const key = scenarioId?.trim();
  if (!key) return undefined;

  const direct = explicitMap.find((r) => r.scenarioId === key);
  if (direct) return direct.capabilitySkuId;

  for (const rule of BILLING_SCENARIO_PREFIX_RULES) {
    if (rule.kind === "prefix") {
      for (const prefix of rule.prefixes) {
        if (key.startsWith(prefix)) return rule.capabilitySkuId;
      }
    } else if (key.includes(rule.contains)) {
      return rule.capabilitySkuId;
    }
  }

  return undefined;
}
