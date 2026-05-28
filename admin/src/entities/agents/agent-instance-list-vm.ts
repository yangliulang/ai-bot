/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-16
 * 修改功能: 列表 VM 增加 **`exchangeSubAccountDisplay`**；关键字可命中交易所子账号 ID
 * 作者: 杨永的Agent
 * 日期: 2026-05-14
 * 修改功能: **`deriveAgentStateVm`** 等与后端 **`agentState`/`OPERATIONAL`** 对齐；掩码/阻断原因优先读 API
 * 日期: 2026-05-12
 * 修改功能: 将 admin API `AgentInstanceRow` 映射为实例列表展示 VM（对齐 product-doc 列表列字段）
 */
import type { AgentInstanceRow } from '@/shared/api/agent-instances'

export type AgentStateVm =
  | 'NORMAL'
  | 'GLOBAL_OFF'
  | 'BILLING_BLOCKED'
  | 'OPS_SUSPENDED'
  | 'MEMBERSHIP_BLOCKED'
  | 'AGENT_SUBACCOUNT_BLOCKED'

export type RuntimeStateVm = 'RUNNING' | 'PAUSED' | 'STOPPED' | 'STARTING' | 'ERROR'

export type SubAccountStatusVm = 'LINKED' | 'PENDING' | 'NONE'

/** 列表行视图模型（与原型 Instances 列一致；部分字段由绑定状态推导） */
export interface AgentInstanceListVm {
  raw: AgentInstanceRow
  instanceId: string
  /** Telegram numeric user id（tg_id），与协查 / Observability 关键字一致 */
  userId: string
  userEmailMasked: string
  /** 交易所子账号标识展示；未绑定为空占位 */
  exchangeSubAccountDisplay: string
  templateDisplayName: string
  templateVersion: string
  agentState: AgentStateVm
  runtimeState: RuntimeStateVm
  subAccountStatus: SubAccountStatusVm
  lastProductBlockReason: string
  lastActiveAt: string
  createdAt: string
}

const GATE_AGENT_STATES: AgentStateVm[] = [
  'NORMAL',
  'BILLING_BLOCKED',
  'GLOBAL_OFF',
  'OPS_SUSPENDED',
  'MEMBERSHIP_BLOCKED',
  'AGENT_SUBACCOUNT_BLOCKED',
]

const RUNTIME_STATES: RuntimeStateVm[] = ['RUNNING', 'PAUSED', 'STOPPED', 'STARTING', 'ERROR']

/** 列表/详情共用：附录 A 门禁枚举优先，否则按绑定推导 */
export function deriveAgentStateVm(r: AgentInstanceRow): AgentStateVm {
  const api = r.agentState?.trim()
  if (api && (GATE_AGENT_STATES as readonly string[]).includes(api)) {
    return api as AgentStateVm
  }
  return r.tradingApiBindingStatus === 'BOUND' ? 'NORMAL' : 'AGENT_SUBACCOUNT_BLOCKED'
}

export function deriveRuntimeStateVm(r: AgentInstanceRow): RuntimeStateVm {
  const api = r.runtimeState?.trim()
  if (api && (RUNTIME_STATES as readonly string[]).includes(api)) {
    return api as RuntimeStateVm
  }
  return 'RUNNING'
}

export function deriveSubAccountStatusVm(r: AgentInstanceRow): SubAccountStatusVm {
  const s = r.subAccountStatus
  if (s === 'LINKED' || s === 'NONE' || s === 'PENDING') return s
  const ex = r.exchangeSubAccountUserId
  return ex != null && String(ex).trim() !== '' ? 'LINKED' : 'NONE'
}

export function deriveLastProductBlockReason(r: AgentInstanceRow): string {
  const raw = r.lastProductBlockReason?.trim()
  if (raw) return raw
  return r.tradingApiBindingStatus === 'BOUND' ? '—' : '交易 API 未绑定'
}

export function deriveUserEmailMasked(r: AgentInstanceRow): string {
  const m = r.userEmailMasked?.trim()
  if (m && m !== '—') return m
  return r.tgUsername ? `@${r.tgUsername}` : `Telegram · ${r.telegramUserId}`
}

export function deriveExchangeSubAccountDisplay(r: AgentInstanceRow): string {
  const ex = r.exchangeSubAccountUserId?.trim()
  return ex && ex.length > 0 ? ex : '—'
}

export function mapAgentRowToListVm(r: AgentInstanceRow): AgentInstanceListVm {
  const td = r.templateDisplayName?.trim() || r.templateId
  return {
    raw: r,
    instanceId: r.instanceId,
    userId: r.telegramUserId,
    userEmailMasked: deriveUserEmailMasked(r),
    exchangeSubAccountDisplay: deriveExchangeSubAccountDisplay(r),
    templateDisplayName: td,
    templateVersion: r.templateVersion,
    agentState: deriveAgentStateVm(r),
    runtimeState: deriveRuntimeStateVm(r),
    subAccountStatus: deriveSubAccountStatusVm(r),
    lastProductBlockReason: deriveLastProductBlockReason(r),
    lastActiveAt: r.lastActiveAt,
    createdAt: r.createdAt,
  }
}

/** 关键字 + 门禁 + 运行态（与 product-doc instanceListFilters 行为一致） */
export function filterInstanceListVm(
  rows: AgentInstanceListVm[],
  keyword: string,
  agentState: string,
  runtimeState: string,
): AgentInstanceListVm[] {
  const k = keyword.trim().toLowerCase()
  return rows.filter((i) => {
    if (k) {
      const hitUid = i.userId.toLowerCase().includes(k)
      const hitMail = i.userEmailMasked.toLowerCase().includes(k)
      const hitInst = i.instanceId.toLowerCase().includes(k)
      const hitExSub = (i.raw.exchangeSubAccountUserId?.trim().toLowerCase() ?? '').includes(k)
      const hitMaster = (i.raw.userId?.trim().toLowerCase() ?? '').includes(k)
      if (!hitUid && !hitMail && !hitInst && !hitExSub && !hitMaster) return false
    }
    if (agentState !== 'all' && i.agentState !== agentState) return false
    if (runtimeState !== 'all' && i.runtimeState !== runtimeState) return false
    return true
  })
}
