// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: 意图裁决 plan 展示文案（S11 clarify · policyCodes · nextStep）

import type { AgentIntentPlanNextStep } from '@/shared/api/agent-runtime'

const NEXT_STEP_ZH: Record<AgentIntentPlanNextStep, string> = {
  CLARIFY: '澄清（CLARIFY）',
  ROUTE_READ_SKILL: '只读技能路由',
  ROUTE_CHAT_FAQ: '闲聊 FAQ',
  CONFIRM_TYPE_A: 'Type-A 确认',
  RESOLVE_FLASH_NOTIONAL: '闪兑名义解析（读余额）',
  RESOLVE_TRADE_NOTIONAL: '交易名义解析（读余额）',
  EXECUTE_SPOT_CANCEL: '现货撤单',
  EXECUTE_FUTURES_CANCEL: '合约撤单',
  BLOCKED_FEATURE: '功能阻断',
  STUB_NOT_EXECUTABLE: '占位不可执行',
  UNKNOWN: '未知',
}

const POLICY_CODE_ZH: Record<string, string> = {
  QUOTE_PAIR_NOT_FROZEN: '交易对未冻结，需确认计价币种',
  TRADE_NOTIONAL_PENDING: '名义金额待澄清',
  FUTURES_NOMINAL_AMBIGUOUS: '合约名义/保证金歧义',
  SLOT_TRADE_INCOMPLETE: '交易槽位不完整',
  FR_AO02_AMBIGUOUS: '意图歧义',
}

export function zhIntentPlanNextStep(step: string | null | undefined): string {
  const k = (step ?? '').trim() as AgentIntentPlanNextStep
  if (!k) return '—'
  return NEXT_STEP_ZH[k] ?? k
}

export function zhPolicyCode(code: string): string {
  const c = code.trim()
  if (!c) return '—'
  const hint = POLICY_CODE_ZH[c]
  return hint ? `${c} · ${hint}` : c
}

export function isNotionalResolveStep(step: string | null | undefined): boolean {
  const s = (step ?? '').trim()
  return s === 'RESOLVE_TRADE_NOTIONAL' || s === 'RESOLVE_FLASH_NOTIONAL'
}
