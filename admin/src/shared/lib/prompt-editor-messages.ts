/**
 * Prompt 编辑器：messages[] 与 Markdown 正文互转、占位符与发布校验
 *
 * 作者: 杨永的Agent
 * 日期: 2026-05-19
 * 修改功能: 对齐原型编辑器 workbench（单正文编辑 · OpenAI messages PATCH）
 */

import type { PromptPackDetail } from '@/shared/api/admin-prompt-packs'

const PROMPT_BODY_MAX_BYTES = 256 * 1024

export function approximateTokensFromUtf8(text: string): number {
  const t = text.trim()
  if (!t.length) return 0
  return Math.max(1, Math.ceil(Array.from(t).length / 3.2))
}

export function extractPlaceholderKeys(markdown: string): string[] {
  const keys: string[] = []
  const re = /\{\{\s*([a-zA-Z0-9_.-]+)\s*\}\}/g
  let m: RegExpExecArray | null
  while ((m = re.exec(markdown))) {
    const key = m[1]
    if (typeof key === 'string' && key.length > 0) keys.push(key)
  }
  return keys.sort((a, b) => a.localeCompare(b))
}

export function serverBodyMarkdown(d: {
  bodyMarkdown?: string | null
  messages: Record<string, unknown>[]
}): string {
  if (typeof d.bodyMarkdown === 'string') return d.bodyMarkdown
  return messagesToEditorBody(d.messages)
}

export function messagesToEditorBody(messages: Record<string, unknown>[]): string {
  if (!messages.length) return ''
  const sysIdx = messages.findIndex((m) => m.role === 'system')
  const idx = sysIdx >= 0 ? sysIdx : 0
  const row = messages[idx]
  if (row && typeof row.content === 'string') return row.content
  return ''
}

export function editorBodyToMessages(
  body: string,
  prior: Record<string, unknown>[],
): Record<string, unknown>[] {
  if (!prior.length) return [{ role: 'system', content: body }]
  const sysIdx = prior.findIndex((m) => m.role === 'system')
  const idx = sysIdx >= 0 ? sysIdx : 0
  return prior.map((m, i) => (i === idx ? { ...m, content: body } : { ...m }))
}

export interface PromptWorkbenchSnapshot {
  packTitle: string
  body: string
  variableSchemaRaw: string
}

export function serializeWorkbench(snapshot: PromptWorkbenchSnapshot): string {
  return JSON.stringify(snapshot)
}

export function promptGovernancePublicationLabel(lifecycle: string): {
  zh: string
  badgeClass: string
} {
  const u = (lifecycle || '').toUpperCase()
  if (u === 'DRAFT') return { zh: '草稿', badgeClass: 'border-sky-600/45 bg-sky-950/30 text-sky-200/95' }
  if (u === 'PUBLISHED') return { zh: '已发布', badgeClass: 'border-emerald-600/45 bg-emerald-950/30 text-emerald-200/95' }
  if (u === 'LOCKED') return { zh: '已发布（冻结）', badgeClass: 'border-cyan-700/45 bg-cyan-950/25 text-cyan-200/90' }
  if (u === 'DEPRECATED' || u === 'DISABLED') {
    return { zh: '已停用', badgeClass: 'border-slate-600 bg-slate-800/50 text-slate-400' }
  }
  return { zh: lifecycle || '—', badgeClass: 'border-slate-700 bg-slate-900/40 text-slate-500' }
}

export function validatePublishPack(detail: PromptPackDetail, body: string): { ok: boolean; reasons: string[] } {
  const reasons: string[] = []
  const pt = String(detail.promptPackType ?? '').toUpperCase()
  const sid = (detail.scenarioId ?? '').trim()
  if ((pt === 'TRADING' || pt === 'ANALYSIS') && !sid) {
    reasons.push(
      '交易类或行情分析类提示词须已绑定生效场景（scenarioId）后方可发布；请从列表确认绑定或联系研发补齐。',
    )
  }
  const bytes = new TextEncoder().encode(JSON.stringify([{ role: 'system', content: body }])).length
  if (bytes > PROMPT_BODY_MAX_BYTES) {
    reasons.push(`正文过长（超过约 ${PROMPT_BODY_MAX_BYTES} 字节），请删减后再发布。`)
  }
  return { ok: reasons.length === 0, reasons }
}

export function packMessagesMutable(lifecycle: string): boolean {
  const u = (lifecycle || '').toUpperCase()
  return u !== 'LOCKED' && u !== 'DEPRECATED' && u !== 'DISABLED'
}

const SESSION_PREFIX = 'prompt-editor-cache:'

export function loadSessionEditorBody(promptPackId: string): string | null {
  try {
    const raw = sessionStorage.getItem(SESSION_PREFIX + promptPackId)
    if (!raw) return null
    const parsed = JSON.parse(raw) as { bodyMarkdown?: string }
    return typeof parsed.bodyMarkdown === 'string' ? parsed.bodyMarkdown : null
  } catch {
    return null
  }
}

export function saveSessionEditorBody(promptPackId: string, body: string): void {
  try {
    sessionStorage.setItem(SESSION_PREFIX + promptPackId, JSON.stringify({ bodyMarkdown: body }))
  } catch {
    /* quota */
  }
}

export function clearSessionEditorBody(promptPackId: string): void {
  try {
    sessionStorage.removeItem(SESSION_PREFIX + promptPackId)
  } catch {
    /* ignore */
  }
}
