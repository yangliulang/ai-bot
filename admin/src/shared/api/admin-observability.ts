// 作者: 杨永的Agent
// 日期: 2026-05-18
// 修改功能: **`prompt.snapshot`** / **`llm.chat.faq`** / **`llm.{read.market.*|read.account.balance|wealth.holdings_read}`**（`gateway*` / `stepKind` · FE_HANDOFF 0014～0016）；现货撤单 **`cancel_order`** stepKind（FE_HANDOFF 2026-05-18）
// 作者: 杨永的Agent
// 日期: 2026-05-15
// 修改功能: `summary` 可选 **`venue` / `canonicalOp`**（ADR-004 · FE_HANDOFF）
// 日期: 2026-05-14
// 修改功能: `orderRequest.limitOrderMeta`（限价 base / price / TIF · trade.spot.limit_order）
// 日期: 2026-05-14
// 修改功能: `orderRequest.flashMarketMeta`（volume 语义协查 · MARKET BUY/SELL）
// 日期: 2026-05-14
// 修改功能: `summary.exchangeReadPreviewSummary` / `appErrorCode`（只读路由 §5.2.2）
// 日期: 2026-05-27
// 修改功能: 执行详情 Tab **`/queue|events|retries|recovery`** GET 与类型（FE_HANDOFF 2026-05-27）
// 日期: 2026-05-27
// 修改功能: **`promptBindingResolved` / `skillSpecRead`** 时间线 summary；**`getScenarioSkillScope`**（FE_HANDOFF 2026-05-26）
// 日期: 2026-05-14
// 修改功能: `ObservabilityTimelineSummary`（transitionTrigger/stepKind 等 · §5.2）
// 日期: 2026-05-14
// 修改功能: `GET …/executions/{id}/timeline`（ObservabilityTimelineResponse · FE_HANDOFF FR-MC801）
// 日期: 2026-05-13
// 修改功能: Admin Observability — `GET`/`DELETE …/executions`（agent_execution，FE_HANDOFF）

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'
import type { ResolvedPromptBinding } from '@/shared/api/admin-prompt-packs'

/** 时间线 `agent.skill.spec_read` · `summary.skillSpecRead` 镜像 */
export interface ObservabilitySkillSpecReadSummary {
  skillId?: string | null
  skillSpecVersion?: string | null
  specDigest?: string | null
  phase?: string | null
}

/** 场景 Skill 范围 · `GET …/scenarios/{scenarioId}/skill-scope` */
export interface ScenarioSkillScopeSkillItem {
  skillId: string
  skillSpecVersion?: string | null
  specDigest?: string | null
  contractComplete?: boolean | null
  role?: string | null
}

export interface ScenarioSkillScopeResponse {
  scenarioId: string
  category: string
  mode: 'write_skill' | 'read_only' | 'unmapped_write' | string
  skills: ScenarioSkillScopeSkillItem[]
  promptStrategyPackId?: string | null
  promptStrategyVersion?: string | null
  promptSkillScopeRef?: string | null
  narrative: string
}

const PREFIX = 'v1/admin/observability'

/** 与 `AdminAgentExecutionItem`（camelCase）一致 */
export interface AdminAgentExecutionItem {
  executionId: string
  userId: string
  scenarioId: string | null
  channel: string | null
  state: string
  source: string | null
  idempotencyKey: string | null
  note: string | null
  /** 已发布 Prompt 包版本（accept 时未手填可由服务端写入；无发布包时为 `null` / 省略） */
  promptPackVersion?: string | null
  /** 与 effective prompts 同源绑定快照 */
  resolvedPromptBinding?: ResolvedPromptBinding | Record<string, unknown> | null
  createdAt: string
  updatedAt: string | null
}

export interface AdminAgentExecutionListResponse {
  items: AdminAgentExecutionItem[]
  total: number
}

