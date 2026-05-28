// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: Prompt 拼装追溯 · binding 解析 · 时间线 skillSpecRead（对齐 SC-PM-22 / FE_HANDOFF 2026-05-26）

import type { ResolvedPromptBinding } from '@/shared/api/admin-prompt-packs'
import type { ObservabilityTimelineItem } from '@/shared/api/admin-observability'

export const PROMPT_BINDING_RESOLVED_EVENT = 'agent.prompt.binding_resolved' as const
export const SKILL_SPEC_READ_EVENT = 'agent.skill.spec_read' as const

export const PROMPT_ASSEMBLY_LAYER = {
  base: '基础',
  ux: '体验',
  scenario: '场景',
  analysis: '分析',
  runtime: '运行时',
  output: '输出',
} as const

export type PromptAssemblyLayerRow = {
  layer: string
  source: string
  promptPackId?: string
  promptPackVersion?: string | null
}

const ANALYSIS_PACK_ID = 'pp-analysis-core'

function asBinding(raw: unknown): ResolvedPromptBinding | null {
  if (raw == null || typeof raw !== 'object') return null
  return raw as ResolvedPromptBinding
}

function formatPackRef(id: string | null | undefined, version: string | null | undefined): string {
  const pid = (id ?? '').trim()
  if (!pid) return '—'
  const ver = (version ?? '').trim()
  return ver ? `${pid}@v${ver}` : pid
}

function formatOutputLayerSource(binding: ResolvedPromptBinding): string {
  const base = formatPackRef(
    binding.runtimeOutputContractPromptPackId,
    binding.runtimeOutputContractPromptPackVersion,
  )
  const extras = [
    binding.placeholderDenylistRevision
      ? `占位符闸 ${binding.placeholderDenylistRevision}`
      : null,
    binding.fewShotDigest ? `示例集摘要 ${binding.fewShotDigest}` : null,
  ]
    .filter(Boolean)
    .join(' · ')
  return extras ? `${base} · ${extras}` : base
}

/** 读侧 / 统一分析包 → 分析槽 */
export function isAnalysisStrategyBinding(binding: ResolvedPromptBinding): boolean {
  if (binding.tradingPromptPackId === ANALYSIS_PACK_ID) return true
  const sid = (binding.scenarioId ?? '').trim()
  if (!sid) return false
  if (
    sid.startsWith('read.') ||
    sid.startsWith('market.read_') ||
    sid.startsWith('research.') ||
    sid.startsWith('monitoring.') ||
    sid.startsWith('portfolio.') ||
    sid.startsWith('orders.read_') ||
    sid.startsWith('futures.read_')
  ) {
    return true
  }
  return sid === 'wealth.holdings_read'
}

/** `ResolvedPromptBinding` → 运营可读拼装层 */
export function bindingToAssemblyLayers(binding: ResolvedPromptBinding): PromptAssemblyLayerRow[] {
  const rows: PromptAssemblyLayerRow[] = [
    {
      layer: PROMPT_ASSEMBLY_LAYER.base,
      source: formatPackRef(binding.systemPromptPackId, binding.systemPromptPackVersion),
      promptPackId: binding.systemPromptPackId ?? undefined,
      promptPackVersion: binding.systemPromptPackVersion,
    },
    {
      layer: PROMPT_ASSEMBLY_LAYER.ux,
      source: formatPackRef(binding.safetyPromptPackId, binding.safetyPromptPackVersion),
      promptPackId: binding.safetyPromptPackId ?? undefined,
      promptPackVersion: binding.safetyPromptPackVersion,
    },
  ]

  if (binding.tradingPromptPackId) {
    rows.push({
      layer: isAnalysisStrategyBinding(binding)
        ? PROMPT_ASSEMBLY_LAYER.analysis
        : PROMPT_ASSEMBLY_LAYER.scenario,
      source: formatPackRef(binding.tradingPromptPackId, binding.tradingPromptPackVersion),
      promptPackId: binding.tradingPromptPackId,
      promptPackVersion: binding.tradingPromptPackVersion,
    })
  }

  rows.push(
    {
      layer: PROMPT_ASSEMBLY_LAYER.runtime,
      source: formatPackRef(
        binding.runtimeClarifyPromptPackId,
        binding.runtimeClarifyPromptPackVersion,
      ),
      promptPackId: binding.runtimeClarifyPromptPackId ?? undefined,
      promptPackVersion: binding.runtimeClarifyPromptPackVersion,
    },
    {
      layer: PROMPT_ASSEMBLY_LAYER.output,
      source: formatOutputLayerSource(binding),
      promptPackId: binding.runtimeOutputContractPromptPackId ?? undefined,
      promptPackVersion: binding.runtimeOutputContractPromptPackVersion,
    },
  )

  return rows
}

