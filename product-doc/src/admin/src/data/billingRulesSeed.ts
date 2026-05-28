import { DEMO_BILLING_CAPABILITY_MAP } from "../productionRuntime/billingCapabilityMap";

/** 扣减规则种子（与资源 Capability 对齐，不含配额） */
export type BillingDebitRule = {
  capabilitySkuId: string;
  displayLabel: string;
  /** 运营可读：该桶覆盖的业务范围（列表副文案） */
  summary: string;
  debitUnitsPerExecution: number;
};

export const DEBIT_CAPABILITY_TAG_COLOR: Record<string, string> = {
  "cap.agent.analyze": "blue",
  "cap.agent.trade": "gold",
  "cap.agent.monitoring": "cyan",
};

export const DEBIT_RULE_SEED: BillingDebitRule[] = [
  {
    capabilitySkuId: "cap.agent.analyze",
    displayLabel: "AI 分析",
    summary: "只读分析、行情问答、持仓解读等对话类执行",
    debitUnitsPerExecution: 1,
  },
  {
    capabilitySkuId: "cap.agent.trade",
    displayLabel: "自动交易",
    summary: "现货/合约/杠杆下单、改单、理财申购赎回等写路径",
    debitUnitsPerExecution: 1,
  },
  {
    capabilitySkuId: "cap.agent.monitoring",
    displayLabel: "盯盘监控",
    summary: "价格/仓位告警、条件触发与监控类后台任务",
    debitUnitsPerExecution: 1,
  },
];

export function debitCapabilityTagColor(capabilitySkuId: string): string | undefined {
  return DEBIT_CAPABILITY_TAG_COLOR[capabilitySkuId];
}

export function debitCapabilityShortId(capabilitySkuId: string): string {
  const parts = capabilitySkuId.split(".");
  return parts[parts.length - 1] ?? capabilitySkuId;
}

export type BillingScenarioMappingRow = {
  scenarioId: string;
  capabilitySkuId: string;
};

export const SCENARIO_MAPPING_SEED: BillingScenarioMappingRow[] = Object.entries(
  DEMO_BILLING_CAPABILITY_MAP,
).map(([scenarioId, entry]) => ({
  scenarioId,
  capabilitySkuId: entry.capabilitySkuId,
}));

export type BillingPrefixRule =
  | {
      key: string;
      label: string;
      description: string;
      kind: "prefix";
      prefixes: string[];
      capabilitySkuId: string;
    }
  | {
      key: string;
      label: string;
      description: string;
      kind: "contains";
      contains: string;
      capabilitySkuId: string;
    };

/** 显式映射未命中时的前缀 / 兜底规则（Runtime 同窗逻辑） */
export const BILLING_SCENARIO_PREFIX_RULES: BillingPrefixRule[] = [
  {
    key: "analysis-prefix",
    label: "分析类场景",
    description: "scenarioId 以下列前缀开头",
    kind: "prefix",
    prefixes: ["analysis.", "market.query", "qa."],
    capabilitySkuId: "cap.agent.analyze",
  },
  {
    key: "monitor-fallback",
    label: "监控兜底",
    description: "scenarioId 包含关键字",
    kind: "contains",
    contains: "monitor",
    capabilitySkuId: "cap.agent.monitoring",
  },
];

export const BILLING_UNMAPPED_SCENARIO_POLICY =
  "演示环境：未命中任何规则时 Runtime 可能放行；生产须 fail-closed 并告警。";

export const CAPABILITY_OPTIONS = DEBIT_RULE_SEED.map((r) => ({
  value: r.capabilitySkuId,
  label: r.displayLabel,
}));
