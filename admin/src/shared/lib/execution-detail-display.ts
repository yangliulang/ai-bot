// 作者: 杨永的Agent
// 日期: 2026-05-27
// 修改功能: 执行详情展示辅助（场景标题 · 对齐 5176 原型页眉）

import { ROUTE_PHASE1_SCENARIOS } from '@/entities/orchestration/scenario-registry'

export function scenarioDisplayTitle(scenarioId: string | null | undefined): string {
  const sid = (scenarioId ?? '').trim()
  if (!sid) return '执行详情'
  const row = ROUTE_PHASE1_SCENARIOS.find((r) => r.scenarioId === sid)
  return row?.scenarioTitle ?? sid
}

export function observabilityExecutionHref(executionId: string): string {
  const id = executionId.trim()
  return id ? `/observability?executionId=${encodeURIComponent(id)}` : '/observability'
}
