/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-15
 * 修改功能: `formatInstanceAt` 与全局 Admin 时点展示对齐（Asia/Shanghai 或 UTC 切换）
 * 作者: 杨永的Agent
 * 日期: 2026-05-14
 * 修改功能: **`OPERATIONAL`** 与 **`NORMAL`** 同为正向门禁色阶
 * 日期: 2026-05-12
 * 修改功能: 实例列表 Tag 色板（Tailwind 语义，对应 product-doc agentInstanceUi 色阶）
 */

import { formatAdminApiTime } from '@/shared/lib/admin-datetime-display'

export function agentStateTagClass(state: string): string {
  if (state === 'NORMAL' || state === 'OPERATIONAL') {
    return 'border-emerald-500/40 bg-emerald-500/15 text-emerald-200'
  }
  if (state === 'BILLING_BLOCKED' || state === 'MEMBERSHIP_BLOCKED') {
    return 'border-amber-500/40 bg-amber-500/15 text-amber-200'
  }
  if (state === 'GLOBAL_OFF' || state === 'OPS_SUSPENDED' || state === 'AGENT_SUBACCOUNT_BLOCKED') {
    return 'border-rose-500/40 bg-rose-500/15 text-rose-200'
  }
  return 'border-slate-600 bg-slate-800/80 text-slate-400'
}

export function runtimeStateTagClass(state: string): string {
  if (state === 'RUNNING') return 'border-emerald-500/40 bg-emerald-500/15 text-emerald-200'
  if (state === 'PAUSED') return 'border-amber-500/40 bg-amber-500/15 text-amber-200'
  if (state === 'STARTING') return 'border-sky-500/40 bg-sky-500/15 text-sky-200'
  if (state === 'ERROR') return 'border-rose-500/40 bg-rose-500/15 text-rose-200'
  return 'border-slate-600 bg-slate-800/80 text-slate-400'
}

export function formatInstanceAt(iso: string): string {
  return formatAdminApiTime(iso)
}
