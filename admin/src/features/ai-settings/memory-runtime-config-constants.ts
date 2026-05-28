// 作者: 杨永的Agent
// 日期: 2026-05-28
// 修改功能: MR-MEM-01 续 · 对齐 memory_runtime_settings 全键 + READ §2.3

import type { TradingAgentConfigValue } from '@/shared/api/admin-trading-agent-config'

export type MemoryConfigFieldKind = 'int' | 'float' | 'bool' | 'enum'

export type MemoryConfigSection = 'stm' | 'session' | 'read'

export interface MemoryRuntimeConfigFieldMeta {
  configKey: string
  envVar: string
  label: string
  kind: MemoryConfigFieldKind
  defaultValue: string | number | boolean
  enumOptions?: readonly string[]
  description: string
  section: MemoryConfigSection
  /** GlobalConfigBundle PATCH 已支持（热覆盖 Env） */
  bundleSupported: boolean
  min?: number
  max?: number
  step?: number
}

const ENV_PREFIX = 'CHAINUP_AGENT_'

function envVar(configKey: string): string {
  return `${ENV_PREFIX}${configKey}`
}

export const MEMORY_RUNTIME_CONFIG_FIELDS: readonly MemoryRuntimeConfigFieldMeta[] = [
  {
    configKey: 'STM_L0_MAX_TURNS',
    envVar: envVar('STM_L0_MAX_TURNS'),
    label: 'L0 近轮上限',
    kind: 'int',
    defaultValue: 10,
    min: 2,
    max: 50,
    description: 'L0 近轮 user+assistant 对上限；超界裁远端或压 rolling summary。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'STM_IDLE_RESUME_PROMPT_SEC',
    envVar: envVar('STM_IDLE_RESUME_PROMPT_SEC'),
    label: '写澄清空闲 stale 阈值',
    kind: 'int',
    defaultValue: 1800,
    min: 60,
    max: 86400,
    description: '写澄清/写 L1 空闲 ≥ 本值 → §14.6 默认 stale + Resume 门控（30min）。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'STM_IDLE_DEFAULT_POLICY',
    envVar: envVar('STM_IDLE_DEFAULT_POLICY'),
    label: '空闲默认策略',
    kind: 'enum',
    defaultValue: 'stale_prior_write',
    enumOptions: ['stale_prior_write', 'prompt_resume_or_new'],
    description: '默认 stale_prior_write；fallback 可弹 cl:resume/cl:new。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'RESUME_CLASSIFIER_MODE',
    envVar: envVar('RESUME_CLASSIFIER_MODE'),
    label: 'Resume 分类器模式',
    kind: 'enum',
    defaultValue: 'rules_then_llm',
    enumOptions: ['rules_only', 'rules_then_llm'],
    description: 'ambiguous 默认 new_intent；规则层明确续单 bypass 分类器。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'RESUME_CLASSIFIER_MIN_CONFIDENCE',
    envVar: envVar('RESUME_CLASSIFIER_MIN_CONFIDENCE'),
    label: 'Resume 最低置信度',
    kind: 'float',
    defaultValue: 0.75,
    min: 0,
    max: 1,
    step: 0.01,
    description: 'resume_prior_write 须 confidence ≥ 本值，否则降级 new_intent。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'WARM_EXECUTION_INDEX_TTL_SEC',
    envVar: envVar('WARM_EXECUTION_INDEX_TTL_SEC'),
    label: '温索引保留 TTL',
    kind: 'int',
    defaultValue: 86400,
    description: 'WarmExecutionEpisode 保留时长（24h）。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'STM_CLARIFY_SESSION_TTL_SEC',
    envVar: envVar('STM_CLARIFY_SESSION_TTL_SEC'),
    label: '写澄清 session TTL',
    kind: 'int',
    defaultValue: 900,
    min: 60,
    max: 7200,
    description: 'ClarifySessionSnapshot.expiresAt 默认 TTL（15min）；与 idle 先达者触发 stale。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'STM_SESSION_CLEAR_MODE',
    envVar: envVar('STM_SESSION_CLEAR_MODE'),
    label: 'STM 清空模式',
    kind: 'enum',
    defaultValue: 'in_place',
    enumOptions: ['in_place', 'rotate_session_id'],
    description: 'FR-STM01：原地清 L0/活跃 L1 或分配新 sessionId。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'STM_HOT_RECYCLE_SESSION_IDLE_SEC',
    envVar: envVar('STM_HOT_RECYCLE_SESSION_IDLE_SEC'),
    label: 'Session 热面回收',
    kind: 'int',
    defaultValue: 86400,
    description: 'session 空闲热面回收（24h）；与 STM_IDLE_RESUME_PROMPT_SEC 独立。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'STM_HOT_RECYCLE_EXECUTION_AFTER_TERMINAL_SEC',
    envVar: envVar('STM_HOT_RECYCLE_EXECUTION_AFTER_TERMINAL_SEC'),
    label: 'Execution 终局 L1 回收',
    kind: 'int',
    defaultValue: 7200,
    description: 'execution 终局后 L1 热回收（2h）。',
    section: 'stm',
    bundleSupported: true,
  },
  {
    configKey: 'SESSION_INBOUND_QUEUE_POLICY',
    envVar: envVar('SESSION_INBOUND_QUEUE_POLICY'),
    label: '入站队列策略',
    kind: 'enum',
    defaultValue: 'serial_per_session',
    enumOptions: ['serial_per_session', 'coalesce_latest', 'reject_while_busy'],
    description: 'per-session 串行 / 合并最新 / 忙时拒收。',
    section: 'session',
    bundleSupported: true,
  },
  {
    configKey: 'SESSION_INBOUND_QUEUE_MAX_DEPTH',
    envVar: envVar('SESSION_INBOUND_QUEUE_MAX_DEPTH'),
    label: '入站排队硬顶',
    kind: 'int',
    defaultValue: 3,
    min: 1,
    max: 20,
    description: '排队深度上限；超限须可观测丢弃/合并策略。',
    section: 'session',
    bundleSupported: true,
  },
  {
    configKey: 'SESSION_INBOUND_COALESCE_WINDOW_MS',
    envVar: envVar('SESSION_INBOUND_COALESCE_WINDOW_MS'),
    label: '合并窗口（ms）',
    kind: 'int',
    defaultValue: 800,
    description: '仅 coalesce_latest 生效。',
    section: 'session',
    bundleSupported: true,
  },
  {
    configKey: 'SESSION_BUSY_ACK_WITHIN_MS',
    envVar: envVar('SESSION_BUSY_ACK_WITHIN_MS'),
    label: '忙时 ack 时限（ms）',
    kind: 'int',
    defaultValue: 800,
    description: 'in-flight 内须 typing 或进度短句。',
    section: 'session',
    bundleSupported: true,
  },
  {
    configKey: 'SESSION_MAX_ACTIVE_WRITE_EXECUTIONS',
    envVar: envVar('SESSION_MAX_ACTIVE_WRITE_EXECUTIONS'),
    label: '在途写 execution 上限',
    kind: 'int',
    defaultValue: 1,
    min: 1,
    max: 3,
    description: '在途写 executionId 上限；与 Type A / clarify 优先级同窗。',
    section: 'session',
    bundleSupported: true,
  },
  {
    configKey: 'SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN',
    envVar: envVar('SESSION_BLOCK_NEW_WRITE_ON_UNKNOWN'),
    label: 'UNKNOWN 挡新写',
    kind: 'bool',
    defaultValue: true,
    description: 'unknown_pending 时挡新写起票（D-1 默认 ON）。',
    section: 'session',
    bundleSupported: true,
  },
  {
    configKey: 'READ_CLARIFY_SESSION_TTL_SEC',
    envVar: envVar('READ_CLARIFY_SESSION_TTL_SEC'),
    label: '只读澄清 session TTL',
    kind: 'int',
    defaultValue: 600,
    min: 60,
    max: 3600,
    description: 'ReadClarifySessionSnapshot.expiresAt；短于写澄清 TTL。',
    section: 'read',
    bundleSupported: true,
  },
  {
    configKey: 'READ_CLARIFY_MAX_TURNS',
    envVar: envVar('READ_CLARIFY_MAX_TURNS'),
    label: '只读澄清轮次软顶',
    kind: 'int',
    defaultValue: 2,
    min: 1,
    max: 5,
    description: '只读澄清轮次软顶；超限缩窄或拒答。',
    section: 'read',
    bundleSupported: true,
  },
] as const

