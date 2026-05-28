// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: binding 摘要含横切 clarify / output 槽（pp-* · FE_HANDOFF 2026-05-27）
// 作者: 杨永的Agent
// 日期: 2026-05-18
// 修改功能: Prompt 快照列/详情摘要（promptPackVersion · resolvedPromptBinding 关键键 · FE_HANDOFF 2026-05-18）

/** 列表/协查表格：已发布 Prompt 包版本文案 */
export function formatPromptPackVersionLabel(v: string | null | undefined): string {
  if (v == null || String(v).trim() === '') return '—'
  return `v${String(v).trim()}`
}

function slotBrief(o: Record<string, unknown>, idKey: string, verKey: string, label: string): string | null {
  const id = typeof o[idKey] === 'string' ? o[idKey].trim() : ''
  const ver = typeof o[verKey] === 'string' ? o[verKey].trim() : ''
  if (!id && !ver) return null
  const tail = ver ? `@v${ver}` : ''
  return `${label}:${id || '—'}${tail}`
}

/** 协查可读一行：system / safety / 场景策略（同源 effective 快照） */
export function summarizeTradingPromptBinding(b: unknown): string {
  if (b == null || typeof b !== 'object') return '—'
  const o = b as Record<string, unknown>
  const slots = [
    slotBrief(o, 'systemPromptPackId', 'systemPromptPackVersion', 'sys'),
    slotBrief(o, 'safetyPromptPackId', 'safetyPromptPackVersion', 'safety'),
    slotBrief(o, 'tradingPromptPackId', 'tradingPromptPackVersion', 'strategy'),
    slotBrief(o, 'runtimeClarifyPromptPackId', 'runtimeClarifyPromptPackVersion', 'clarify'),
    slotBrief(o, 'runtimeOutputContractPromptPackId', 'runtimeOutputContractPromptPackVersion', 'output'),
  ].filter((s): s is string => Boolean(s))
  return slots.length ? slots.join(' · ') : '—'
}
