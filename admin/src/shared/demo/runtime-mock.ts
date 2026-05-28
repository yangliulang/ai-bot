import {
  ExecutionRowSchema,
  ObsBillingRowSchema,
  ObsLlmRowSchema,
  ObsToolRowSchema,
  RuntimeEventRowSchema,
  RuntimeTaskRowSchema,
  type ExecutionRow,
  type ObsBillingRow,
  type ObsLlmRow,
  type ObsToolRow,
  type RuntimeEventRow,
  type RuntimeTaskRow,
} from '@/entities/runtime/execution.schema'

import { ORCHESTRATION_VERSION_DISPLAY } from '@/entities/orchestration/scenario-registry'

const RAW_EXECUTIONS = [
  {
    executionId: 'exec-aa11',
    sessionId: 'sess-aa11',
    userIdMasked: 'u-10482',
    scenarioId: 'trade.spot.limit_order',
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: '现货 · 限价下单',
    status: 'COMPLETED',
    currentStage: 'COMPLETED',
    retries: 0,
    createdAt: '2026-05-07T01:17:50Z',
    stageTimeline: ['CREATED', 'CONFIRM_PENDING', 'RUNNING', 'COMPLETED'],
    durationMs: 8420,
    startedAt: '2026-05-07T01:17:50Z',
    outcome: 'PER_EXECUTION_FINAL',
  },
  {
    executionId: 'exec-bb22',
    sessionId: 'sess-bb22',
    userIdMasked: 'u-88301',
    scenarioId: 'trade.spot.limit_order',
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: '现货 · 限价下单',
    status: 'BLOCKED',
    currentStage: 'BILLING_GATE',
    retries: 1,
    createdAt: '2026-05-06T18:40:55Z',
    stageTimeline: ['CREATED', 'RUNNING', 'BLOCKED'],
    durationMs: 2100,
    startedAt: '2026-05-06T18:40:55Z',
    outcome: 'BILLING_BLOCKED',
  },
  {
    executionId: 'exec-un99',
    sessionId: 'sess-un99',
    userIdMasked: 'u-10482',
    scenarioId: 'trade.spot.flash_convert',
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: '现货 · 闪兑演练 / 对账不确定性',
    status: 'UNKNOWN',
    currentStage: 'RECONCILING',
    retries: 2,
    createdAt: '2026-05-07T02:05:12Z',
    stageTimeline: ['CREATED', 'RUNNING', 'UNKNOWN', 'RECOVERING'],
    durationMs: 0,
    startedAt: '2026-05-07T02:05:12Z',
    outcome: 'UNKNOWN',
  },
  {
    executionId: 'exec-fail01',
    sessionId: 'sess-fail01',
    userIdMasked: 'u-22001',
    scenarioId: 'trade.futures.market_order',
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: '合约 · 市价单失败',
    status: 'FAILED',
    currentStage: 'TOOL_FAILED',
    retries: 1,
    createdAt: '2026-05-07T00:30:00Z',
    stageTimeline: ['CREATED', 'RUNNING', 'FAILED'],
    durationMs: 800,
    startedAt: '2026-05-07T00:30:00Z',
    outcome: 'FAILED',
  },
  {
    executionId: 'exec-run01',
    sessionId: 'sess-run01',
    userIdMasked: 'u-10482',
    scenarioId: 'trade.spot.limit_order',
    orchestrationVersion: ORCHESTRATION_VERSION_DISPLAY,
    intent: '现货 · 限价进行中',
    status: 'RUNNING',
    currentStage: 'RUNNING',
    retries: 0,
    createdAt: '2026-05-07T02:10:00Z',
    stageTimeline: ['CREATED', 'CONFIRM_PENDING', 'RUNNING'],
    durationMs: 0,
    startedAt: '2026-05-07T02:10:00Z',
    outcome: 'RUNNING',
  },
] as const

export const demoObsExecutions: ExecutionRow[] = RAW_EXECUTIONS.map((r) =>
  ExecutionRowSchema.parse(r),
)

const RAW_TASKS = [
  { taskId: 'task-001', executionId: 'exec-aa11', state: 'PENDING', scheduledAt: '2026-05-07T01:17:50Z' },
  { taskId: 'task-002', executionId: 'exec-un99', state: 'BLOCKED', scheduledAt: '2026-05-07T02:05:14Z' },
  { taskId: 'task-003', executionId: 'exec-bb22', state: 'PENDING', scheduledAt: '2026-05-06T18:41:12Z' },
  { taskId: 'task-004', executionId: 'exec-run01', state: 'RUNNING', scheduledAt: '2026-05-07T02:10:05Z' },
  { taskId: 'task-005', executionId: 'exec-fail01', state: 'PENDING', scheduledAt: '2026-05-07T00:30:02Z' },
] as const

