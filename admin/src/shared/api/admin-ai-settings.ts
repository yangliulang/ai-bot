// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: AiGatewayDefaults — intentNluUseLlm、telegramLlmNarrate（网关策略 UI）
// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能：GET/PATCH/DELETE 模型改用 Query `modelId`（catalog id 含 `/` 时避免 path `%2F` 经代理 404）
// 作者: 杨永的Agent
// 日期: 2026-05-19
// 修改功能: apiModel 字段、PATCH defaults 422 AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG 解析（FE_HANDOFF 2026-05-19）
// 作者: 杨永的Agent
// 日期: 2026-05-13
// 修改功能: Admin AI Settings — DELETE Provider；模型 CRUD（FE_HANDOFF）

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/admin/ai'

/** `PATCH …/defaults`：策略字段引用的 catalog `modelId` 未登记 */
export const AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG = 'AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG'

export interface GatewayModelCatalogMissingEntry {
  field: string
  modelId: string
}

const GATEWAY_MODEL_FIELD_LABELS: Record<string, string> = {
  defaultModelId: '默认模型',
  defaultInferenceModel: '默认推理模型',
  scenarioChatModel: '普通问答',
  scenarioTradingModel: '交易执行',
  scenarioRiskModel: '风险判断',
  fallbackModel: '降级模型',
}

export function formatGatewayModelCatalogError(
  message: string,
  details?: Record<string, unknown> | null,
): string {
  const raw = details?.missing
  if (!Array.isArray(raw) || raw.length === 0) return message
  const parts: string[] = []
  for (const item of raw) {
    if (!item || typeof item !== 'object') continue
    const field = 'field' in item && typeof item.field === 'string' ? item.field : ''
    const modelId = 'modelId' in item && typeof item.modelId === 'string' ? item.modelId : ''
    if (!field || !modelId) continue
    const label = GATEWAY_MODEL_FIELD_LABELS[field] ?? field
    parts.push(`${label} → ${modelId}`)
  }
  return parts.length ? `${message}：${parts.join('；')}` : message
}

export interface LlmProviderSummary {
  providerId: string
  displayName: string
  baseUrl: string
  secretRef: string | null
  configured: boolean
}

export interface LlmProviderListResponse {
  items: LlmProviderSummary[]
}

export interface LlmProviderCreateBody {
  displayName: string
  baseUrl: string
  secretRef?: string | null
}

export interface LlmModelSummary {
  modelId: string
  providerId: string
  status: string
  contextWindowTokens: number | null
  /** 对端 HTTP JSON `model`；留空则运行时等价于 modelId */
  apiModel?: string | null
}

export interface LlmModelListResponse {
  items: LlmModelSummary[]
}

export interface LlmModelPatchBody {
  providerId?: string
  status?: string
  contextWindowTokens?: number | null
  apiModel?: string | null
}

export interface LlmModelCreateBody {
  providerId: string
  modelId: string
  status?: string
  contextWindowTokens?: number | null
  apiModel?: string | null
}

export interface OrchestrationExecutionBudget {
  maxToolCallsPerExecution: number
  maxOrchestrationStepsPerExecution: number
  maxModelTurnsPerExecution: number | null
}

/** Telegram 场景 LLM narrate 开关（9 字段，与后端 camelCase 一致） */
export interface TelegramLlmNarrateFlags {
  readMarketTicker: boolean
  readMarketDepth: boolean
  readMarketTrades: boolean
  readAccountBalance: boolean
  wealthHoldingsRead: boolean
  spotFlashConfirm: boolean
  spotLimitConfirm: boolean
  futuresMarketConfirm: boolean
  futuresLimitConfirm: boolean
}

