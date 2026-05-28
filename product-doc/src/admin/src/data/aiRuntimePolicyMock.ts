/**
 * Agent Runtime 模型策略 — 表单默认值与分场景字段（运营语义）。
 * 下拉选项由页面根据「厂商与模型」台账动态生成：仅已启用厂商、且模型启用且未弃用（见 `buildRuntimeModelSelectOptions`）。
 */

/** 推理分层 */
export const SCENARIO_MODEL_FIELDS = [
  { rowKey: "chat", field: "scenarioChatModel" as const, label: "普通问答" },
  { rowKey: "trading", field: "scenarioTradingModel" as const, label: "交易执行" },
  { rowKey: "risk", field: "scenarioRiskModel" as const, label: "风险判断" },
];

export const AI_RUNTIME_POLICY_INITIAL = {
  defaultInferenceModel: "gpt-4.1",
  scenarioChatModel: "gpt-4.1-mini",
  scenarioTradingModel: "gpt-4.1",
  scenarioRiskModel: "gpt-4.1",
  maxContextTokens: 128000,
  maxOutputTokens: 4096,
  timeoutSec: 120,
  fallbackOnPrimaryFailure: true,
  fallbackOnTimeout: true,
  downgradePeakTraffic: false,
  fallbackModel: "gpt-4.1-mini",
  maxTokensPerRequest: 32000,
  dailyTokenBudgetM: 50,
  rateLimitRpm: 600,
};
