// 作者: 杨永的Agent
// 日期: 2026-05-26
// 修改功能: **I02/I04/I05** 写路径 · `createAgentInstance` / `patchAgentInstance` / bind / unbind · **`formatAgentInstanceWriteError`**
// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: **`DELETE …/instances/{instanceId}`**（204）；**`formatAgentInstanceDeleteError`** 展示 **422** **`details`**
// 作者: 杨永的Agent
// 日期: 2026-05-14
// 修改功能: `AgentInstanceRow` 对齐 **`AdminAgentInstanceItem`**（userId · agentState · instanceOverrides · appendix82 等）
// 日期: 2026-05-13
// 修改功能: GET /api/v1/admin/agents/instances 列表与详情（注意 `/agents` 复数，与 trading-bindings `/agent` 单数区分）

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

/** 不含尾斜杠；与 trading-bindings 的 `v1/admin/agent/...` 勿混淆 */
const PATH = 'v1/admin/agents/instances'

export type TradingApiBindingStatus = 'BOUND' | 'NONE'

export interface AgentInstanceRow {
  instanceId: string
  telegramUserId: string
  /** 交易所子账号标识；未接入时可能为空串 */
  exchangeSubAccountUserId: string | null
  templateId: string
  templateVersion: string
  channel: 'telegram'
  tradingApiBindingStatus: TradingApiBindingStatus
  openapiBaseUrl: string | null
  bindingId: number | null
  tgUsername: string | null
  tgLang: string | null
  createdAt: string
  updatedAt: string
  lastActiveAt: string
  /** Phase1：主站 userId，未入库时为空串 */
  userId?: string
  /** 掩码邮箱/账号展示；占位「—」 */
  userEmailMasked?: string
  /** 模板运营展示名；无服务时与 templateId 相同 */
  templateDisplayName?: string
  /** 门禁聚合态（附录 A）；Phase1 默认多为 `OPERATIONAL` */
  agentState?: string
  runtimeState?: string
  subAccountStatus?: 'LINKED' | 'NONE' | 'PENDING'
  lastProductBlockReason?: string
  /** 附录 A §8.2 运营摘要下限（JSON 对象） */
  appendix82?: Record<string, unknown>
  /** 白名单实例参数（不含 Secret） */
  instanceOverrides?: Record<string, unknown>
}

export interface AgentInstanceListResponse {
  items: AgentInstanceRow[]
  total: number
}

/** I05 白名单键（与 OpenAPI / server instance_overrides 一致） */
export type InstanceOverridesPatch = {
  preferredLanguage?: string
  cooldownPreferenceSec?: number
  symbolPreference?: string
  voiceOutputEnabled?: boolean
}

export interface CreateAgentInstanceBody {
  telegramUserId: string
  templateId?: string
  templateVersion?: string
  exchangeSubAccountUserId?: string
}

export interface CreateAgentInstanceResponse {
  instanceId: string
  userId: string
  templateId: string
  runtimeInstanceState: string
  agentSubAccountId?: string | null
}

function adminErrorDetails(body: object): Record<string, unknown> | undefined {
  if (
    'details' in body &&
    body.details !== null &&
    typeof body.details === 'object' &&
    !Array.isArray(body.details)
  ) {
    return body.details as Record<string, unknown>
  }
  return undefined
}

function throwFromAdminErrorBody(body: unknown, status: number): never {
  if (body === null || typeof body !== 'object') {
    throw new AppError('请求失败', { status })
  }
  const code =
    'code' in body && typeof (body as { code: unknown }).code === 'string'
      ? (body as { code: string }).code
      : undefined
  const details = adminErrorDetails(body)
  if (
    'detail' in body &&
    typeof (body as { detail: unknown }).detail === 'string'
  ) {
    throw new AppError((body as { detail: string }).detail, { status, code, details })
  }
  if (
    'message' in body &&
    typeof (body as { message: unknown }).message === 'string'
  ) {
    throw new AppError((body as { message: string }).message, { status, code, details })
  }
  throw new AppError('请求失败', { status, code, details })
}

async function normalizeKyError(error: unknown): Promise<never> {
  if (error instanceof HTTPError) {
    const cloned = error.response.clone()
    const body: unknown = await cloned.json().catch(() => null)
    if (body !== null && typeof body === 'object') {
      throwFromAdminErrorBody(body, error.response.status)
    }
  }
  throw await toAppError(error)
}

/** I02/I04/I05 写操作失败文案（含 **422** `unknownKeys` 等 `details`） */
export function formatAgentInstanceWriteError(e: unknown): string {
  if (!(e instanceof AppError)) return '操作失败'
  const parts: string[] = []
  if (e.code) parts.push(e.code)
  if (e.message) parts.push(e.message)
  const uk = e.details?.unknownKeys
  if (Array.isArray(uk) && uk.length > 0) {
    parts.push(`未知键: ${uk.map((k) => String(k)).join(', ')}`)
  }
  return parts.length ? parts.join(' · ') : '操作失败'
}

