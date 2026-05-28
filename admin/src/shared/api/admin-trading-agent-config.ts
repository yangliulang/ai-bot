// 作者: 杨永的Agent
// 日期: 2026-05-28
// 修改功能: GlobalConfigBundle GET/PATCH（MR-MEM-01 续 · trading-agent-config/bundle）

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const PREFIX = 'v1/admin/trading-agent-config'

export const AGENT_AI_SETTINGS_VERSION_CONFLICT = 'AGENT_AI_SETTINGS_VERSION_CONFLICT'

export type TradingAgentConfigValue = string | number | boolean

export interface TradingAgentConfigBundle {
  configVersion: number
  values: Record<string, TradingAgentConfigValue>
  defaults?: Record<string, TradingAgentConfigValue> | null
  appliedKeys?: string[]
}

export interface TradingAgentConfigBundlePatchBody {
  values: Record<string, TradingAgentConfigValue>
  expectedConfigVersion?: number
}

function ifMatchHeader(configVersion: number | string): Record<string, string> {
  const v = String(configVersion).trim()
  return { 'If-Match': v.startsWith('"') ? v : `"${v}"` }
}

async function normalizeKyError(error: unknown): Promise<never> {
  if (error instanceof HTTPError) {
    const cloned = error.response.clone()
    const body: unknown = await cloned.json().catch(() => null)
    if (body !== null && typeof body === 'object') {
      const code =
        'code' in body && typeof (body as { code: unknown }).code === 'string'
          ? (body as { code: string }).code
          : undefined
      let message: string | undefined
      if ('message' in body && typeof (body as { message: unknown }).message === 'string') {
        message = (body as { message: string }).message
      } else if ('detail' in body && typeof (body as { detail: unknown }).detail === 'string') {
        message = (body as { detail: string }).detail
      }
      throw new AppError(message ?? '请求失败', { status: error.response.status, code })
    }
  }
  throw await toAppError(error)
}

export async function getTradingAgentConfigBundle(): Promise<TradingAgentConfigBundle> {
  try {
    return await httpClient.get(`${PREFIX}/bundle`).json<TradingAgentConfigBundle>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function patchTradingAgentConfigBundle(
  body: TradingAgentConfigBundlePatchBody,
  options?: { ifMatch?: number | string },
): Promise<TradingAgentConfigBundle> {
  if (!body.values || Object.keys(body.values).length === 0) {
    throw new AppError('values 不可为空', { status: 400 })
  }
  try {
    const headers =
      options?.ifMatch != null ? ifMatchHeader(options.ifMatch) : undefined
    return await httpClient
      .patch(`${PREFIX}/bundle`, {
        json: {
          values: body.values,
          ...(body.expectedConfigVersion != null
            ? { expectedConfigVersion: body.expectedConfigVersion }
            : {}),
        },
        headers,
      })
      .json<TradingAgentConfigBundle>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
