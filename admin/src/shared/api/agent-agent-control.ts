// 作者: 杨永的Agent
// 日期: 2026-05-14
// 修改功能: **G01** **`global-agent-gate`**、实例 **Runtime R01–R06**、**L01–L03** logs（`/instances/{id}/logs/*`，FE_HANDOFF）

import { HTTPError } from 'ky'

import type { AgentInstanceRow } from '@/shared/api/agent-instances'
import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const AGENTS_PREFIX = 'v1/admin/agents'

export type AgentRuntimeControlAction = 'start' | 'pause' | 'resume' | 'stop'

export interface GlobalAgentGateResponse {
  globalAgentSwitchOn: boolean
  opsSuspended: boolean
  bannerMessage: string | null
  reasonCodes: string[]
}

export interface AgentBatchFailureItem {
  instanceId: string
  code: string
  message: string
}

export interface AgentBatchRuntimeResponse {
  code?: string | null
  message?: string | null
  succeeded: string[]
  failures: AgentBatchFailureItem[]
}

export interface AgentRuntimeBatchRequestBody {
  instanceIds: string[]
  action: AgentRuntimeControlAction
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

export async function getGlobalAgentGate(): Promise<GlobalAgentGateResponse> {
  try {
    return await httpClient
      .get(`${AGENTS_PREFIX}/runtime/global-agent-gate`)
      .json<GlobalAgentGateResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function postAgentInstanceRuntimeAction(
  instanceId: string,
  action: AgentRuntimeControlAction,
): Promise<AgentInstanceRow> {
  const id = instanceId.trim()
  if (!id) throw new AppError('instanceId 不可为空', { status: 400 })
  try {
    return await httpClient
      .post(`${AGENTS_PREFIX}/instances/${encodeURIComponent(id)}/runtime/${action}`, { json: {} })
      .json<AgentInstanceRow>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function postAgentInstancesRuntimeBatch(
  body: AgentRuntimeBatchRequestBody,
): Promise<AgentBatchRuntimeResponse> {
  try {
    return await httpClient
      .post(`${AGENTS_PREFIX}/instances/runtime/batch`, {
        json: {
          instanceIds: body.instanceIds.map((s) => s.trim()).filter(Boolean),
          action: body.action,
        },
      })
      .json<AgentBatchRuntimeResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

// --- Instance logs (L01–L03)

export interface InstanceConversationLogItem {
  executionId: string
  scenarioId?: string | null
  channel?: string | null
  state: string
  createdAt: string
  notePreview?: string | null
  observabilityExecutionPath: string
}

export interface InstanceConversationLogsResponse {
  tab: 'conversations'
  items: InstanceConversationLogItem[]
  total: number
  observabilityBasePath?: string
}

export interface InstanceToolLogItem {
  eventId: string
  executionId: string
  eventName: string
  stepKind?: string | null
  outcome?: string | null
  createdAt: string
  summary: Record<string, unknown>
  observabilityTimelinePath: string
}

export interface InstanceToolLogsResponse {
  tab: 'tools'
  items: InstanceToolLogItem[]
  total: number
  observabilityBasePath?: string
}

export interface InstanceErrorLogItem {
  kind: 'execution_failed' | 'timeline_step_failed'
  executionId: string
  createdAt: string
  scenarioId?: string | null
  channel?: string | null
  stateOrOutcome: string
  message?: string | null
  observabilityTimelinePath: string
}

export interface InstanceErrorLogsResponse {
  tab: 'errors'
  items: InstanceErrorLogItem[]
  total: number
  observabilityBasePath?: string
}

function clampLimitOff(limit?: number, offset?: number): { limit: number; offset: number } {
  const lim = Number.isFinite(limit ?? NaN) ? Math.floor(limit as number) : 50
  const off = Number.isFinite(offset ?? NaN) ? Math.floor(offset as number) : 0
  return {
    limit: Math.min(200, Math.max(1, lim)),
    offset: Math.max(0, off),
  }
}

export async function getAgentInstanceLogsConversations(
  instanceId: string,
  params?: { limit?: number; offset?: number },
): Promise<InstanceConversationLogsResponse> {
  const id = instanceId.trim()
  if (!id) throw new AppError('instanceId 不可为空', { status: 400 })
  const { limit, offset } = clampLimitOff(params?.limit, params?.offset)
  try {
    return await httpClient
      .get(`${AGENTS_PREFIX}/instances/${encodeURIComponent(id)}/logs/conversations`, {
        searchParams: { limit: String(limit), offset: String(offset) },
      })
      .json<InstanceConversationLogsResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAgentInstanceLogsTools(
  instanceId: string,
  params?: { limit?: number; offset?: number },
): Promise<InstanceToolLogsResponse> {
  const id = instanceId.trim()
  if (!id) throw new AppError('instanceId 不可为空', { status: 400 })
  const { limit, offset } = clampLimitOff(params?.limit, params?.offset)
  try {
    return await httpClient
      .get(`${AGENTS_PREFIX}/instances/${encodeURIComponent(id)}/logs/tools`, {
        searchParams: { limit: String(limit), offset: String(offset) },
      })
      .json<InstanceToolLogsResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function getAgentInstanceLogsErrors(
  instanceId: string,
  params?: { limit?: number; offset?: number },
): Promise<InstanceErrorLogsResponse> {
  const id = instanceId.trim()
  if (!id) throw new AppError('instanceId 不可为空', { status: 400 })
  const { limit, offset } = clampLimitOff(params?.limit, params?.offset)
  try {
    return await httpClient
      .get(`${AGENTS_PREFIX}/instances/${encodeURIComponent(id)}/logs/errors`, {
        searchParams: { limit: String(limit), offset: String(offset) },
      })
      .json<InstanceErrorLogsResponse>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
