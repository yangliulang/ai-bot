/*
作者: 杨永的Agent
日期: 2026-05-12
修改功能: `TradingApiBindInput` / wire body 透传 `sub_account_id`（子账户 ID）
修改功能: `normalizeTradingApiBindResult` 透出 `bindingRowCreated`（与 `binding_row_created`）；成功页仅在重复绑定（UPDATE，`false`）时展示「已绑定」横幅
修改功能: `normalizeTradingApiBindResult` 透出 `saved`；成功页在 `BOUND` + `saved` 时提示「已完成绑定」
日期: 2026-05-12
修改功能: `postTradingApiBinding` 改走 `httpClient`（与 validate 同源：`VITE_API_BASE_URL` 默认 `/api` + 代理）；Body 用 snake_case 对齐校验/服务端
日期: 2026-05-12
修改功能: 绑定 Body 附带 `openapiBaseUrl`（服务端 `openapi_base_url` 别名），与 validate 同源
日期: 2026-05-12
修改功能: 绑定 POST 可选附带 `telegram`（与校验一致）；实现 `POST /api/v1/me/agent/bindings/trading-api` 的 /be 须收此字段
日期: 2026-05-12
修改功能: 对齐 product-doc/Web meAgent — POST 绑定子账户交易 API（VITE_AGENT_API_BASE_URL；未配置时页面走演示分支）
 */
import { HTTPError } from 'ky'

import { httpClient } from '@/shared/api/http-client'
import type { TelegramInboundPayload } from '@/shared/lib/onboarding'

/** 调用方入参（camelCase）；写入网络前会转为与 validate 一致的 snake_case */
export type TradingApiBindInput = {
  openapiBaseUrl: string
  apiKey: string
  apiSecret: string
  idempotencyKey: string
  /** Deeplink 签发的一次性票据（若有），非 Secret */
  deeplinkToken?: string
  telegram?: TelegramInboundPayload
  /** 交易所子账户 ID（与校验页一致） */
  subAccountId?: string
}

/** 与 `POST /api/v1/me/agent/bindings/trading-api` 响应兼容（camelCase / snake_case） */
export type TradingApiBindResult = {
  /** 服务端落库成功时多为 `true` */
  saved?: boolean
  agentTradingApiBindingStatus?: string
  agentTradingApiKeyId?: string
  agentSubAccountId?: string
  /**
   * `true`：新插入绑定行（解绑后重绑或首次绑定）；`false`：同一 tg 已存在行上的更新（重复提交绑定）。
   * 未返回时视为未知（不展示「重复绑定」横幅）。
   */
  bindingRowCreated?: boolean
}

export type TradingApiBindRejectCode =
  | 'AGENT_BIND_KEY_NOT_SUBACCOUNT'
  | 'AGENT_BIND_SUBACCOUNT_DISABLED'
  | 'AGENT_BIND_API_TRADING_DISABLED'
  | 'AGENT_BIND_SPOT_PERMISSION_DISABLED'
  | 'AGENT_BIND_MARGIN_PERMISSION_DISABLED'
  | 'AGENT_BIND_FUTURES_PERMISSION_DISABLED'
  | 'AGENT_BIND_PERMISSION_INCOMPLETE'

export type MissingPermissionKind = 'API_TRADING' | 'SPOT' | 'MARGIN' | 'FUTURES'

export type ApiErrorBody = {
  title?: string
  detail?: string
  message?: string
  status?: number
  code?: string
  details?: { missingPermissions?: MissingPermissionKind[] }
}

const MISSING_PERM_LABEL: Record<MissingPermissionKind, string> = {
  API_TRADING: 'API 交易',
  SPOT: '币币',
  MARGIN: '杠杆',
  FUTURES: '合约',
}

const BIND_REJECT_MESSAGE: Record<TradingApiBindRejectCode, string> = {
  AGENT_BIND_KEY_NOT_SUBACCOUNT:
    '当前 API Key 属于主账户。Agent 仅支持子账户 API Key，请在交易所创建子账户并使用其子账户 Key。',
  AGENT_BIND_SUBACCOUNT_DISABLED: '该子账户当前为禁用状态，请在交易所激活子账户后再保存。',
  AGENT_BIND_API_TRADING_DISABLED: '请为该子账户 API Key 开启「API 交易」权限。',
  AGENT_BIND_SPOT_PERMISSION_DISABLED: '请为该子账户 API Key 开启「币币」交易权限。',
  AGENT_BIND_MARGIN_PERMISSION_DISABLED: '请为该子账户 API Key 开启「杠杆」权限。',
  AGENT_BIND_FUTURES_PERMISSION_DISABLED: '请为该子账户 API Key 开启「合约」权限。',
  AGENT_BIND_PERMISSION_INCOMPLETE:
    '请为该子账户 API Key 同时开启 API 交易、币币、杠杆与合约权限；以下为仍未开启的项：',
}

export class TradingApiBindError extends Error {
  readonly status: number
  readonly code?: TradingApiBindRejectCode
  readonly raw?: unknown

