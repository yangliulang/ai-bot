/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-22
 * 修改功能: Toast 状态元数据（图标键、无障碍文案、色调 class）
 */

import type { AdminToastTone } from '@/shared/lib/admin-toast'

export type AdminToastIconKey = 'check-circle' | 'x-circle' | 'information-circle'

export const ADMIN_TOAST_TONE_ICON: Record<AdminToastTone, AdminToastIconKey> = {
  success: 'check-circle',
  error: 'x-circle',
  info: 'information-circle',
}

export function adminToastToneLabel(tone: AdminToastTone): string {
  switch (tone) {
    case 'success':
      return '成功'
    case 'error':
      return '失败'
    default:
      return '提示'
  }
}

export type AdminToastToneVisual = {
  surface: string
  iconWrap: string
  iconColor: string
  message: string
}

export const ADMIN_TOAST_TONE_VISUAL: Record<AdminToastTone, AdminToastToneVisual> = {
  success: {
    surface:
      'border-emerald-500/30 bg-slate-950/92 text-slate-100 shadow-[0_16px_48px_-16px_rgba(0,0,0,0.75),inset_0_1px_0_0_rgba(255,255,255,0.06)]',
    iconWrap: 'bg-emerald-500/15 ring-1 ring-emerald-500/25',
    iconColor: 'text-emerald-400',
    message: 'text-slate-100',
  },
  error: {
    surface:
      'border-rose-500/30 bg-slate-950/92 text-slate-100 shadow-[0_16px_48px_-16px_rgba(0,0,0,0.75),inset_0_1px_0_0_rgba(255,255,255,0.06)]',
    iconWrap: 'bg-rose-500/15 ring-1 ring-rose-500/25',
    iconColor: 'text-rose-400',
    message: 'text-slate-100',
  },
  info: {
    surface:
      'border-sky-500/30 bg-slate-950/92 text-slate-100 shadow-[0_16px_48px_-16px_rgba(0,0,0,0.75),inset_0_1px_0_0_rgba(255,255,255,0.06)]',
    iconWrap: 'bg-sky-500/15 ring-1 ring-sky-500/25',
    iconColor: 'text-sky-400',
    message: 'text-slate-100',
  },
}
