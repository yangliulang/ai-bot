// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: Admin 人工确认规则 CRUD · 启用 · 重置（FE_HANDOFF · ai.confirmation-rules）

import { HTTPError } from 'ky'

import type {
  ConfirmationRuleWriteBody,
  RiskLevel,
  RuleAction,
  ScenarioKey,
  TriggerConditionRow,
  TriggerFieldKey,
  TriggerOpKey,
} from '@/entities/confirmation-rules/confirmation-rules-catalog'
import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/admin/confirmation-rules'

export const AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY =
  'AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY'
export const AGENT_ADMIN_CONFIRMATION_RULE_NOT_FOUND = 'AGENT_ADMIN_CONFIRMATION_RULE_NOT_FOUND'

export interface ConfirmationRuleItem {
  id: string
  title: string
  summary: string
  riskLevel: RiskLevel
  triggerConditions: TriggerConditionRow[]
  scenarios: ScenarioKey[]
  action: RuleAction
  defaultEnabled: boolean
  enabled: boolean
  isBuiltin: boolean
  updatedAt?: string | null
}

export interface ConfirmationRuleListResponse {
  items: ConfirmationRuleItem[]
  total: number
  enabledCount: number
}

export type ConfirmationRuleCreateBody = ConfirmationRuleWriteBody

export type ConfirmationRuleUpdateBody = ConfirmationRuleWriteBody

async function normalizeKyError(error: unknown): Promise<never> {
  if (error instanceof HTTPError) {
    const cloned = error.response.clone()
    const body: unknown = await cloned.json().catch(() => null)
    if (body !== null && typeof body === 'object') {
      const msg =
        'message' in body && typeof (body as { message: unknown }).message === 'string'
          ? (body as { message: string }).message
          : 'detail' in body && typeof (body as { detail: unknown }).detail === 'string'
            ? (body as { detail: string }).detail
            : undefined
      if (msg) {
        const code =
          'code' in body && typeof (body as { code: unknown }).code === 'string'
            ? (body as { code: string }).code
            : undefined
        throw new AppError(msg, {
          status: error.response.status,
          code,
        })
      }
    }
  }
  throw await toAppError(error)
}

export function explainConfirmationRuleError(e: unknown): string {
  if (e instanceof AppError) {
    if (e.code === AGENT_ADMIN_CONFIRMATION_RULE_BUILTIN_READONLY) {
      return '内置规则不可编辑或删除，仅可切换启用状态。'
    }
    if (e.code === AGENT_ADMIN_CONFIRMATION_RULE_NOT_FOUND) {
      return '未找到该规则，可能已被删除。'
    }
    return e.message
  }
  return '操作失败，请稍后重试。'
}

export async function listConfirmationRules(): Promise<ConfirmationRuleListResponse> {
  try {
    return await httpClient.get(PREFIX).json<ConfirmationRuleListResponse>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function getConfirmationRule(ruleId: string): Promise<ConfirmationRuleItem> {
  try {
    return await httpClient.get(`${PREFIX}/${encodeURIComponent(ruleId)}`).json<ConfirmationRuleItem>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function createConfirmationRule(
  body: ConfirmationRuleCreateBody,
): Promise<ConfirmationRuleItem> {
  try {
    return await httpClient.post(PREFIX, { json: body }).json<ConfirmationRuleItem>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function updateConfirmationRule(
  ruleId: string,
  body: ConfirmationRuleUpdateBody,
): Promise<ConfirmationRuleItem> {
  try {
    return await httpClient
      .put(`${PREFIX}/${encodeURIComponent(ruleId)}`, { json: body })
      .json<ConfirmationRuleItem>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function deleteConfirmationRule(ruleId: string): Promise<void> {
  try {
    await httpClient.delete(`${PREFIX}/${encodeURIComponent(ruleId)}`)
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function patchConfirmationRuleEnabled(
  ruleId: string,
  enabled: boolean,
): Promise<ConfirmationRuleItem> {
  try {
    return await httpClient
      .patch(`${PREFIX}/${encodeURIComponent(ruleId)}/enabled`, { json: { enabled } })
      .json<ConfirmationRuleItem>()
  } catch (e) {
    return normalizeKyError(e)
  }
}

export async function resetConfirmationRules(): Promise<ConfirmationRuleListResponse> {
  try {
    return await httpClient.post(`${PREFIX}/reset`).json<ConfirmationRuleListResponse>()
  } catch (e) {
    return normalizeKyError(e)
  }
}
