// 作者: 杨永的Agent
// 日期: 2026-05-21
// 修改功能: **`PromptPackSummary`/`PromptPackDetail.title`** · **`resolvePromptPackDisplayTitle`**
// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: **`CreatePromptPackBody.sourcePromptPackId`**（从模板复制 · FE_HANDOFF 新建草稿）
// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: fork / versions / rollback；PATCH 可选 If-Match（rowVersion）；详情 bodyMarkdown / updatedAt
// 作者: 杨永的Agent
// 日期: 2026-05-19
// 修改功能: PATCH 支持 **`variableSchema`**（与 **`messages`** 至少其一）；**`PromptPackDetail.variableSchema`**（FE_HANDOFF AC-09f）
// 作者: 杨永的Agent
// 日期: 2026-05-17
// 修改功能: POST 创建 DRAFT、`…/publish`、列表 Query；保留 GET 详情与 PATCH messages（FE_HANDOFF 2026-05-15）
import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/admin/prompt-packs'

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

export interface PromptPackSummary {
  promptPackId: string
  promptPackType: string
  scenarioId: string | null
  /** 运营展示名（服务端解析 · 只读） */
  title?: string | null
  promptPackVersion: string | null
  lifecycle: string | null
  etag: string | null
}

export interface PromptPackListResponse {
  items: PromptPackSummary[]
}

export interface ResolvedPromptBinding {
  scenarioId?: string | null
  sessionId?: string | null
  systemPromptPackId?: string | null
  systemPromptPackVersion?: string | null
  safetyPromptPackId?: string | null
  safetyPromptPackVersion?: string | null
  tradingPromptPackId?: string | null
  tradingPromptPackVersion?: string | null
  runtimeClarifyPromptPackId?: string | null
  runtimeClarifyPromptPackVersion?: string | null
  runtimeOutputContractPromptPackId?: string | null
  runtimeOutputContractPromptPackVersion?: string | null
  fewShotDigest?: string | null
  placeholderDenylistRevision?: string | null
  safetyPhraseBlocklistRevision?: string | null
}

export interface PromptPackDetail {
  promptPackId: string
  promptPackType: string
  scenarioId: string | null
  /** 运营展示名（服务端解析 · 只读） */
  title?: string | null
  promptPackVersion: string
  lifecycle: string
  etag: string | null
  rowVersion?: number | null
  updatedAt?: string | null
  placeholderDenylistRevision?: string | null
  safetyPhraseBlocklistRevision?: string | null
  messages: Record<string, unknown>[]
  /** 编辑器正文（与 messages 中 system content 同源） */
  bodyMarkdown?: string | null
  resolvedPromptBinding: ResolvedPromptBinding
  /** 非空 JSON 对象时：**`messages` 内 `{{slug}}`** 须在 **本平台白名单 ∪ 本题键集合** · `nullable`（见服务端校验） */
  variableSchema?: Record<string, unknown> | null
}

export interface PromptPackVersionEntry {
  promptPackVersion: string
  publishedAt: string
  lifecycle?: string | null
  event?: string | null
  actor?: string | null
  summary?: string | null
}

export interface PromptPackVersionHistoryResponse {
  items: PromptPackVersionEntry[]
}

export interface PromptPackForkBody {
  promptPackId?: string
}

export interface PromptPackRollbackBody {
  promptPackVersion: string
}

export interface PatchPromptPackOptions {
  /** PM-C03：传 **`rowVersion`**（数字或已带引号的 ETag 字符串） */
  ifMatch?: string | number | null
}

/** PATCH：**`messages` / `variableSchema`** 可选；服务端要求 **至少传其一**（本模块在发包前兜底校验）。 */
export interface PromptPackPatchBody {
  messages?: Record<string, unknown>[]
  variableSchema?: Record<string, unknown> | null
}

/** @deprecated 请改用 **`PromptPackPatchBody`**；保留别名供旧 import。 */
export type PromptPackMessagesPatchBody = PromptPackPatchBody

/** 列表查询，与控制台筛选对齐；服务端未识别之键会自动忽略或由网关校验 */
export interface ListPromptPacksQuery {
  promptPackType?: string
  scenarioId?: string
  lifecycle?: string
}

export interface CreatePromptPackBody {
  promptPackType: string
  scenarioId?: string
  promptPackId?: string
  /** 从已有包复制 messages + variableSchema 到新 DRAFT */
  sourcePromptPackId?: string
}

export interface PromptPackPublishResult {
  promptPackId: string
  promptPackVersion: string
  lifecycle: string
}

