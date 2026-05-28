/**
 * 作者: 杨永的Agent
 * 日期: 2026-05-14
 * 修改功能: `isObservabilityTab`、`readObservabilityTraceQueryFromRoute`（对齐 product-doc observabilityDeepLink）
 * 日期: 2026-05-12
 * 修改功能: 执行链路协查页查询串构造（与 product-doc observabilityDeepLink 一致）
 */

import type { RouteLocationNormalizedLoaded } from 'vue-router'

export type ObservabilityTab = 'execution' | 'tool' | 'llm' | 'billing' | 'audit'

const OBS_TABS: ObservabilityTab[] = ['execution', 'tool', 'llm', 'billing', 'audit']

export function isObservabilityTab(s: string): s is ObservabilityTab {
  return (OBS_TABS as readonly string[]).includes(s)
}

/** 计费 trace 与 `traceKey` 同窗 */
export function readObservabilityTraceQueryFromRoute(route: RouteLocationNormalizedLoaded): string {
  const t = typeof route.query.traceId === 'string' ? route.query.traceId.trim() : ''
  if (t) return t
  const k = typeof route.query.traceKey === 'string' ? route.query.traceKey.trim() : ''
  return k
}

export function buildObservabilitySearch(params: {
  executionId?: string
  userId?: string
  traceId?: string
  traceKey?: string
  tab?: ObservabilityTab
}): string {
  const sp = new URLSearchParams()
  if (params.executionId?.trim()) sp.set('executionId', params.executionId.trim())
  if (params.userId?.trim()) sp.set('userId', params.userId.trim())
  const tid = (params.traceId?.trim() || params.traceKey?.trim()) ?? ''
  if (tid) sp.set('traceId', tid)
  if (params.tab) sp.set('tab', params.tab)
  const q = sp.toString()
  return q ? `?${q}` : ''
}
