/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-22
 * 修改功能: 控制台页头统一布局 token 与角标 tone class
 */

export type AdminPageHeaderBadgeTone =
  | 'violet'
  | 'sky'
  | 'emerald'
  | 'rose'
  | 'amber'
  | 'slate'

export type AdminPageHeaderBadge = {
  label: string
  tone?: AdminPageHeaderBadgeTone
}

export const ADMIN_PAGE_HEADER_ROOT_CLASS =
  'flex flex-col gap-4 border-b border-slate-800/80 pb-6 sm:flex-row sm:items-start sm:justify-between'

export const ADMIN_PAGE_HEADER_ROOT_COMPACT_CLASS =
  'flex flex-col gap-3 border-b border-slate-800/80 pb-5 sm:flex-row sm:items-start sm:justify-between'

export const ADMIN_PAGE_HEADER_ACTIONS_CLASS =
  'flex shrink-0 flex-wrap items-center gap-2'

export function adminPageHeaderBadgeClass(tone: AdminPageHeaderBadgeTone = 'slate'): string {
  switch (tone) {
    case 'violet':
      return 'rounded border border-violet-500/30 bg-violet-500/10 px-2 py-0.5 text-[11px] font-medium text-violet-200'
    case 'sky':
      return 'rounded border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 text-[11px] font-medium text-sky-200'
    case 'emerald':
      return 'rounded border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[11px] font-medium text-emerald-200'
    case 'rose':
      return 'rounded border border-rose-500/30 bg-rose-500/10 px-2 py-0.5 text-[11px] font-medium text-rose-200'
    case 'amber':
      return 'rounded border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[11px] font-medium text-amber-200'
    default:
      return 'rounded border border-slate-600/70 bg-slate-800/80 px-2 py-0.5 text-[11px] font-medium text-slate-400'
  }
}
