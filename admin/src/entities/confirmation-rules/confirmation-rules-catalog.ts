// 作者: 杨永的Agent
// 日期: 2026-05-20
// 修改功能: 人工确认规则枚举、展示文案与格式化（对齐 product-doc confirmationRulesCatalog · FE_HANDOFF）

export type RiskLevel = 'low' | 'medium' | 'high'

export type RuleAction = 'force_confirm' | 'second_confirm' | 'otp_confirm' | 'block_auto_execute'

export type ScenarioKey =
  | 'spot'
  | 'futures'
  | 'convert'
  | 'wealth'
  | 'leverage'
  | 'transfer'
  | 'conditional_order'

export type TriggerFieldKey = 'nominal_usdt' | 'leverage' | 'operation_scope' | 'custom'

export type TriggerOpKey = 'gt' | 'gte' | 'lt' | 'lte' | 'eq' | 'contains'

export interface TriggerConditionRow {
  fieldKey: TriggerFieldKey
  operator: TriggerOpKey
  value: string
}

export interface ConfirmationRuleWriteBody {
  title: string
  summary: string
  riskLevel: RiskLevel
  triggerConditions: TriggerConditionRow[]
  scenarios: ScenarioKey[]
  action: RuleAction
  defaultEnabled: boolean
}

export const RISK_LEVEL_OPTIONS: { value: RiskLevel; label: string }[] = [
  { value: 'low', label: '低风险' },
  { value: 'medium', label: '中风险' },
  { value: 'high', label: '高风险' },
]

export const SCENARIO_OPTIONS: { value: ScenarioKey; label: string }[] = [
  { value: 'spot', label: '现货交易' },
  { value: 'futures', label: '合约交易' },
  { value: 'convert', label: '闪兑' },
  { value: 'wealth', label: '理财申购' },
  { value: 'leverage', label: '杠杆调整' },
  { value: 'transfer', label: '资金划转' },
  { value: 'conditional_order', label: '条件单/计划委托' },
]

export const TRIGGER_FIELD_OPTIONS: { value: TriggerFieldKey; label: string }[] = [
  { value: 'nominal_usdt', label: '名义本金（USDT 等值）' },
  { value: 'leverage', label: '杠杆（倍）' },
  { value: 'operation_scope', label: '操作范围' },
  { value: 'custom', label: '其他' },
]

export const TRIGGER_OPERATOR_OPTIONS: { value: TriggerOpKey; label: string }[] = [
  { value: 'gt', label: '>' },
  { value: 'gte', label: '≥' },
  { value: 'lt', label: '<' },
  { value: 'lte', label: '≤' },
  { value: 'eq', label: '=' },
  { value: 'contains', label: '包含' },
]

export const RULE_ACTION_OPTIONS: { value: RuleAction; label: string; hint: string }[] = [
  { value: 'force_confirm', label: '强制确认', hint: '须先完成摘单确认，再继续业务执行' },
  { value: 'second_confirm', label: '二次确认', hint: '在常规确认外再追加一轮风险提示与确认' },
  { value: 'otp_confirm', label: 'OTP 确认', hint: '须通过一次性口令等第二因素确认' },
  {
    value: 'block_auto_execute',
    label: '禁止自动执行',
    hint: '命中后不得由系统自动落单，仅人工或显式确认后放行',
  },
]

export const RULE_ACTION_META: Record<
  RuleAction,
  { label: string; badgeClass: string; hint: string }
> = {
  force_confirm: {
    label: '强制确认',
    badgeClass: 'border-sky-500/35 bg-sky-500/10 text-sky-200',
    hint: RULE_ACTION_OPTIONS[0]!.hint,
  },
  second_confirm: {
    label: '二次确认',
    badgeClass: 'border-fuchsia-500/35 bg-fuchsia-500/10 text-fuchsia-200',
    hint: RULE_ACTION_OPTIONS[1]!.hint,
  },
  otp_confirm: {
    label: 'OTP 确认',
    badgeClass: 'border-violet-500/35 bg-violet-500/10 text-violet-200',
    hint: RULE_ACTION_OPTIONS[2]!.hint,
  },
  block_auto_execute: {
    label: '禁止自动执行',
    badgeClass: 'border-rose-500/35 bg-rose-500/10 text-rose-200',
    hint: RULE_ACTION_OPTIONS[3]!.hint,
  },
}

export function ruleActionNeedsStrongDisableGuard(action: RuleAction): boolean {
  return action === 'force_confirm' || action === 'block_auto_execute'
}

export function scenarioLabels(keys: ScenarioKey[]): string {
  const map = Object.fromEntries(SCENARIO_OPTIONS.map((o) => [o.value, o.label])) as Record<string, string>
  return keys.map((k) => map[k] ?? k).join(' · ')
}

export function operatorsForField(fieldKey: TriggerFieldKey): TriggerOpKey[] {
  if (fieldKey === 'nominal_usdt' || fieldKey === 'leverage') {
    return ['gt', 'gte', 'lt', 'lte', 'eq']
  }
  return ['contains', 'eq']
}

export function defaultOperatorForField(fieldKey: TriggerFieldKey): TriggerOpKey {
  return operatorsForField(fieldKey)[0] ?? 'eq'
}

export function formatTriggerLine(r: TriggerConditionRow): string {
  const fl = Object.fromEntries(TRIGGER_FIELD_OPTIONS.map((o) => [o.value, o.label])) as Record<string, string>
  const ol = Object.fromEntries(TRIGGER_OPERATOR_OPTIONS.map((o) => [o.value, o.label])) as Record<string, string>
  const field = fl[r.fieldKey] ?? r.fieldKey
  const op = ol[r.operator] ?? r.operator
  const val =
    r.fieldKey === 'leverage' && r.value && !String(r.value).toLowerCase().includes('x')
      ? `${r.value}x`
      : r.fieldKey === 'nominal_usdt' && r.value && !String(r.value).toUpperCase().includes('USDT')
        ? `${r.value} USDT`
        : r.value
  return `${field} ${op} ${val}`
}

export function formatTriggerSummary(rows: TriggerConditionRow[]): string {
  if (!rows.length) return '—'
  return rows.map(formatTriggerLine).join('；')
}

export function riskLevelBadgeClass(level: RiskLevel): string {
  if (level === 'low') return 'border-emerald-500/35 bg-emerald-500/10 text-emerald-200'
  if (level === 'medium') return 'border-amber-500/35 bg-amber-500/10 text-amber-200'
  return 'border-rose-500/35 bg-rose-500/10 text-rose-200'
}

export function riskLevelLabel(level: RiskLevel): string {
  return RISK_LEVEL_OPTIONS.find((o) => o.value === level)?.label ?? level
}

export function emptyTriggerCondition(): TriggerConditionRow {
  return { fieldKey: 'nominal_usdt', operator: 'gt', value: '' }
}
