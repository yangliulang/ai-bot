import { z } from 'zod'

/** 与 admin-console page-specs / OpenAPI 聚合前 Demo 对齐 */
export const ExecutionRowSchema = z.object({
  executionId: z.string(),
  sessionId: z.string(),
  userIdMasked: z.string(),
  scenarioId: z.string(),
  orchestrationVersion: z.string(),
  intent: z.string(),
  status: z.string(),
  currentStage: z.string(),
  retries: z.number(),
  createdAt: z.string(),
  stageTimeline: z.array(z.string()),
  durationMs: z.number(),
  startedAt: z.string(),
  outcome: z.string(),
})

export type ExecutionRow = z.infer<typeof ExecutionRowSchema>

export const RuntimeTaskRowSchema = z.object({
  taskId: z.string(),
  executionId: z.string(),
  state: z.string(),
  scheduledAt: z.string().optional(),
})

export type RuntimeTaskRow = z.infer<typeof RuntimeTaskRowSchema>

export const RuntimeEventRowSchema = z.object({
  executionId: z.string(),
  at: z.string(),
  eventType: z.string(),
  summary: z.string(),
})

export type RuntimeEventRow = z.infer<typeof RuntimeEventRowSchema>

export const ObsToolRowSchema = z.object({
  executionId: z.string(),
  toolId: z.string(),
  toolCallSeq: z.number(),
  invocationState: z.string(),
  pathSummary: z.string(),
  at: z.string(),
})

export type ObsToolRow = z.infer<typeof ObsToolRowSchema>

export const ObsLlmRowSchema = z.object({
  executionId: z.string(),
  modelId: z.string(),
  inputTokens: z.number(),
  outputTokens: z.number(),
  at: z.string(),
})

export type ObsLlmRow = z.infer<typeof ObsLlmRowSchema>

export const ObsBillingRowSchema = z.object({
  executionId: z.string(),
  billingTraceId: z.string(),
  idempotencyKeySuffix: z.string(),
  billCode: z.string(),
  chargeStatus: z.string(),
  amountUsdt: z.string(),
  at: z.string(),
})

export type ObsBillingRow = z.infer<typeof ObsBillingRowSchema>