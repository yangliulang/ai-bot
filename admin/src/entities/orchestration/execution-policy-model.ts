/**
 * 执行策略表单模型（运营字段 + 工程镜像），与 product-doc ExecutionPolicyTab 对齐。
 * 作者: 杨永的Agent
 * 日期: 2026-05-20
 * 修改功能: 自 OrchestrationPolicyTab 抽出，供 API 映射与 Tab 共用
 */

import type { OrchestrationExecutionPolicy } from '@/shared/api/admin-orchestration'

export type FailureStopPolicy = 'stop_notify' | 'stop_silent' | 'escalate_manual'

export interface ExecutionPolicyState {
  autoExecutionAllowed: boolean
  blockAutoHighRiskWrite: boolean
  queryAutoDefault: boolean
  confirmationRequiredForWrites: boolean
  secondConfirmLargeNotional: boolean
  highLeverageConfirm: boolean
  maxNotionalUsdt: number
  maxLeverage: number
  maxDailyWriteOperations: number
  rateLimitNote: string
  maxRetries: number
  executionTimeoutSeconds: number
  failureStopPolicy: FailureStopPolicy
  maxToolCalls: number
  maxOrchestrationSteps: number
  maxModelRounds: number
  modelRoundsLimitEnabled: boolean
  budgetExceededStableCode: string
  cClassPoolNote: string
  retrySummary: string
  unknownHandlingSummary: string
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
  rateLimitNote: '同一用户 10 秒内同类写请求合并提示（演示）',
  maxRetries: 3,
  executionTimeoutSeconds: 120,
  failureStopPolicy: 'stop_notify',
  maxToolCalls: 32,
  maxOrchestrationSteps: 48,
  maxModelRounds: 16,
  modelRoundsLimitEnabled: true,
  budgetExceededStableCode: 'ORCHESTRATION_BUDGET_EXCEEDED',
  cClassPoolNote:
    '与 ADR-003 外网步预算叠加时以更严或 design 优先级为准（execution-lifecycle §4.1）',
  retrySummary: 'retry-policy：重试不得跳过确认门 / read_skill（SC-AO-06）',
  unknownHandlingSummary:
    'UNKNOWN / 504 路径：查单对账 + Runtime reconciliation；禁止写类无脑同参自动重试（runtime-contract）',
}

export const FAILURE_STOP_OPTIONS: { value: FailureStopPolicy; label: string }[] = [
  { value: 'stop_notify', label: '失败即停并通知用户' },
  { value: 'stop_silent', label: '失败即停（仅日志）' },
  { value: 'escalate_manual', label: '失败转人工待办' },
]

export const FALLBACK_ENGINEERING_SPEC_REFS: string[] = [
  'domains/agent/agent-orchestration/execution-lifecycle.md §4 · FR-AO06',
  'domains/agent/agent-orchestration/retry-policy.md',
  'domains/admin/tool-management/runtime-contract.md §3',
  'design/api.md · 编排执行预算 / FR-MC408',
]

export function executionPolicyFromApi(api: OrchestrationExecutionPolicy): ExecutionPolicyState {
  return {
    autoExecutionAllowed: api.autoExecutionAllowed,
    blockAutoHighRiskWrite: api.blockAutoHighRiskWrite,
    queryAutoDefault: api.queryAutoDefault,
    confirmationRequiredForWrites: api.confirmationRequiredForWrites,
    secondConfirmLargeNotional: api.secondConfirmLargeNotional,
    highLeverageConfirm: api.highLeverageConfirm,
    maxNotionalUsdt: api.maxNotionalUsdt,
    maxLeverage: api.maxLeverage,
    maxDailyWriteOperations: api.maxDailyWriteOperations,
    rateLimitNote: api.rateLimitNote,
    maxRetries: api.maxRetries,
    executionTimeoutSeconds: api.executionTimeoutSeconds,
    failureStopPolicy: api.failureStopPolicy,
    maxToolCalls: api.maxToolCalls,
    maxOrchestrationSteps: api.maxOrchestrationSteps,
    maxModelRounds: api.maxModelRounds,
    modelRoundsLimitEnabled: api.modelRoundsLimitEnabled,
    budgetExceededStableCode: api.budgetExceededStableCode,
    cClassPoolNote: api.cClassPoolNote,
    retrySummary: api.retrySummary,
    unknownHandlingSummary: api.unknownHandlingSummary,
  }
}
