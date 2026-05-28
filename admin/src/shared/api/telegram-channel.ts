// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: **PATCH …/telegram/bot**（`runtimeParams` · 可选 **If-Match**）· GET 扩展 **runtimeParams/configVersion**
// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: Telegram 渠道 Bot 状态与连通性自检（对齐 OpenAPI admin/telegram-channels.yaml）

import { HTTPError } from 'ky'

import { AppError } from '@/shared/api/errors'
import { httpClient, toAppError } from '@/shared/api/http-client'

const BOT_PATH = 'v1/admin/channels/telegram/bot'
const SELF_TEST_PATH = 'v1/admin/channels/telegram/self-test'

export interface TelegramBotIdentity {
  id: string
  username?: string | null
  name?: string | null
}

export interface TelegramBotStatus {
  bot: TelegramBotIdentity | null
  channelTelegramEnabled: boolean
  lastFetchedAt: string
  lastErrorSummary?: string | null
  secretRefFingerprint?: string | null
  tokenConfigured: boolean
  /** 只读：server/.env CHAINUP_AGENT_PUBLIC_BASE_URL */
  publicBaseUrl?: string
  /** 只读：server/.env CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL */
  bindPageUrl?: string
  /** 只读：「使用默认 URL 注册」将提交的地址 */
  defaultWebhookUrl?: string
  /** FR-TG-ADMIN-02 · 非密钥运行参数（GET/PATCH 同窗） */
  runtimeParams?: Record<string, unknown> | null
  configVersion?: number | null
}

export interface TelegramBotPatchBody {
  telegramBotTokenSecretRef?: string | null
  runtimeParams?: Record<string, unknown>
}

export interface PatchTelegramBotOptions {
  ifMatch?: string | number | null
}

export interface TelegramSelfTestResult {
  getMeOk: boolean
  getWebhookInfoOk: boolean
  errorSummary?: string | null
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

export async function getTelegramBotStatus(): Promise<TelegramBotStatus> {
  try {
    return await httpClient.get(BOT_PATH).json<TelegramBotStatus>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

export async function postTelegramSelfTest(): Promise<TelegramSelfTestResult> {
  try {
    return await httpClient.post(SELF_TEST_PATH).json<TelegramSelfTestResult>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}

function ifMatchHeaderValue(ifMatch: string | number): string {
  const raw = String(ifMatch).trim()
  if (!raw) return raw
  return raw.startsWith('"') ? raw : `"${raw}"`
}

export async function patchTelegramBot(
  body: TelegramBotPatchBody,
  options?: PatchTelegramBotOptions,
): Promise<TelegramBotStatus> {
  const headers: Record<string, string> = {}
  if (options?.ifMatch != null && String(options.ifMatch).trim() !== '') {
    headers['If-Match'] = ifMatchHeaderValue(options.ifMatch)
  }
  try {
    return await httpClient
      .patch(BOT_PATH, { json: body, headers: Object.keys(headers).length ? headers : undefined })
      .json<TelegramBotStatus>()
  } catch (e) {
    throw await normalizeKyError(e)
  }
}
