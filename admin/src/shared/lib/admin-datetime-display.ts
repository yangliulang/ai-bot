/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-15
 * 修改功能: 全局时点标签 **`(UTC+8)` / `(UTC)`**；顶栏仅 **UTC+8/UTC**；API 仍按 UTC 解析（BACKEND_SPEC §2.1）
 */
import { ref } from 'vue'

const STORAGE_KEY = 'chainup-admin-datetime-display-mode'

export type AdminDatetimeDisplayMode = 'ops_shanghai' | 'utc_compact'

/** 运营墙钟：与产品约定（FE_HANDOFF 建议固定上海） */
export const ADMIN_OPS_IANA_TIME_ZONE = 'Asia/Shanghai'
export const ADMIN_OPS_TIME_ZONE_LABEL = 'UTC+8'
export const ADMIN_UTC_DISPLAY_LABEL = 'UTC'

export const adminDatetimeDisplayModeRef = ref<AdminDatetimeDisplayMode>('ops_shanghai')

function readStoredMode(): AdminDatetimeDisplayMode {
  if (typeof sessionStorage === 'undefined') return 'ops_shanghai'
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (raw === 'utc_compact') return 'utc_compact'
  } catch {
    /* ignore */
  }
  return 'ops_shanghai'
}

adminDatetimeDisplayModeRef.value = readStoredMode()

function persistMode(mode: AdminDatetimeDisplayMode): void {
  try {
    sessionStorage.setItem(STORAGE_KEY, mode)
  } catch {
    /* ignore quota / private mode */
  }
}

export function toggleAdminDatetimeDisplayMode(): void {
  const next: AdminDatetimeDisplayMode =
    adminDatetimeDisplayModeRef.value === 'utc_compact' ? 'ops_shanghai' : 'utc_compact'
  adminDatetimeDisplayModeRef.value = next
  persistMode(next)
}

export function adminDatetimeModeButtonLabel(): string {
  return adminDatetimeDisplayModeRef.value === 'utc_compact'
    ? ADMIN_UTC_DISPLAY_LABEL
    : ADMIN_OPS_TIME_ZONE_LABEL
}

/** 列表头 / 说明用：`'(UTC+8)' | '(UTC)'` */
export function adminTimeZoneParenSuffix(): string {
  return adminDatetimeDisplayModeRef.value === 'utc_compact' ? '(UTC)' : '(UTC+8)'
}

/**
 * 若字符串无时区后缀，按契约视为 **UTC** 墙钟（避免被 `Date` 当作本地解析）。
 * 若仍无法解析，返回 `null`（调用方可展示「—」并向 /be 回报异常串）。
 */
export function parseApiInstantUtc(iso: string | null | undefined): Date | null {
  if (iso == null) return null
  const t = String(iso).trim()
  if (!t) return null

  const hasExplicitTz =
    /[zZ]$/.test(t) || /[+-]\d{2}:?\d{2}$/.test(t) || /[+-]\d{4}$/.test(t)

  let normalized = t
  if (!hasExplicitTz) {
    if (/^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}/.test(t)) {
      const asT = t.includes('T') ? t : t.replace(' ', 'T')
      normalized = asT.endsWith('Z') ? asT : `${asT}Z`
    }
  }

  const d = new Date(normalized)
  if (Number.isNaN(d.getTime())) return null
  return d
}

function formatOpsShanghai(d: Date): string {
  const parts = new Intl.DateTimeFormat('sv-SE', {
    timeZone: ADMIN_OPS_IANA_TIME_ZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(d)
  const g = (type: Intl.DateTimeFormatPartTypes) => parts.find((p) => p.type === type)?.value ?? ''
  const y = g('year')
  const mo = g('month')
  const da = g('day')
  const h = g('hour')
  const mi = g('minute')
  const s = g('second')
  if (!y || !mo || !da) return d.toISOString()
  return `${y}-${mo}-${da} ${h}:${mi}:${s}`
}

function formatUtcCompact(d: Date): string {
  return d.toISOString().slice(0, 19).replace('T', ' ')
}

/**
 * 展示 API 返回的时点（createdAt / updatedAt / ts / addedAt 等）。
 * 依赖全局 `adminDatetimeDisplayModeRef`：在组件模板中调用时会随模式切换而更新。
 */
export function formatAdminApiTime(iso: string | null | undefined): string {
  const d = parseApiInstantUtc(iso ?? '')
  if (!d) {
    const raw = iso == null ? '' : String(iso).trim()
    return raw ? `${raw}（无法解析）` : '—'
  }
  return adminDatetimeDisplayModeRef.value === 'utc_compact'
    ? formatUtcCompact(d)
    : formatOpsShanghai(d)
}