const demoRuntimeTasks: RuntimeTaskRow[] = RAW_TASKS.map((r) => RuntimeTaskRowSchema.parse(r))

const RAW_EVENTS = [
  { executionId: 'exec-aa11', at: '2026-05-07T01:17:50Z', eventType: 'execution.created', summary: 'CREATED' },
  {
    executionId: 'exec-aa11',
    at: '2026-05-07T01:17:55Z',
    eventType: 'confirm.pending',
    summary: 'CONFIRM_PENDING',
  },
  {
    executionId: 'exec-aa11',
    at: '2026-05-07T01:17:58Z',
    eventType: 'tool.started',
    summary: 'tool.exchange.account.balance',
  },
  {
    executionId: 'exec-aa11',
    at: '2026-05-07T01:18:05Z',
    eventType: 'tool.started',
    summary: 'tool.exchange.spot.order',
  },
  {
    executionId: 'exec-aa11',
    at: '2026-05-07T01:18:22Z',
    eventType: 'reconciliation.completed',
    summary: 'billing settled',
  },
  { executionId: 'exec-bb22', at: '2026-05-06T18:40:55Z', eventType: 'execution.created', summary: 'CREATED' },
  {
    executionId: 'exec-bb22',
    at: '2026-05-06T18:41:00Z',
    eventType: 'tool.succeeded',
    summary: 'tool.exchange.account.balance',
  },
  {
    executionId: 'exec-bb22',
    at: '2026-05-06T18:41:04Z',
    eventType: 'billing.preflight.failed',
    summary: 'INSUFFICIENT_BALANCE',
  },
  { executionId: 'exec-run01', at: '2026-05-07T02:10:00Z', eventType: 'execution.created', summary: 'CREATED' },
  { executionId: 'exec-run01', at: '2026-05-07T02:10:03Z', eventType: 'llm.completed', summary: 'planner round 1' },
  { executionId: 'exec-run01', at: '2026-05-07T02:10:08Z', eventType: 'order.pending', summary: 'partial fill · awaiting' },
  { executionId: 'exec-un99', at: '2026-05-07T02:05:12Z', eventType: 'execution.created', summary: 'CREATED' },
  { executionId: 'exec-un99', at: '2026-05-07T02:05:13Z', eventType: 'retry.started', summary: 'attempt 2' },
  { executionId: 'exec-un99', at: '2026-05-07T02:05:14Z', eventType: 'tool.failed', summary: 'reconciliation timeout' },
  { executionId: 'exec-fail01', at: '2026-05-07T00:30:00Z', eventType: 'execution.created', summary: 'CREATED' },
  { executionId: 'exec-fail01', at: '2026-05-07T00:30:01Z', eventType: 'tool.failed', summary: 'market depth insufficient' },
] as const

const demoRuntimeEvents: RuntimeEventRow[] = RAW_EVENTS.map((r) => RuntimeEventRowSchema.parse(r))

const RAW_TOOLS = [
  {
    executionId: 'exec-aa11',
    toolId: 'tool.exchange.spot.order',
    toolCallSeq: 1,
    invocationState: 'SUCCEEDED',
    pathSummary: 'POST /sapi/v1/agent/order · 201',
    at: '2026-05-07T01:18:05Z',
  },
  {
    executionId: 'exec-aa11',
    toolId: 'tool.exchange.account.balance',
    toolCallSeq: 0,
    invocationState: 'SUCCEEDED',
    pathSummary: 'GET /sapi/v1/agent/balance · 200',
    at: '2026-05-07T01:17:58Z',
  },
  {
    executionId: 'exec-bb22',
    toolId: 'tool.exchange.account.balance',
    toolCallSeq: 0,
    invocationState: 'SUCCEEDED',
    pathSummary: 'GET /sapi/v1/agent/balance · 200',
    at: '2026-05-06T18:41:00Z',
  },
  {
    executionId: 'exec-bb22',
    toolId: 'tool.billing.preflight',
    toolCallSeq: 1,
    invocationState: 'SUCCEEDED',
    pathSummary: 'POST /internal/billing/preflight · 402 simulate insufficient',
    at: '2026-05-06T18:41:03Z',
  },
  {
    executionId: 'exec-un99',
    toolId: 'tool.reconcile.execution',
    toolCallSeq: 0,
    invocationState: 'FAILED',
    pathSummary: 'POST /internal/reconcile · 504 gateway timeout',
    at: '2026-05-07T02:05:14Z',
  },
  {
    executionId: 'exec-fail01',
    toolId: 'tool.exchange.spot.market',
    toolCallSeq: 0,
    invocationState: 'FAILED',
    pathSummary: 'POST /sapi/v1/agent/order/market · depth insufficient',
    at: '2026-05-07T00:30:01Z',
  },
  {
    executionId: 'exec-run01',
    toolId: 'tool.llm.router.plan',
    toolCallSeq: 0,
    invocationState: 'SUCCEEDED',
    pathSummary: `orchestration · scenario trade.spot.limit_order`,
    at: '2026-05-07T02:10:02Z',
  },
  {
    executionId: 'exec-run01',
    toolId: 'tool.exchange.spot.order',
    toolCallSeq: 1,
    invocationState: 'SUCCEEDED',
    pathSummary: 'POST /sapi/v1/agent/order · 202 pending fill',
    at: '2026-05-07T02:10:08Z',
  },
] as const

