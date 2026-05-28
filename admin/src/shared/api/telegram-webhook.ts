// 作者: 杨永的Agent
// 日期: 2026-05-12
// 修改功能: 运营侧 Telegram Webhook API（GET/POST/DELETE）与后端 ErrorBody 解析

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const WEBHOOK_PATH = 'v1/admin/channels/telegram/webhook'

/** 与 `server` `TelegramWebhookInfo`（camelCase JSON）对齐 */
export interface TelegramWebhookInfo {
  url: string
  hasCustomCertificate: boolean
  pendingUpdateCount: number
  lastErrorDate: number | null
  lastErrorMessage: string | null
  maxConnections: number | null
}

export interface TelegramWebhookSetPayload {
  url?: string
  secretToken?: string
  dropPendingUpdates?: boolean
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

export async function getTelegramWebhook(): Promise<TelegramWebhookInfo> {
  try {
    return await httpClient.get(WEBHOOK_PATH).json<TelegramWebhookInfo>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function setTelegramWebhook(
  payload?: TelegramWebhookSetPayload | null,
): Promise<TelegramWebhookInfo> {
  const json: Record<string, unknown> = {}
  const p = payload ?? undefined
  if (p?.url?.trim()) json.url = p.url.trim()
  if (p?.secretToken?.trim()) json.secretToken = p.secretToken.trim()
  if (typeof p?.dropPendingUpdates === 'boolean') json.dropPendingUpdates = p.dropPendingUpdates

  try {
    return await httpClient.post(WEBHOOK_PATH, { json }).json<TelegramWebhookInfo>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function deleteTelegramWebhook(): Promise<TelegramWebhookInfo> {
  try {
    return await httpClient.delete(WEBHOOK_PATH).json<TelegramWebhookInfo>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