export const STM_MEMORY_CONFIG_FIELDS = MEMORY_RUNTIME_CONFIG_FIELDS.filter((f) => f.section === 'stm')
export const SESSION_MEMORY_CONFIG_FIELDS = MEMORY_RUNTIME_CONFIG_FIELDS.filter(
  (f) => f.section === 'session',
)
export const READ_MEMORY_CONFIG_FIELDS = MEMORY_RUNTIME_CONFIG_FIELDS.filter((f) => f.section === 'read')

export function formatMemoryConfigDefault(meta: MemoryRuntimeConfigFieldMeta): string {
  if (meta.kind === 'bool') return meta.defaultValue ? 'true' : 'false'
  return String(meta.defaultValue)
}

export function coerceDraftValue(
  meta: MemoryRuntimeConfigFieldMeta,
  raw: string | number | boolean,
): TradingAgentConfigValue {
  if (meta.kind === 'bool') return Boolean(raw)
  if (meta.kind === 'float') return Number(raw)
  if (meta.kind === 'int') return Math.trunc(Number(raw))
  return String(raw)
}

export function valuesEqual(
  meta: MemoryRuntimeConfigFieldMeta,
  a: TradingAgentConfigValue | undefined,
  b: TradingAgentConfigValue | undefined,
): boolean {
  if (a === undefined || b === undefined) return a === b
  if (meta.kind === 'float') return Math.abs(Number(a) - Number(b)) < 1e-9
  if (meta.kind === 'bool') return Boolean(a) === Boolean(b)
  return String(a) === String(b)
}
