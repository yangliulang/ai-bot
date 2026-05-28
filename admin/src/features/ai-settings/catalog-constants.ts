/**
 * AI Settings · 厂商目录交互常量（对齐 product-doc `/ai-settings` Demo）
 *
 * 作者: 杨永的Agent
 * 日期: 2026-05-19
 * 修改功能: 接入底座预置、默认 Base URL、运行时下拉过滤规则
 */

export type LlmVendorCatalogKind = 'openai' | 'anthropic' | 'deepseek' | 'none'

export type LlmHealthStatus = 'healthy' | 'degraded' | 'unknown'

export const LLM_VENDOR_CATALOG_OPTIONS: { value: LlmVendorCatalogKind; label: string }[] = [
  { value: 'openai', label: 'OpenAI' },
  { value: 'anthropic', label: 'Anthropic（Claude）' },
  { value: 'deepseek', label: 'DeepSeek' },
  { value: 'none', label: '暂无预置模型目录（自定义底座）' },
]

export const LLM_VENDOR_CATALOG_LABELS: Record<LlmVendorCatalogKind, string> = {
  openai: 'OpenAI',
  anthropic: 'Anthropic（Claude）',
  deepseek: 'DeepSeek',
  none: '暂无预置模型目录',
}

export const DEFAULT_BASE_URL_BY_CATALOG: Record<Exclude<LlmVendorCatalogKind, 'none'>, string> = {
  openai: 'https://api.openai.com/v1',
  anthropic: 'https://api.anthropic.com',
  deepseek: 'https://api.deepseek.com/v1',
}

export type ModelPresetEntry = {
  modelId: string
  displayLabel: string
  contextWindow: number
}

export const LLM_MODEL_PRESETS: Record<Exclude<LlmVendorCatalogKind, 'none'>, ModelPresetEntry[]> = {
  openai: [
    { modelId: 'gpt-4.1', displayLabel: 'GPT-4.1', contextWindow: 1_047_576 },
    { modelId: 'gpt-4.1-mini', displayLabel: 'GPT-4.1 Mini', contextWindow: 1_047_576 },
    { modelId: 'gpt-4o', displayLabel: 'GPT-4o', contextWindow: 128_000 },
  ],
  anthropic: [
    { modelId: 'claude-3-5-sonnet-20241022', displayLabel: 'Claude 3.5 Sonnet', contextWindow: 200_000 },
    { modelId: 'claude-3-haiku-20240307', displayLabel: 'Claude 3 Haiku', contextWindow: 200_000 },
  ],
  deepseek: [
    { modelId: 'deepseek-chat', displayLabel: 'DeepSeek Chat', contextWindow: 128_000 },
    { modelId: 'deepseek-reasoner', displayLabel: 'DeepSeek Reasoner', contextWindow: 128_000 },
  ],
}

const PROVIDER_ID_PATTERN = /^[a-z][a-z0-9_-]{0,63}$/

export function suggestProviderId(displayName: string, existingIds: readonly string[]): string {
  const taken = new Set(existingIds)
  let slug = displayName
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-zA-Z0-9\s_-]/g, '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, '-')
    .replace(/_+/g, '-')
    .replace(/^-+|-+$/g, '')

  while (slug.length && !/[a-z]/.test(slug.charAt(0))) {
    slug = slug.slice(1)
  }

  let base = slug.length ? slug : 'vendor'
  if (!PROVIDER_ID_PATTERN.test(base)) {
    base = 'vendor'
  }
  base = base.slice(0, 48)

  let candidate = base
  let n = 0
  while (taken.has(candidate)) {
    n += 1
    candidate = `${base}-${n}`
    if (!PROVIDER_ID_PATTERN.test(candidate)) {
      candidate = `vendor-${n}`
    }
    if (n > 500) {
      candidate = `vendor-${Date.now()}`
      break
    }
  }
  return candidate
}

export function healthStatusTag(h: LlmHealthStatus): { label: string; className: string } {
  if (h === 'healthy') {
    return {
      label: '健康',
      className: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-200',
    }
  }
  if (h === 'degraded') {
    return {
      label: '降级 / 待确认',
      className: 'border-amber-500/40 bg-amber-500/10 text-amber-200',
    }
  }
  return {
    label: '未探测',
    className: 'border-slate-600 bg-slate-800/50 text-slate-400',
  }
}

export function probeResultToHealth(probeText: string | undefined): LlmHealthStatus {
  if (!probeText || probeText === '…') return 'unknown'
  if (probeText.startsWith('ok')) return 'healthy'
  if (probeText.startsWith('fail')) return 'degraded'
  return 'unknown'
}

export function getAddablePresetModels(
  catalogKind: LlmVendorCatalogKind,
  takenModelIds: Set<string>,
): ModelPresetEntry[] {
  if (catalogKind === 'none') return []
  return LLM_MODEL_PRESETS[catalogKind].filter((p) => !takenModelIds.has(p.modelId))
}
