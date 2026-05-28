/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-22
 * 修改功能: 工具条控件共用行高与 flex 簇 class（与 UiButton size=sm / UiSelect size=sm 对齐）
 */

/** 工具条内按钮、下拉、统计 Chip 共用行高 */
export const ADMIN_TOOLBAR_CONTROL_H_CLASS = 'h-8 min-h-8'

/** 筛选条 / 分页条右侧操作簇：水平居中、统一间距 */
export const ADMIN_TOOLBAR_CLUSTER_CLASS = 'inline-flex flex-wrap items-center gap-2'

/** 分页页码、范围文案等与控件同行的辅助文字 */
export const ADMIN_TOOLBAR_META_CLASS = `inline-flex ${ADMIN_TOOLBAR_CONTROL_H_CLASS} items-center text-xs leading-none tabular-nums text-slate-500`
