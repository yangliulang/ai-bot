/*
作者: 杨永的Agent
日期: 2026-05-12
修改功能: pending 快照含 `subAccountId`，与校验页子账户 ID 字段一并提交绑定
修改功能: `AgentOnboardingBindResult` 增加 `bindingRowCreated`（`false` 时成功页才展示「已绑定」重复提示）
修改功能: `AgentOnboardingBindResult` 增加 `saved` / `agentTradingApiBindingStatus`（服务端 BOUND）
日期: 2026-05-12
修改功能: onboarding 多页流程用 sessionStorage 传递校验通过后的待绑定快照与成功结果（同标签会话；勿入 URL）
 */
import type { TelegramInboundPayload } from '@/shared/lib/onboarding'

const PENDING_KEY = 'dl_agent_onboard_pending_v1'
const RESULT_KEY = 'dl_agent_onboard_bind_result_v1'

export type AgentOnboardingPendingBind = {
  apiKey: string
  apiSecret: string
  openapiRoot: string
  /** 用户填写的交易所子账户 ID */
  subAccountId: string
  telegram?: TelegramInboundPayload
}

export type AgentOnboardingBindResult = {
  agentSubAccountId?: string
  /** 服务端 `POST .../bindings/trading-api` 成功体 */
  saved?: boolean
  agentTradingApiBindingStatus?: string
  /** 与 `bindingRowCreated` / `binding_row_created` 对齐；缺省则不展示「重复绑定」横幅 */
  bindingRowCreated?: boolean
}

export function saveAgentOnboardingPendingBind(s: AgentOnboardingPendingBind): void {
  try {
    sessionStorage.setItem(PENDING_KEY, JSON.stringify(s))
  } catch {
    /* ignore */
  }
}

export function readAgentOnboardingPendingBind(): AgentOnboardingPendingBind | null {
  try {
    const raw = sessionStorage.getItem(PENDING_KEY)?.trim()
    if (!raw) return null
    const p = JSON.parse(raw) as AgentOnboardingPendingBind
    if (!p || typeof p.apiKey !== 'string' || typeof p.apiSecret !== 'string' || typeof p.openapiRoot !== 'string') {
      return null
    }
    if (typeof p.subAccountId !== 'string' || !p.subAccountId.trim()) {
      return null
    }
    return p
  } catch {
    return null
  }
}

export function clearAgentOnboardingPendingBind(): void {
  try {
    sessionStorage.removeItem(PENDING_KEY)
  } catch {
    /* ignore */
  }
}

export function saveAgentOnboardingBindResult(s: AgentOnboardingBindResult): void {
  try {
    sessionStorage.setItem(RESULT_KEY, JSON.stringify(s))
  } catch {
    /* ignore */
  }
}

export function readAgentOnboardingBindResult(): AgentOnboardingBindResult | null {
  try {
    const raw = sessionStorage.getItem(RESULT_KEY)?.trim()
    if (!raw) return null
    return JSON.parse(raw) as AgentOnboardingBindResult
  } catch {
    return null
  }
}

export function clearAgentOnboardingBindResult(): void {
  try {
    sessionStorage.removeItem(RESULT_KEY)
  } catch {
    /* ignore */
  }
}

/** 用户点「重新配置」或异常收口：清空多页 onboarding 会话态 */
export function clearAgentOnboardingFlowSession(): void {
  clearAgentOnboardingPendingBind()
  clearAgentOnboardingBindResult()
}
