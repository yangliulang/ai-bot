/**
 * 作者: Cursor Agent
 * 日期: 2026-05-26
 * 修改功能: 技能与工具 · 启用开关 localStorage（对齐 product-doc toolRegistryStorage）
 */

const STORAGE_KEY = 'chainup-admin-tool-registry-demo-v1'
const MAX_AUDIT = 80

export type RegistryEntryClass = 'A' | 'B' | 'C'

export interface ToolRegistryAuditEntry {
  at: string
  stableId: string
  entryClass: RegistryEntryClass
  enabled: boolean
  actor: string
}

export interface ToolRegistryStored {
  enabled: Record<string, boolean>
  audit: ToolRegistryAuditEntry[]
}

function defaultPayload(ids: string[], defaults: Record<string, boolean>): ToolRegistryStored {
  const enabled: Record<string, boolean> = {}
  for (const id of ids) {
    enabled[id] = defaults[id] ?? true
  }
  return { enabled, audit: [] }
}

export function loadToolRegistryState(
  allIds: string[],
  rowDefaults: Record<string, boolean>,
): ToolRegistryStored {
  if (typeof localStorage === 'undefined') {
    return defaultPayload(allIds, rowDefaults)
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return defaultPayload(allIds, rowDefaults)
    const parsed = JSON.parse(raw) as Partial<ToolRegistryStored>
    const merged: ToolRegistryStored = {
      enabled: { ...defaultPayload(allIds, rowDefaults).enabled },
      audit: Array.isArray(parsed.audit) ? parsed.audit.slice(-MAX_AUDIT) : [],
    }
    if (parsed.enabled && typeof parsed.enabled === 'object') {
      for (const id of allIds) {
        if (typeof parsed.enabled[id] === 'boolean') merged.enabled[id] = parsed.enabled[id]!
      }
    }
    return merged
  } catch {
    return defaultPayload(allIds, rowDefaults)
  }
}

export function persistToggle(params: {
  stableId: string
  entryClass: RegistryEntryClass
  enabled: boolean
  prev: ToolRegistryStored
}): ToolRegistryStored {
  const next: ToolRegistryStored = {
    enabled: { ...params.prev.enabled, [params.stableId]: params.enabled },
    audit: [
      ...params.prev.audit,
      {
        at: new Date().toISOString(),
        stableId: params.stableId,
        entryClass: params.entryClass,
        enabled: params.enabled,
        actor: 'demo-operator',
      },
    ].slice(-MAX_AUDIT),
  }
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
  }
  return next
}

export function resetToolRegistryDemo(
  allIds: string[],
  rowDefaults: Record<string, boolean>,
): ToolRegistryStored {
  const fresh = defaultPayload(allIds, rowDefaults)
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(fresh))
  }
  return fresh
}

export function isRowEnabled(
  stableId: string,
  defaultEnabled: boolean,
  store: ToolRegistryStored,
): boolean {
  return store.enabled[stableId] ?? defaultEnabled
}