const demoObsTools: ObsToolRow[] = RAW_TOOLS.map((r) => ObsToolRowSchema.parse(r))

const RAW_LLMS = [
  {
    executionId: 'exec-aa11',
    modelId: 'gpt-4.1-mini',
    inputTokens: 1204,
    outputTokens: 356,
    at: '2026-05-07T01:18:10Z',
  },
  {
    executionId: 'exec-bb22',
    modelId: 'gpt-4.1-mini',
    inputTokens: 980,
    outputTokens: 240,
    at: '2026-05-06T18:40:58Z',
  },
  {
    executionId: 'exec-un99',
    modelId: 'gpt-4.1-mini',
    inputTokens: 612,
    outputTokens: 128,
    at: '2026-05-07T02:05:13Z',
  },
  {
    executionId: 'exec-fail01',
    modelId: 'gpt-4.1-mini',
    inputTokens: 410,
    outputTokens: 96,
    at: '2026-05-07T00:30:00Z',
  },
  {
    executionId: 'exec-run01',
    modelId: 'gpt-4.1',
    inputTokens: 2104,
    outputTokens: 418,
    at: '2026-05-07T02:10:03Z',
  },
] as const

const demoObsLlms: ObsLlmRow[] = RAW_LLMS.map((r) => ObsLlmRowSchema.parse(r))

const RAW_BILLING = [
  {
    executionId: 'exec-aa11',
    billingTraceId: 'bt-7f2a-001',
    idempotencyKeySuffix: '…idemp-7a2f',
    billCode: 'CHARGE_SUCCESS',
    chargeStatus: 'SETTLED',
    amountUsdt: '0.042',
    at: '2026-05-07T01:18:22Z',
  },
  {
    executionId: 'exec-bb22',
    billingTraceId: 'bt-883-fail',
    idempotencyKeySuffix: '…idemp-883',
    billCode: 'INSUFFICIENT_BALANCE',
    chargeStatus: 'REJECTED',
    amountUsdt: '—',
    at: '2026-05-06T18:41:05Z',
  },
  {
    executionId: 'exec-un99',
    billingTraceId: 'bt-recon-pending-9',
    idempotencyKeySuffix: '…idemp-un99',
    billCode: 'CHARGE_HELD',
    chargeStatus: 'PENDING',
    amountUsdt: '0.000',
    at: '2026-05-07T02:05:15Z',
  },
  {
    executionId: 'exec-fail01',
    billingTraceId: 'bt-no-settlement',
    idempotencyKeySuffix: '…idemp-fail01',
    billCode: 'NO_SETTLEMENT_TOOL_FAILED',
    chargeStatus: 'REJECTED',
    amountUsdt: '—',
    at: '2026-05-07T00:30:02Z',
  },
  {
    executionId: 'exec-run01',
    billingTraceId: 'bt-run-pending',
    idempotencyKeySuffix: '…idemp-run',
    billCode: 'CHARGE_PENDING',
    chargeStatus: 'PENDING',
    amountUsdt: '—',
    at: '2026-05-07T02:10:10Z',
  },
] as const

const demoObsBilling: ObsBillingRow[] = RAW_BILLING.map((r) => ObsBillingRowSchema.parse(r))

export function getDemoExecution(id: string): ExecutionRow | undefined {
  return demoObsExecutions.find((r) => r.executionId === id)
}

export function tasksForExecution(id: string): RuntimeTaskRow[] {
  return demoRuntimeTasks.filter((t) => t.executionId === id)
}

export function eventsForExecution(id: string): RuntimeEventRow[] {
  return demoRuntimeEvents
    .filter((e) => e.executionId === id)
    .slice()
    .sort((a, b) => a.at.localeCompare(b.at))
}

export function toolsForExecution(id: string): ObsToolRow[] {
  return demoObsTools
    .filter((t) => t.executionId === id)
    .slice()
    .sort((a, b) => a.toolCallSeq - b.toolCallSeq)
}

export function llmsForExecution(id: string): ObsLlmRow[] {
  return demoObsLlms.filter((l) => l.executionId === id)
}

export function billingForExecution(id: string): ObsBillingRow[] {
  return demoObsBilling.filter((b) => b.executionId === id)
}
