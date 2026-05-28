/*
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 校验/绑定 POST 可选 `sub_account_id`（`subAccountId`），与 Deeplink 子账户 ID 输入对齐
修改功能: 校验请求体可选 `telegram`（与 onboarding.buildTelegramInboundPayload 对齐）；当前服务端未建模则忽略
日期: 2026-05-11
修改功能: 调用服务端校验子账户交易 API Key / Secret（契约供 /be 落地 POST /api/v1/agent/api-binding/validate）
日期: 2026-05-11
修改功能: 请求体附带 ``openapi_base_url``（GitBook ``baseurl``）；服务端验签时需按此根地址请求交易所
 */
import { HTTPError } from 'ky'

import { httpClient } from '@/shared/api/http-client'
import type { TelegramInboundPayload } from '@/shared/lib/onboarding'

/**
 * 请求体：与主站/所内交易 API 命名对齐（由服务端转发交易所或验签）。
 * 参见 [Coobit / ChainUp OpenAPI 说明](https://exchangedocsv2.gitbook.io/open-api-doc-v2)：`baseurl`、``X-CH-APIKEY`` 等。
 */
export type ValidateAgentApiKeysJson = {
  api_key: string
  secret_key: string
  /** OpenAPI Host 基准（不设 path 或使用站点根）；Phase1 /be 可忽略，联调交易所时必填语义 */
  openapi_base_url: string
  /** 交易所子账户 ID（用户自填；与 /be ``sub_account_id`` 对齐） */
  sub_account_id?: string
  /** Telegram 入站上下文；/be 需在 ``ValidateAgentApiKeysRequest`` 中建模后方可落库/审计 */
  telegram?: TelegramInboundPayload
}

/**
 * 服务端须实现：**POST `/api/v1/agent/api-binding/validate`**
 * - **200**：`{ "valid": true }` 或 `{ "ok": true }`（二者任一视为成功）
 * - **4xx**：`ErrorBody`（`code` / `message`）表示密钥无效或权限不足等
 * - **`openapi_base_url`**：后端向交易所发起探测或签名请求时的根 URL（Pydantic 可 `Field` 可选；未实现前忽略）
 */
export async function validateAgentApiKeys(body: ValidateAgentApiKeysJson): Promise<{ ok: true }> {
  const data = (await httpClient
    .post('v1/agent/api-binding/validate', {
      json: body,
    })
    .json()) as Record<string, unknown>

  const valid =
    data.valid === true ||
    data.ok === true ||
    (typeof data.data === 'object' &&
      data.data !== null &&
      (data.data as Record<string, unknown>).valid === true)

  if (!valid) {
    throw new Error('校验响应未表明成功')
  }
  return { ok: true }
}

/** 从 ky 错误中提取可读 `message`（与 `ErrorBody` 对齐时优先） */
export async function errorMessageFromKy(err: unknown): Promise<string> {
  if (err instanceof HTTPError) {
    try {
      const j = (await err.response.json()) as Record<string, unknown>
      const m = j.message
      if (typeof m === 'string' && m.trim()) return m.trim()
    } catch {
      // ignore
    }
    return `请求失败（HTTP ${err.response.status}）`
  }
  if (err instanceof Error) return err.message || '未知错误'
  return '网络异常'
}
