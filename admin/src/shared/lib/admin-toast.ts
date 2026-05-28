// 作者: 杨永的Agent
// 日期: 2026-05-22
// 修改功能: **`adminNotifyManualRefresh`**：仅用户点击「刷新」时弹出 Toast
// 作者: 杨永的Agent
// 日期: 2026-05-22
// 修改功能: Admin 全局操作反馈 Toast（成功/失败/信息 · 替代页面内联 flash 文案）

import { readonly, ref } from 'vue'

import { AppError } from '@/shared/api/errors'

export type AdminToastTone = 'success' | 'error' | 'info'

export interface AdminToastItem {
  id: number
  tone: AdminToastTone
  message: string
}

const items = ref<AdminToastItem[]>([])
let seq = 0
const timers = new Map<number, ReturnType<typeof setTimeout>>()

const DEFAULT_DURATION_MS: Record<AdminToastTone, number> = {
  success: 2800,
  error: 4200,
  info: 2800,
}

function dismiss(id: number) {
  items.value = items.value.filter((t) => t.id !== id)
  const timer = timers.get(id)
  if (timer) {
    clearTimeout(timer)
    timers.delete(id)
  }
}

function push(message: string, tone: AdminToastTone, durationMs?: number) {
  const trimmed = message.trim()
  if (!trimmed) return
  const id = ++seq
  const ms = durationMs ?? DEFAULT_DURATION_MS[tone]
  items.value = [...items.value.slice(-4), { id, tone, message: trimmed }]
  timers.set(
    id,
    setTimeout(() => dismiss(id), ms),
  )
}

/** 只读队列，供 `AdminToastHost` 渲染 */
export const adminToastItems = readonly(items)

export function adminToastSuccess(message: string, durationMs?: number) {
  push(message, 'success', durationMs)
}

export function adminToastError(message: string, durationMs?: number) {
  push(message, 'error', durationMs)
}

export function adminToastInfo(message: string, durationMs?: number) {
  push(message, 'info', durationMs)
}

export function dismissAdminToast(id: number) {
  dismiss(id)
}

export function resolveAdminActionErrorMessage(err: unknown, fallback = '操作失败'): string {
  if (err instanceof AppError) return err.message
  if (err instanceof Error && err.message.trim()) return err.message
  return fallback
}

/**
 * 列表/页头「刷新」结果提示：首屏 `load`、路由联动等传 `false`；仅按钮点击传 `true`。
 */
export function adminNotifyManualRefresh(
  toastOnSuccess: boolean,
  outcome: { ok: boolean; successMessage: string; errorMessage?: string | null },
) {
  if (!toastOnSuccess) return
  if (outcome.ok) adminToastSuccess(outcome.successMessage)
  else if (outcome.errorMessage?.trim()) adminToastError(outcome.errorMessage.trim())
}
