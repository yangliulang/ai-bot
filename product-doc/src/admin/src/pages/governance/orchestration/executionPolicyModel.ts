/**
 * 执行策略状态：上层为运营可读的治理字段；`engineering*` 为 Runtime 契约镜像，仅应在「开发信息」中展示。
 * 演示持久化见 OrchestrationPolicyContext（sessionStorage）。
 */

export type FailureStopPolicy = "stop_notify" | "stop_silent" | "escalate_manual";

/** Runtime / OpenAPI 侧工程字段（勿作为主表单的运营价值主张） */
export interface ExecutionPolicyEngineeringFields {
  maxToolCalls: number;
  maxOrchestrationSteps: number;
  maxModelRounds: number;
  modelRoundsLimitEnabled: boolean;
  budgetExceededStableCode: string;
  cClassPoolNote: string;
  retrySummary: string;
  unknownHandlingSummary: string;
}

export interface ExecutionPolicyState extends ExecutionPolicyEngineeringFields {
  /** --- 自动执行 --- */
  autoExecutionAllowed: boolean;
  /** 高风险写场景禁止自动落单 */
  blockAutoHighRiskWrite: boolean;
  /** 查询类默认允许自动执行 */
  queryAutoDefault: boolean;

  /** --- 确认 --- */
  confirmationRequiredForWrites: boolean;
  secondConfirmLargeNotional: boolean;
  highLeverageConfirm: boolean;

  /** --- 风险限制 --- */
  maxNotionalUsdt: number;
  maxLeverage: number;
  maxDailyWriteOperations: number;
  rateLimitNote: string;

  /** --- 执行稳定性 --- */
  maxRetries: number;
  executionTimeoutSeconds: number;
  failureStopPolicy: FailureStopPolicy;
}

export const DEFAULT_EXECUTION_POLICY: ExecutionPolicyState = {
  autoExecutionAllowed: true,
  blockAutoHighRiskWrite: true,
  queryAutoDefault: true,
  confirmationRequiredForWrites: true,
  secondConfirmLargeNotional: true,
  highLeverageConfirm: true,
  maxNotionalUsdt: 50_000,
  maxLeverage: 20,
  maxDailyWriteOperations: 200,
  rateLimitNote: "同一用户 10 秒内同类写请求合并提示（演示）",
  maxRetries: 3,
  executionTimeoutSeconds: 120,
  failureStopPolicy: "stop_notify",

  maxToolCalls: 64,
  maxOrchestrationSteps: 48,
  maxModelRounds: 16,
  modelRoundsLimitEnabled: true,
  budgetExceededStableCode: "ORCHESTRATION_BUDGET_EXCEEDED",
  cClassPoolNote: "与 ADR-003 外网步预算叠加时以更严或 design 优先级为准（execution-lifecycle §4.1）",
  retrySummary: "retry-policy：重试不得跳过确认门 / read_skill（SC-AO-06）",
  unknownHandlingSummary: "UNKNOWN / 504 路径：查单对账 + Runtime reconciliation；禁止写类无脑同参自动重试（runtime-contract）",
};

export const FAILURE_STOP_POLICY_LABEL: Record<FailureStopPolicy, string> = {
  stop_notify: "失败即停并通知用户",
  stop_silent: "失败即停（仅日志）",
  escalate_manual: "失败转人工待办",
};

/** 开发信息区展示的规格引用（只读） */
export const ENGINEERING_SPEC_REFS: string[] = [
  "domains/agent/agent-orchestration/execution-lifecycle.md §4 · FR-AO06",
  "domains/agent/agent-orchestration/retry-policy.md",
  "domains/admin/tool-management/runtime-contract.md §3",
  "design/api.md · 编排执行预算 / FR-MC408",
];
