// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: Admin AI 网关策略 UI — NLU / Telegram narrate 字段元数据（feature 2026-05-27--admin-ai-settings-gateway-ui）

/** 与后端 `TELEGRAM_LLM_NARRATE_SCENARIO_KEYS` 一致 */
export type TelegramLlmNarrateKey =
  | 'readMarketTicker'
  | 'readMarketDepth'
  | 'readMarketTrades'
  | 'readAccountBalance'
  | 'wealthHoldingsRead'
  | 'spotFlashConfirm'
  | 'spotLimitConfirm'
  | 'futuresMarketConfirm'
  | 'futuresLimitConfirm'

export const TELEGRAM_LLM_NARRATE_KEYS: readonly TelegramLlmNarrateKey[] = [
  'readMarketTicker',
  'readMarketDepth',
  'readMarketTrades',
  'readAccountBalance',
  'wealthHoldingsRead',
  'spotFlashConfirm',
  'spotLimitConfirm',
  'futuresMarketConfirm',
  'futuresLimitConfirm',
] as const

export type NarrateFieldGroup = 'readonly' | 'type-a'

export interface NarrateFieldMeta {
  key: TelegramLlmNarrateKey
  label: string
  group: NarrateFieldGroup
  envVar: string
}

function narrateEnvVar(adminField: TelegramLlmNarrateKey): string {
  const suffix = adminField.replace(/([A-Z])/g, '_$1').toUpperCase()
  return `CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_${suffix}`
}

export const INTENT_NLU_ENV_VAR = 'CHAINUP_AGENT_INTENT_NLU_USE_LLM'
export const INTENT_CLARIFY_ENV_VAR = 'CHAINUP_AGENT_INTENT_CLARIFY_USE_LLM'

export const NARRATE_FIELD_METAS: readonly NarrateFieldMeta[] = [
  { key: 'readMarketTicker', label: '行情 · 最新价', group: 'readonly', envVar: narrateEnvVar('readMarketTicker') },
  { key: 'readMarketDepth', label: '行情 · 深度', group: 'readonly', envVar: narrateEnvVar('readMarketDepth') },
  { key: 'readMarketTrades', label: '行情 · 成交', group: 'readonly', envVar: narrateEnvVar('readMarketTrades') },
  { key: 'readAccountBalance', label: '账户余额', group: 'readonly', envVar: narrateEnvVar('readAccountBalance') },
  { key: 'wealthHoldingsRead', label: '理财持仓', group: 'readonly', envVar: narrateEnvVar('wealthHoldingsRead') },
  { key: 'spotFlashConfirm', label: '现货闪兑 · 确认前叙述', group: 'type-a', envVar: narrateEnvVar('spotFlashConfirm') },
  { key: 'spotLimitConfirm', label: '现货限价 · 确认前叙述', group: 'type-a', envVar: narrateEnvVar('spotLimitConfirm') },
  { key: 'futuresMarketConfirm', label: '合约市价 · 确认前叙述', group: 'type-a', envVar: narrateEnvVar('futuresMarketConfirm') },
  { key: 'futuresLimitConfirm', label: '合约限价 · 确认前叙述', group: 'type-a', envVar: narrateEnvVar('futuresLimitConfirm') },
]

export const NARRATE_READONLY_FIELDS = NARRATE_FIELD_METAS.filter((m) => m.group === 'readonly')
export const NARRATE_TYPE_A_FIELDS = NARRATE_FIELD_METAS.filter((m) => m.group === 'type-a')

export function emptyTelegramLlmNarrate(): Record<TelegramLlmNarrateKey, boolean> {
  return Object.fromEntries(TELEGRAM_LLM_NARRATE_KEYS.map((k) => [k, false])) as Record<
    TelegramLlmNarrateKey,
    boolean
  >
}

export function mergeTelegramLlmNarrateFromDefaults(
  raw: unknown,
): Record<TelegramLlmNarrateKey, boolean> {
  const base = emptyTelegramLlmNarrate()
  if (!raw || typeof raw !== 'object') return base
  const src = raw as Record<string, unknown>
  for (const key of TELEGRAM_LLM_NARRATE_KEYS) {
    base[key] = src[key] === true
  }
  return base
}