/** 列表/编辑器展示名：优先 **`title`**，fallback scenarioId → promptPackId */
export function resolvePromptPackDisplayTitle(
  row: Pick<PromptPackSummary, 'title' | 'scenarioId' | 'promptPackId'>,
): string {
  const title = (row.title ?? '').trim()
  if (title) return title
  const sid = (row.scenarioId ?? '').trim()
  return sid || row.promptPackId
}

function withListQuery(prefix: string, query?: ListPromptPacksQuery): string {
  if (!query) return prefix
  const params = new URLSearchParams()
  const t = query.promptPackType?.trim()
  const s = query.scenarioId?.trim()
  const l = query.lifecycle?.trim()
  if (t) params.set('promptPackType', t)
  if (s) params.set('scenarioId', s)
  if (l) params.set('lifecycle', l)
  const qs = params.toString()
  return qs ? `${prefix}?${qs}` : prefix
}

export async function listPromptPacks(query?: ListPromptPacksQuery): Promise<PromptPackListResponse> {
  try {
    return await httpClient.get(withListQuery(PREFIX, query)).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getPromptPack(promptPackId: string): Promise<PromptPackDetail> {
  try {
    return await httpClient.get(`${PREFIX}/${encodeURIComponent(promptPackId)}`).json()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

function ifMatchHeaderValue(ifMatch: string | number): string {
  const raw = String(ifMatch).trim()
  if (!raw) return raw
  return raw.startsWith('"') ? raw : `"${raw}"`
}

export async function patchPromptPack(
  promptPackId: string,
  body: PromptPackPatchBody,
  options?: PatchPromptPackOptions,
): Promise<PromptPackDetail> {
  const hasMessages = body.messages !== undefined
  const hasSchema = body.variableSchema !== undefined
  if (!hasMessages && !hasSchema) {
    throw new AppError('messages 与 variableSchema 至少须在 PATCH Body 中带其一。', {
      status: 400,
    })
  }
  const headers: Record<string, string> = {}
  if (options?.ifMatch != null && String(options.ifMatch).trim() !== '') {
    headers['If-Match'] = ifMatchHeaderValue(options.ifMatch)
  }
  try {
    return await httpClient
      .patch(`${PREFIX}/${encodeURIComponent(promptPackId)}`, { json: body, headers })
      .json<PromptPackDetail>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function forkPromptPack(
  sourcePromptPackId: string,
  body?: PromptPackForkBody,
): Promise<PromptPackDetail> {
  try {
    const payload: Record<string, string> = {}
    const pid = body?.promptPackId?.trim()
    if (pid) payload.promptPackId = pid
    return await httpClient
      .post(`${PREFIX}/${encodeURIComponent(sourcePromptPackId)}/fork`, {
        json: Object.keys(payload).length ? payload : {},
      })
      .json<PromptPackDetail>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function listPromptPackVersions(
  promptPackId: string,
): Promise<PromptPackVersionHistoryResponse> {
  try {
    return await httpClient
      .get(`${PREFIX}/${encodeURIComponent(promptPackId)}/versions`)
      .json<PromptPackVersionHistoryResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function rollbackPromptPack(
  promptPackId: string,
  body: PromptPackRollbackBody,
): Promise<PromptPackPublishResult> {
  try {
    return await httpClient
      .post(`${PREFIX}/${encodeURIComponent(promptPackId)}/rollback`, { json: body })
      .json<PromptPackPublishResult>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

/** PATCH 别名：与 **`patchPromptPack`** 等价。 */
export async function patchPromptPackMessages(
  promptPackId: string,
  body: PromptPackMessagesPatchBody,
): Promise<PromptPackDetail> {
  return patchPromptPack(promptPackId, body)
}

export async function createPromptPack(body: CreatePromptPackBody): Promise<PromptPackDetail> {
  try {
    const payload: Record<string, string> = {
      promptPackType: body.promptPackType.trim(),
    }
    const sid = body.scenarioId?.trim()
    const pid = body.promptPackId?.trim()
    const src = body.sourcePromptPackId?.trim()
    if (sid) payload.scenarioId = sid
    if (pid) payload.promptPackId = pid
    if (src) payload.sourcePromptPackId = src
    return await httpClient.post(PREFIX, { json: payload }).json<PromptPackDetail>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function publishPromptPack(promptPackId: string): Promise<PromptPackPublishResult> {
  try {
    return await httpClient
      .post(`${PREFIX}/${encodeURIComponent(promptPackId)}/publish`)
      .json<PromptPackPublishResult>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
