import {
  BILLING_SCENARIO_PREFIX_RULES,
  type BillingPrefixRule,
  type BillingScenarioMappingRow,
} from "../../data/billingRulesSeed";

export type ScenarioMappingTableRow =
  | {
      rowKey: string;
      source: "auto";
      scenarioPattern: string;
      capabilitySkuId: string;
    }
  | {
      rowKey: string;
      source: "custom";
      scenarioId: string;
      capabilitySkuId: string;
    };

function formatRulePattern(rule: BillingPrefixRule): string {
  if (rule.kind === "prefix") {
    return rule.prefixes.map((p) => `${p}*`).join("、");
  }
  return `含「${rule.contains}」`;
}

/** 自动规则置顶，其后为可编辑的精确场景映射 */
export function buildScenarioMappingTableRows(
  custom: BillingScenarioMappingRow[],
): ScenarioMappingTableRow[] {
  const autoRows: ScenarioMappingTableRow[] = BILLING_SCENARIO_PREFIX_RULES.map((rule) => ({
    rowKey: `auto:${rule.key}`,
    source: "auto",
    scenarioPattern: formatRulePattern(rule),
    capabilitySkuId: rule.capabilitySkuId,
  }));

  const customRows: ScenarioMappingTableRow[] = [...custom]
    .sort((a, b) => a.scenarioId.localeCompare(b.scenarioId))
    .map((row) => ({
      rowKey: row.scenarioId,
      source: "custom",
      scenarioId: row.scenarioId,
      capabilitySkuId: row.capabilitySkuId,
    }));

  return [...autoRows, ...customRows];
}