/** `orderRequest.flashMarketMeta` · 标明 MARKET 单 wire `volume` 与用户意向的区别 */
export interface ObservabilityFlashMarketMeta {
  volumeSemantics?: string
  baseQtyUserRequested?: string | number
  /** BUY：`volume` 字段实为计价金额，与本字段一致 */
  quoteAmountOnWire?: string | number
  /** SELL：`volume` 与 base 数量一致时常与本字段对齐 */
  baseQtyOnWire?: string | number
  lastPriceUsed?: string | number
  volumeSemanticsNote?: string
  userVolumeInput?: string
}

/** `orderRequest.limitOrderMeta` · LIMIT 协查（与闪兑 `flashMarketMeta` 并列） */
export interface ObservabilityLimitOrderMeta {
  volumeSemantics?: string
  limitPriceUserRequested?: string | number
  baseQtyUserRequested?: string | number
  timeInForce?: string
}

/** 时间线里脱敏的下单请求快照（嵌于 `summary.orderRequest`） */
export interface ObservabilityOrderRequestSnapshot {
  path?: string
  symbol?: string
  side?: string
  type?: string
  volume?: string | number
  price?: string | number
  newClientOrderId?: string
  flashMarketMeta?: ObservabilityFlashMarketMeta
  limitOrderMeta?: ObservabilityLimitOrderMeta
}

/**
 * 时间线 `summary` 常见键（详见 `API_ADMIN_OBSERVABILITY_EXECUTIONS.md` §5.2）。
 * 服务端仍可追加任意字段，故保留索引签名由调用方收窄读取。
 */
export type ObservabilityTimelineSummary = Record<string, unknown> & {
  /** 如 flash：`quote` / `confirm_prompt` / `confirm_accept` / `submit_order` */
  stepKind?: string
  /** 状态迁移触发（若后端写入） */
  transitionTrigger?: string
  scenarioId?: string
  outcome?: string
  methodPathSummary?: string
  exchangeOutcome?: string
  clientOrderRef?: string
  httpStatus?: number
  orderRequest?: ObservabilityOrderRequestSnapshot
  exchangeResponsePreview?: Record<string, unknown>
  /** 只读路由成功：`routing/execute` · Telegram `read.*`（§5.2.2） */
  exchangeReadPreviewSummary?: Record<string, unknown> | string | number | boolean | null
  /** 只读失败：`routing.read.failed` */
  appErrorCode?: string
  /** 交易场所（限价/闪兑写路径摘要 · ADR-004） */
  venue?: string
  /** 规范操作名（如 `place_order`） */
  canonicalOp?: string
  /** `prompt.snapshot` / `llm.chat.faq` / 托管预览 `llm.*` 叙述：**Prompt 版本与网关快照** */
  promptPackVersion?: string | null
  /** 与 effective 同源绑定 */
  resolvedPromptBinding?: ResolvedPromptBinding | Record<string, unknown> | null
  /** `agent.prompt.binding_resolved` 镜像（与 `resolvedPromptBinding` 同形） */
  promptBindingResolved?: ResolvedPromptBinding | Record<string, unknown> | null
  /** `agent.skill.spec_read` 镜像 */
  skillSpecRead?: ObservabilitySkillSpecReadSummary | Record<string, unknown> | null
  skillId?: string | null
  skillSpecVersion?: string | null
  specDigest?: string | null
  /** 闲聊网关：目录模型 id（已解析时） */
  gatewayModelId?: string | null
  /** 对端 HTTP model 线 id（apiModel ?? modelId） */
  gatewayUpstreamModel?: string | null
  gatewayProviderId?: string | null
  /** 方舟 `/api/v3/responses` 路径 */
  useArkProtocol?: boolean | null
}

/** `/executions/{id}/timeline` 单项 · camelCase JSON */
export interface ObservabilityTimelineItem {
  ts: string
  eventName: string
  executionId?: string | null
  userId?: string | null
  summary: ObservabilityTimelineSummary
}

export interface ObservabilityTimelineResponse {
  items: ObservabilityTimelineItem[]
}