export function parseBindingFromTimeline(
  items: ObservabilityTimelineItem[] | undefined,
): ResolvedPromptBinding | null {
  if (!items?.length) return null
  for (const ev of items) {
    const direct = asBinding(ev.summary.promptBindingResolved ?? ev.summary.resolvedPromptBinding)
    if (
      direct &&
      (direct.systemPromptPackId || direct.safetyPromptPackId || direct.tradingPromptPackId)
    ) {
      return direct
    }
  }
  return null
}

export function resolvePromptBindingForExecution(params: {
  scenarioId?: string | null
  resolvedPromptBinding?: unknown
  timelineItems?: ObservabilityTimelineItem[]
}): ResolvedPromptBinding | null {
  const direct = asBinding(params.resolvedPromptBinding)
  if (
    direct &&
    (direct.systemPromptPackId || direct.safetyPromptPackId || direct.tradingPromptPackId)
  ) {
    if (!direct.scenarioId?.trim() && params.scenarioId?.trim()) {
      return { ...direct, scenarioId: params.scenarioId.trim() }
    }
    return direct
  }
  const fromTimeline = parseBindingFromTimeline(params.timelineItems)
  if (fromTimeline) {
    if (!fromTimeline.scenarioId?.trim() && params.scenarioId?.trim()) {
      return { ...fromTimeline, scenarioId: params.scenarioId.trim() }
    }
    return fromTimeline
  }
  return direct
}

export interface SkillSpecReadView {
  skillId: string
  skillSpecVersion: string
  specDigest?: string | null
  phase?: string | null
}

export function parseSkillSpecReadFromTimeline(
  items: ObservabilityTimelineItem[] | undefined,
): SkillSpecReadView | null {
  if (!items?.length) return null
  for (const ev of items) {
    const raw = ev.summary.skillSpecRead
    if (raw != null && typeof raw === 'object') {
      const o = raw as Record<string, unknown>
      const skillId = typeof o.skillId === 'string' ? o.skillId.trim() : ''
      const skillSpecVersion =
        typeof o.skillSpecVersion === 'string' ? o.skillSpecVersion.trim() : ''
      if (skillId) {
        return {
          skillId,
          skillSpecVersion: skillSpecVersion || '—',
          specDigest: typeof o.specDigest === 'string' ? o.specDigest : null,
          phase: typeof o.phase === 'string' ? o.phase : null,
        }
      }
    }
    if (ev.eventName !== SKILL_SPEC_READ_EVENT) continue
    const skillId =
      typeof ev.summary.skillId === 'string'
        ? ev.summary.skillId.trim()
        : ''
    const skillSpecVersion =
      typeof ev.summary.skillSpecVersion === 'string'
        ? ev.summary.skillSpecVersion.trim()
        : ''
    if (skillId && skillSpecVersion) {
      return {
        skillId,
        skillSpecVersion,
        specDigest:
          typeof ev.summary.specDigest === 'string' ? ev.summary.specDigest : null,
      }
    }
  }
  return null
}
