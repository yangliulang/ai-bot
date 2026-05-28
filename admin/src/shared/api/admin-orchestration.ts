// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: **GET /api/v1/admin/orchestration/policy** 执行策略读模型（FE_HANDOFF · Phase2 运行编排）

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/admin/orchestration'

export type OrchestrationFailureStopPolicy = 'stop_notify' | 'stop_silent' | 'escalate_manual'

/** 对齐后端 `OrchestrationExecutionPolicyOut` */
export interface OrchestrationExecutionPolicy {
  orchestrationRegistryVersion: string
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
  failureStopPolicy: OrchestrationFailureStopPolicy
  maxToolCalls: number
  maxOrchestrationSteps: number
  maxModelRounds: number
  modelRoundsLimitEnabled: boolean
  budgetExceededStableCode: string
  cClassPoolNote: string
  retrySummary: string
  unknownHandlingSummary: string
  engineeringSpecRefs: string[]
}

async function normalizeKyError(error: unknown): Promise<never> {
  if (error instanceof HTTPError) {
    const cloned = error.response.clone()
    const body: unknown = await cloned.json().catch(() => null)
    if (
      body !== null &&
      typeof body === 'object' &&
      'message' in body &&
      typeof (body as { message: unknown }).message === 'string'
    ) {
      const code =
        'code' in body && typeof (body as { code: unknown }).code === 'string'
          ? (body as { code: string }).code
          : undefined
      throw new AppError((body as { message: string }).message, {
        status: error.response.status,
        code,
      })
    }
  }
  throw await toAppError(error)
}

export async function getOrchestrationPolicy(): Promise<OrchestrationExecutionPolicy> {
  try {
    return await httpClient.get(`${PREFIX}/policy`).json<OrchestrationExecutionPolicy>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