export type ListAdminExecutionsParams = {
  limit?: number
  offset?: number
  executionId?: string
  userId?: string
  channel?: string
  scenarioId?: string
  state?: string
  keyword?: string
  createdAfter?: string
  createdBefore?: string
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

function optionalSearchParams(p: ListAdminExecutionsParams): Record<string, string> {
  const out: Record<string, string> = {}
  const lim = p.limit ?? 50
  const off = p.offset ?? 0
  out.limit = String(Math.min(200, Math.max(1, lim)))
  out.offset = String(Math.max(0, off))
  const eid = p.executionId?.trim()
  if (eid) out.executionId = eid
  const uid = p.userId?.trim()
  if (uid) out.userId = uid
  const ch = p.channel?.trim()
  if (ch) out.channel = ch
  const sid = p.scenarioId?.trim()
  if (sid) out.scenarioId = sid
  const st = p.state?.trim()
  if (st) out.state = st
  const kw = p.keyword?.trim()
  if (kw) out.keyword = kw
  const ca = p.createdAfter?.trim()
  if (ca) out.createdAfter = ca
  const cb = p.createdBefore?.trim()
  if (cb) out.createdBefore = cb
  return out
}

export async function listAdminObservabilityExecutions(
  params: ListAdminExecutionsParams = {},
): Promise<AdminAgentExecutionListResponse> {
  try {
    return await httpClient
      .get(`${PREFIX}/executions`, { searchParams: optionalSearchParams(params) })
      .json<AdminAgentExecutionListResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAdminObservabilityExecutionTimeline(
  executionId: string,
): Promise<ObservabilityTimelineResponse> {
  const id = executionId.trim()
  if (!id) throw new AppError('executionId 不可为空', { status: 400 })
  try {
    return await httpClient
      .get(`${PREFIX}/executions/${encodeURIComponent(id)}/timeline`)
      .json<ObservabilityTimelineResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAdminObservabilityExecution(executionId: string): Promise<AdminAgentExecutionItem> {
  const id = executionId.trim()
  if (!id) throw new AppError('executionId 不可为空', { status: 400 })
  try {
    return await httpClient
      .get(`${PREFIX}/executions/${encodeURIComponent(id)}`)
      .json<AdminAgentExecutionItem>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** 硬删除持久化 execution · 成功 **204** 无 Body */
export async function deleteAdminObservabilityExecution(executionId: string): Promise<void> {
  const id = executionId.trim()
  if (!id) throw new AppError('executionId 不可为空', { status: 400 })
  try {
    await httpClient.delete(`${PREFIX}/executions/${encodeURIComponent(id)}`)
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** FR-MC803 · `GET …/executions/{id}/tool-calls` */
export interface ObservabilityToolCallItem {
  toolId: string
  toolCallSeq: number
  invocationState: string
  phase?: string | null
  durationMs?: number | null
  agentSubAccountId?: string | null
  eventName?: string | null
  stepKind?: string | null
  ts?: string | null
  summary?: Record<string, unknown>
}

export interface ObservabilityToolCallsResponse {
  items: ObservabilityToolCallItem[]
}

/** FR-MC804 · `GET …/executions/{id}/llm`（无 messages 全文） */
export interface ObservabilityLlmCallItem {
  eventName: string
  toolCallSeq: number
  ts: string
  modelId?: string | null
  gatewayModelId?: string | null
  gatewayUpstreamModel?: string | null
  gatewayProviderId?: string | null
  outcome?: string | null
  stepKind?: string | null
  scenarioId?: string | null
  promptPackVersion?: string | null
  inputTokens?: number | null
  outputTokens?: number | null
  totalTokens?: number | null
}

export interface ObservabilityLlmUsageResponse {
  modelId?: string | null
  inputTokens?: number | null
  outputTokens?: number | null
  totalTokens?: number | null
  calls: ObservabilityLlmCallItem[]
}

/** `GET …/executions/{id}/queue` */
export interface ExecutionTaskQueueItem {
  taskId: string
  executionId: string
  state: 'PENDING' | 'RUNNING' | 'BLOCKED' | string
  scheduledAt: string
  stepKey?: string | null
  stepLabelZh?: string | null
}

export interface ExecutionTaskQueueResponse {
  items: ExecutionTaskQueueItem[]
}

/** `GET …/executions/{id}/events` */
export interface ExecutionRuntimeEventItem {
  executionId: string
  at: string
  eventType: string
  summary: string
  seq?: number | null
}

export interface ExecutionRuntimeEventsResponse {
  items: ExecutionRuntimeEventItem[]
}

/** `GET …/executions/{id}/retries` */
export interface ExecutionRetryItem {
  attempt: number
  at: string
  reason: string
  eventType?: string | null
  seq?: number | null
}

export interface ExecutionRetriesResponse {
  retryCount: number
  items: ExecutionRetryItem[]
}

/** `GET …/executions/{id}/recovery` */
export interface ExecutionRecoveryResponse {
  executionId: string
  scenarioId?: string | null
  executionState: string
  caseKind: string
  resolutionStatus: string
  stillUnknown: boolean
  lastReconcileAt?: string | null
  lastReconcileAtSeq?: number | null
  reconcileId?: string | null
  userMessage?: string | null
  hints?: string[]
  recoveryTitle: string
  recoveryBody: string
  observabilitySearchPath: string
  reconcileApiHint: Record<string, unknown>
  manualRetrySupported: boolean
}

export async function getAdminObservabilityToolCalls(
  executionId: string,
): Promise<ObservabilityToolCallsResponse> {
  const id = executionId.trim()
  if (!id) throw new AppError('executionId 不可为空', { status: 400 })
  try {
    return await httpClient
      .get(`${PREFIX}/executions/${encodeURIComponent(id)}/tool-calls`)
      .json<ObservabilityToolCallsResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getScenarioSkillScope(scenarioId: string): Promise<ScenarioSkillScopeResponse> {
  const sid = scenarioId.trim()
  if (!sid) throw new AppError('scenarioId 不可为空', { status: 400 })
  try {
    return await httpClient
      .get(`${PREFIX}/scenarios/${encodeURIComponent(sid)}/skill-scope`)
      .json<ScenarioSkillScopeResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAdminObservabilityLlm(
  executionId: string,
): Promise<ObservabilityLlmUsageResponse> {
  const id = executionId.trim()
  if (!id) throw new AppError('executionId 不可为空', { status: 400 })
  try {
    return await httpClient
      .get(`${PREFIX}/executions/${encodeURIComponent(id)}/llm`)
      .json<ObservabilityLlmUsageResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

async function getExecutionSubResource<T>(executionId: string, suffix: string): Promise<T> {
  const id = executionId.trim()
  if (!id) throw new AppError('executionId 不可为空', { status: 400 })
  try {
    return await httpClient
      .get(`${PREFIX}/executions/${encodeURIComponent(id)}/${suffix}`)
      .json<T>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export function getAdminObservabilityExecutionQueue(
  executionId: string,
): Promise<ExecutionTaskQueueResponse> {
  return getExecutionSubResource<ExecutionTaskQueueResponse>(executionId, 'queue')
}

export function getAdminObservabilityExecutionEvents(
  executionId: string,
): Promise<ExecutionRuntimeEventsResponse> {
  return getExecutionSubResource<ExecutionRuntimeEventsResponse>(executionId, 'events')
}

export function getAdminObservabilityExecutionRetries(
  executionId: string,
): Promise<ExecutionRetriesResponse> {
  return getExecutionSubResource<ExecutionRetriesResponse>(executionId, 'retries')
}

export function getAdminObservabilityExecutionRecovery(
  executionId: string,
): Promise<ExecutionRecoveryResponse> {
  return getExecutionSubResource<ExecutionRecoveryResponse>(executionId, 'recovery')
}