  constructor(message: string, opts: { status: number; code?: TradingApiBindRejectCode; raw?: unknown }) {
    super(message)
    this.name = 'TradingApiBindError'
    this.status = opts.status
    this.code = opts.code
    this.raw = opts.raw
  }
}

export function messageFromTradingApiBindProblem(body: unknown, httpStatus: number): string {
  const prob = body as ApiErrorBody | undefined
  const code = prob?.code as TradingApiBindRejectCode | undefined

  if (code && BIND_REJECT_MESSAGE[code]) {
    if (code === 'AGENT_BIND_PERMISSION_INCOMPLETE') {
      const missing = prob?.details?.missingPermissions?.filter(Boolean)
      if (missing?.length) {
        const labels = missing.map((k) => MISSING_PERM_LABEL[k] ?? k)
        return `${BIND_REJECT_MESSAGE.AGENT_BIND_PERMISSION_INCOMPLETE}${labels.join('、')}。`
      }
      return `${BIND_REJECT_MESSAGE.AGENT_BIND_PERMISSION_INCOMPLETE}API 交易、币币、杠杆、合约。`
    }
    return BIND_REJECT_MESSAGE[code]
  }

  const fallback =
    prob?.detail ?? prob?.message ?? prob?.title ?? `绑定失败（HTTP ${httpStatus}）`
  return typeof fallback === 'string' ? fallback : `绑定失败（HTTP ${httpStatus}）`
}

/** 与 `validateAgentApiKeys` JSON 键一致，服务端 `MeAgentTradingApiBindingRequest` 全量接收 */
function toTradingApiBindWireBody(input: TradingApiBindInput): Record<string, unknown> {
  const body: Record<string, unknown> = {
    openapi_base_url: input.openapiBaseUrl.trim(),
    api_key: input.apiKey.trim(),
    secret_key: input.apiSecret.trim(),
    idempotency_key: input.idempotencyKey.trim(),
  }
  const token = input.deeplinkToken?.trim()
  if (token) body.deeplink_token = token
  if (input.telegram && Object.keys(input.telegram).length > 0) {
    body.telegram = input.telegram
  }
  const sid = input.subAccountId?.trim()
  if (sid) body.sub_account_id = sid
  return body
}

function normalizeTradingApiBindResult(data: Record<string, unknown>): TradingApiBindResult {
  const subId =
    (typeof data.agent_sub_account_id === 'string' && data.agent_sub_account_id) ||
    (typeof data.agentSubAccountId === 'string' && data.agentSubAccountId) ||
    undefined
  const status =
    (typeof data.agent_trading_api_binding_status === 'string' && data.agent_trading_api_binding_status) ||
    (typeof data.agentTradingApiBindingStatus === 'string' && data.agentTradingApiBindingStatus) ||
    undefined
  const keyId =
    (typeof data.agent_trading_api_key_id === 'string' && data.agent_trading_api_key_id) ||
    (typeof data.agentTradingApiKeyId === 'string' && data.agentTradingApiKeyId) ||
    undefined
  const saved = typeof data.saved === 'boolean' ? data.saved : undefined
  const bindingRowCreated =
    typeof data.binding_row_created === 'boolean'
      ? data.binding_row_created
      : typeof data.bindingRowCreated === 'boolean'
        ? data.bindingRowCreated
        : undefined
  return {
    saved,
    agentSubAccountId: subId,
    agentTradingApiBindingStatus: status,
    agentTradingApiKeyId: keyId,
    bindingRowCreated,
  }
}

function stripTrailingSlash(base: string): string {
  return base.replace(/\/+$/, '')
}

/** 跨域直连 Agent API 时用（与旧 env 兼容）；本仓绑定请求已优先走 {@link httpClient} */
export function getAgentApiBase(): string {
  const raw =
    import.meta.env.VITE_AGENT_API_BASE_URL?.trim() ||
    import.meta.env.VITE_COOBIT_API_BASE_URL?.trim()
  return raw ? stripTrailingSlash(raw) : ''
}

/**
 * POST `/api/v1/me/agent/bindings/trading-api`（前缀同 {@link httpClient}，开发时 `/api` 走 Vite 代理）。
 */
export async function postTradingApiBinding(input: TradingApiBindInput): Promise<TradingApiBindResult> {
  const json = toTradingApiBindWireBody(input)
  try {
    const data = (await httpClient
      .post('v1/me/agent/bindings/trading-api', { json })
      .json()) as Record<string, unknown>
    return normalizeTradingApiBindResult(data)
  } catch (e) {
    if (e instanceof HTTPError) {
      let raw: unknown
      try {
        raw = await e.response.json()
      } catch {
        raw = undefined
      }
      const msg = messageFromTradingApiBindProblem(raw, e.response.status)
      const prob = raw as ApiErrorBody | undefined
      const code = prob?.code as TradingApiBindRejectCode | undefined
      throw new TradingApiBindError(msg, { status: e.response.status, code, raw })
    }
    throw e
  }
}
