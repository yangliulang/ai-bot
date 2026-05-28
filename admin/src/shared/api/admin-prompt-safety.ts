// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: Admin 安全防护聚合读 API（ai.prompt-safety · FE_HANDOFF）

import { HTTPError } from 'ky'

import type { PromptPackListResponse, PromptPackSummary } from '@/shared/api/admin-prompt-packs'
import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/admin/prompt-safety'

export type SafetyInterceptCategory = 'runtime' | 'prompt' | 'tool' | 'session'
export type RuntimeGovernanceHrefKind = 'confirmation' | 'policy' | 'routing'
export type ToolPolicyKind = 'deny' | 'allowlist' | 'shadow'
export type ToolEnforcementMode = 'default_deny' | 'allowlist_only' | 'approve_then_allow'
export type SessionPolicyStatus = 'enabled' | 'warning' | 'info'

export interface SafetyBlocklistRule {
  ruleId: string
  phrase: string
  matchMode: string
}

export interface SafetyBlocklistResponse {
  safetyPhraseBlocklistRevision: string
  safetyPhraseScanScopeDefault: string
  rules: SafetyBlocklistRule[]
}

export interface SafetyOverview {
  safetyPhraseBlocklistRevision: string
  safetyPhraseScanScopeDefault: string
  platformSafetyPack: PromptPackSummary | null
  safetyPromptPackCount: number
  publishedSafetyPackCount: number
  enabledConfirmationRulesCount: number
  globalAgentSwitchOn: boolean
  opsSuspended: boolean
}

export interface RuntimeSafetyGovernanceRow {
  key: string
  name: string
  riskLevelLabel: string
  autoExecSummary: string
  confirmSummary: string
  breakerSummary: string
  hrefKind: RuntimeGovernanceHrefKind
}

export interface RuntimeSafetyGovernanceResponse {
  items: RuntimeSafetyGovernanceRow[]
}

export interface ToolSafetyPolicyRow {
  key: string
  toolPattern: string
  policy: ToolPolicyKind
  enforcementMode: ToolEnforcementMode
  note: string
}

export interface ToolSafetyPolicyResponse {
  items: ToolSafetyPolicyRow[]
}

export interface SessionSafetyPolicyItem {
  key: string
  label: string
  summary: string
  status: SessionPolicyStatus
}

export interface SessionSafetyPolicyResponse {
  items: SessionSafetyPolicyItem[]
}

export interface SafetyInterceptItem {
  id: string
  ts: string
  category: SafetyInterceptCategory
  scenarioLabel: string
  kindLabel: string
  reason: string
  subject: string | null
  executionId: string | null
  matchedRuleId: string | null
}

export interface SafetyInterceptListResponse {
  items: SafetyInterceptItem[]
  total: number
}

export interface ListSafetyInterceptsQuery {
  category?: SafetyInterceptCategory
  limit?: number
  offset?: number
}

async function normalizeKyError(error: unknown): Promise<never> {
  if (error instanceof HTTPError) {
    const cloned = error.response.clone()
    const body: unknown = await cloned.json().catch(() => null)
    if (
      body !== null &&
      typeof body === 'object' &&
      'detail' in body &&
      typeof (body as { detail: unknown }).detail === 'string'
    ) {
      const code =
        'code' in body && typeof (body as { code: unknown }).code === 'string'
          ? (body as { code: string }).code
          : undefined
      throw new AppError((body as { detail: string }).detail, {
        status: error.response.status,
        code,
      })
    }
  }
  throw await toAppError(error)
}

export function explainPromptSafetyError(e: unknown, fallback = '请求失败'): string {
  if (!(e instanceof AppError)) return fallback
  return e.message || fallback
}

export async function getPromptSafetyOverview(): Promise<SafetyOverview> {
  try {
    return await httpClient.get(`${PREFIX}/overview`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getPromptSafetyBlocklist(): Promise<SafetyBlocklistResponse> {
  try {
    return await httpClient.get(`${PREFIX}/blocklist`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function listPromptSafetyPacks(): Promise<PromptPackListResponse> {
  try {
    return await httpClient.get(`${PREFIX}/prompt-packs`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getPromptSafetyRuntimeGovernance(): Promise<RuntimeSafetyGovernanceResponse> {
  try {
    return await httpClient.get(`${PREFIX}/runtime-governance`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getPromptSafetyToolPolicies(): Promise<ToolSafetyPolicyResponse> {
  try {
    return await httpClient.get(`${PREFIX}/tool-policies`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getPromptSafetySessionPolicy(): Promise<SessionSafetyPolicyResponse> {
  try {
    return await httpClient.get(`${PREFIX}/session-policy`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function listPromptSafetyIntercepts(
  query?: ListSafetyInterceptsQuery,
): Promise<SafetyInterceptListResponse> {
  const params = new URLSearchParams()
  if (query?.category) params.set('category', query.category)
  if (query?.limit != null) params.set('limit', String(query.limit))
  if (query?.offset != null) params.set('offset', String(query.offset))
  const qs = params.toString()
  const url = qs ? `${PREFIX}/intercepts?${qs}` : `${PREFIX}/intercepts`
  try {
    return await httpClient.get(url).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