/** 网关默认（merged）；含原型 Runtime 策略字段与 OpenAPI 骨架字段 */
export type AiGatewayDefaults = {
  defaultProviderId?: string
  defaultModelId?: string
  orchestrationExecutionBudget?: OrchestrationExecutionBudget
  defaultInferenceModel?: string
  scenarioChatModel?: string
  scenarioTradingModel?: string
  scenarioRiskModel?: string
  maxContextTokens?: number
  maxOutputTokens?: number
  timeoutSec?: number
  fallbackOnPrimaryFailure?: boolean
  fallbackOnTimeout?: boolean
  downgradePeakTraffic?: boolean
  fallbackModel?: string
  maxTokensPerRequest?: number
  dailyTokenBudgetM?: number
  rateLimitRpm?: number
  intentNluUseLlm?: boolean
  intentClarifyUseLlm?: boolean
  telegramLlmNarrate?: Partial<TelegramLlmNarrateFlags>
} & Record<string, unknown>

export interface AiHealthProbeResult {
  ok: boolean
  latencyMs: number
  checkedAt: string
  message?: string | null
}

function throwFromErrorBody(body: unknown, status: number): never {
  if (body === null || typeof body !== 'object') {
    throw new AppError('请求失败', { status })
  }
  const code =
    'code' in body && typeof (body as { code: unknown }).code === 'string'
      ? (body as { code: string }).code
      : undefined
  const details =
    'details' in body &&
    (body as { details: unknown }).details !== null &&
    typeof (body as { details: unknown }).details === 'object'
      ? ((body as { details: Record<string, unknown> }).details ?? undefined)
      : undefined
  let message: string | undefined
  if ('message' in body && typeof (body as { message: unknown }).message === 'string') {
    message = (body as { message: string }).message
  } else if ('detail' in body && typeof (body as { detail: unknown }).detail === 'string') {
    message = (body as { detail: string }).detail
  }
  if (!message) {
    throw new AppError('请求失败', { status, code, details })
  }
  const display =
    code === AGENT_AI_GATEWAY_MODEL_NOT_IN_CATALOG
      ? formatGatewayModelCatalogError(message, details ?? null)
      : message
  throw new AppError(display, { status, code, details })
}

async function normalizeKyError(error: unknown): Promise<never> {
  if (error instanceof HTTPError) {
    const cloned = error.response.clone()
    const body: unknown = await cloned.json().catch(() => null)
    if (body !== null && typeof body === 'object') {
      throwFromErrorBody(body, error.response.status)
    }
  }
  throw await toAppError(error)
}