/** 实例删除失败文案（含 **422** `AGENT_ADMIN_INSTANCE_DELETE_BLOCKED` 的 `details`） */
export function formatAgentInstanceDeleteError(e: unknown): string {
  if (!(e instanceof AppError)) return '删除失败'
  const parts: string[] = []
  if (e.code) parts.push(e.code)
  if (e.message) parts.push(e.message)
  if (e.code === 'AGENT_ADMIN_INSTANCE_DELETE_BLOCKED' && e.details) {
    const extras: string[] = []
    const open = e.details.openExecutions
    const pending = e.details.pendingConfirmations
    if (typeof open === 'number' && open > 0) extras.push(`未终局执行 ${open} 条`)
    if (typeof pending === 'number' && pending > 0) extras.push(`待确认 ${pending} 条`)
    if (extras.length) parts.push(`（${extras.join('；')}）`)
  }
  return parts.length ? parts.join(' · ') : '删除失败'
}

function clampLimit(n: number): number {
  if (!Number.isFinite(n)) return 50
  return Math.min(200, Math.max(1, Math.floor(n)))
}

export async function listAgentInstances(params?: {
  limit?: number
  offset?: number
  instanceId?: string
  telegramUserId?: string
}): Promise<AgentInstanceListResponse> {
  const searchParams: Record<string, string> = {
    limit: String(clampLimit(params?.limit ?? 50)),
    offset: String(Math.max(0, Math.floor(params?.offset ?? 0))),
  }
  const iid = params?.instanceId?.trim()
  if (iid) searchParams.instanceId = iid
  const tg = params?.telegramUserId?.trim()
  if (tg) searchParams.telegramUserId = tg

  try {
    return await httpClient.get(PATH, { searchParams }).json<AgentInstanceListResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAgentInstance(instanceId: string): Promise<AgentInstanceRow> {
  const id = instanceId.trim()
  if (!id) {
    throw new AppError('instanceId 不可为空', { status: 400 })
  }
  try {
    return await httpClient.get(`${PATH}/${encodeURIComponent(id)}`).json<AgentInstanceRow>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** I02 创建实例 · 成功 **201** */
export async function createAgentInstance(
  body: CreateAgentInstanceBody,
): Promise<CreateAgentInstanceResponse> {
  const tg = body.telegramUserId.trim()
  if (!tg) {
    throw new AppError('telegramUserId 必填', { status: 400 })
  }
  const payload: Record<string, string> = { telegramUserId: tg }
  const tid = body.templateId?.trim()
  if (tid) payload.templateId = tid
  const tv = body.templateVersion?.trim()
  if (tv) payload.templateVersion = tv
  const sub = body.exchangeSubAccountUserId?.trim()
  if (sub) payload.exchangeSubAccountUserId = sub
  try {
    return await httpClient.post(PATH, { json: payload }).json<CreateAgentInstanceResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** I05 更新实例 · 成功 **200** 返回详情项 */
export async function patchAgentInstance(
  instanceId: string,
  body: { instanceOverrides?: InstanceOverridesPatch; runtimeState?: string },
): Promise<AgentInstanceRow> {
  const id = instanceId.trim()
  if (!id) {
    throw new AppError('instanceId 不可为空', { status: 400 })
  }
  try {
    return await httpClient
      .patch(`${PATH}/${encodeURIComponent(id)}`, { json: body })
      .json<AgentInstanceRow>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** I04 登记子账户 · 成功 **200** */
export async function bindInstanceSubaccount(
  instanceId: string,
  body: { exchangeSubAccountUserId?: string; subAccountId?: string },
): Promise<AgentInstanceRow> {
  const id = instanceId.trim()
  const sub = (body.exchangeSubAccountUserId ?? body.subAccountId ?? '').trim()
  if (!id) {
    throw new AppError('instanceId 不可为空', { status: 400 })
  }
  if (!sub) {
    throw new AppError('须提供 exchangeSubAccountUserId 或 subAccountId', { status: 400 })
  }
  const json: Record<string, string> = {}
  if (body.exchangeSubAccountUserId?.trim()) {
    json.exchangeSubAccountUserId = body.exchangeSubAccountUserId.trim()
  } else {
    json.subAccountId = sub
  }
  try {
    return await httpClient
      .post(`${PATH}/${encodeURIComponent(id)}/binding`, { json })
      .json<AgentInstanceRow>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** I04 解绑托管行 · 成功 **204** */
export async function unbindInstanceSubaccount(instanceId: string): Promise<void> {
  const id = instanceId.trim()
  if (!id) {
    throw new AppError('instanceId 不可为空', { status: 400 })
  }
  try {
    await httpClient.delete(`${PATH}/${encodeURIComponent(id)}/binding`)
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** 硬删除 agent_instance · 成功 **204** 无 body；不删 trading-binding */
export async function deleteAgentInstance(instanceId: string): Promise<void> {
  const id = instanceId.trim()
  if (!id) {
    throw new AppError('instanceId 不可为空', { status: 400 })
  }
  try {
    await httpClient.delete(`${PATH}/${encodeURIComponent(id)}`)
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