export async function listAiProviders(): Promise<LlmProviderListResponse> {
  try {
    return await httpClient.get(`${PREFIX}/providers`).json<LlmProviderListResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function patchAiProvider(
  providerId: string,
  body: Partial<LlmProviderCreateBody>,
): Promise<LlmProviderSummary> {
  const id = providerId.trim()
  if (!id) throw new AppError('providerId 不可为空', { status: 400 })
  try {
    return await httpClient
      .patch(`${PREFIX}/providers/${encodeURIComponent(id)}`, {
        json: {
          ...(body.displayName !== undefined ? { displayName: body.displayName } : {}),
          ...(body.baseUrl !== undefined ? { baseUrl: body.baseUrl } : {}),
          ...(body.secretRef !== undefined ? { secretRef: body.secretRef } : {}),
        },
      })
      .json<LlmProviderSummary>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function createAiProvider(body: LlmProviderCreateBody): Promise<LlmProviderSummary> {
  try {
    return await httpClient
      .post(`${PREFIX}/providers`, {
        json: {
          displayName: body.displayName,
          baseUrl: body.baseUrl,
          ...(body.secretRef !== undefined ? { secretRef: body.secretRef } : {}),
        },
      })
      .json<LlmProviderSummary>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function deleteAiProvider(providerId: string, ifMatch?: string): Promise<void> {
  const id = providerId.trim()
  if (!id) throw new AppError('providerId 不可为空', { status: 400 })
  try {
    const headers: Record<string, string> = {}
    const v = ifMatch?.trim()
    if (v) headers['If-Match'] = v.startsWith('"') ? v : `"${v}"`
    await httpClient.delete(`${PREFIX}/providers/${encodeURIComponent(id)}`, {
      headers: Object.keys(headers).length ? headers : undefined,
    })
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function listAiModels(providerId?: string): Promise<LlmModelListResponse> {
  try {
    const searchParams: Record<string, string> = {}
    const p = providerId?.trim()
    if (p) searchParams.providerId = p
    return await httpClient.get(`${PREFIX}/models`, { searchParams }).json<LlmModelListResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAiModel(modelId: string): Promise<LlmModelSummary> {
  const id = modelId.trim()
  if (!id) throw new AppError('modelId 不可为空', { status: 400 })
  try {
    // Query modelId：`model_id` 含 `/` 时 path 段的 `%2F` 易被反向代理误判；与 BACKEND_SPEC 约定一致。
    const res = await httpClient.get(`${PREFIX}/models`, { searchParams: { modelId: id } }).json<LlmModelListResponse>()
    const row = res.items[0]
    if (!row) throw new AppError('未找到该模型', { status: 404, code: 'AGENT_AI_MODEL_NOT_FOUND' })
    return row
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function createAiModel(body: LlmModelCreateBody): Promise<LlmModelSummary> {
  const pid = body.providerId.trim()
  const mid = body.modelId.trim()
  if (!pid || !mid) throw new AppError('providerId 与 modelId 必填', { status: 400 })
  try {
    const res = await httpClient.post(`${PREFIX}/models`, {
      json: {
        providerId: pid,
        modelId: mid,
        ...(body.status !== undefined ? { status: body.status } : {}),
        ...(body.contextWindowTokens !== undefined
          ? { contextWindowTokens: body.contextWindowTokens }
          : {}),
        ...(body.apiModel !== undefined ? { apiModel: body.apiModel } : {}),
      },
    })
    return await res.json<LlmModelSummary>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function patchAiModel(
  modelId: string,
  body: LlmModelPatchBody,
  ifMatch?: string,
): Promise<LlmModelSummary> {
  const id = modelId.trim()
  if (!id) throw new AppError('modelId 不可为空', { status: 400 })
  try {
    const headers: Record<string, string> = {}
    const v = ifMatch?.trim()
    if (v) headers['If-Match'] = v.startsWith('"') ? v : `"${v}"`
    const json: Record<string, unknown> = {}
    if (body.providerId !== undefined) json.providerId = body.providerId
    if (body.status !== undefined) json.status = body.status
    if (body.contextWindowTokens !== undefined) json.contextWindowTokens = body.contextWindowTokens
    if (body.apiModel !== undefined) json.apiModel = body.apiModel
    return await httpClient
      .patch(`${PREFIX}/models`, {
        json,
        searchParams: { modelId: id },
        headers: Object.keys(headers).length ? headers : undefined,
      })
      .json<LlmModelSummary>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function deleteAiModel(modelId: string, ifMatch?: string): Promise<void> {
  const id = modelId.trim()
  if (!id) throw new AppError('modelId 不可为空', { status: 400 })
  try {
    const headers: Record<string, string> = {}
    const v = ifMatch?.trim()
    if (v) headers['If-Match'] = v.startsWith('"') ? v : `"${v}"`
    await httpClient.delete(`${PREFIX}/models`, {
      searchParams: { modelId: id },
      headers: Object.keys(headers).length ? headers : undefined,
    })
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAiGatewayDefaults(): Promise<AiGatewayDefaults> {
  try {
    return await httpClient.get(`${PREFIX}/defaults`).json<AiGatewayDefaults>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function patchAiGatewayDefaults(
  body: Record<string, unknown>,
  ifMatch?: string,
): Promise<AiGatewayDefaults> {
  try {
    const headers: Record<string, string> = {}
    const v = ifMatch?.trim()
    if (v) headers['If-Match'] = v.startsWith('"') ? v : `"${v}"`
    return await httpClient
      .patch(`${PREFIX}/defaults`, { json: body, headers: Object.keys(headers).length ? headers : undefined })
      .json<AiGatewayDefaults>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function probeAiProviderHealth(providerId: string): Promise<AiHealthProbeResult> {
  const id = providerId.trim()
  if (!id) throw new AppError('providerId 不可为空', { status: 400 })
  try {
    return await httpClient
      .post(`${PREFIX}/providers/${encodeURIComponent(id)}/health`)
      .json<AiHealthProbeResult>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
