import type { ExecutionRow } from '@/entities/runtime/execution.schema'

export type ExecutionStatusFilter =
  | 'all'
  | 'CREATED'
  | 'COMPLETED'
  | 'RUNNING'
  | 'UNKNOWN'
  | 'FAILED'
  | 'BLOCKED'

const KNOWN_RUNTIME_STATUSES = new Set<ExecutionStatusFilter>([
  'all',
  'CREATED',
  'RUNNING',
  'COMPLETED',
  'UNKNOWN',
  'FAILED',
  'BLOCKED',
])

export function parseExecutionStatusFilter(raw: string | null | undefined): ExecutionStatusFilter {
  if (!raw || raw === 'all') return 'all'
  const u = raw.toUpperCase()
  const candidate = u as ExecutionStatusFilter
  if (KNOWN_RUNTIME_STATUSES.has(candidate) && candidate !== 'all') return candidate
  return 'all'
}

export function executionMatchesStatus(
  status: ExecutionStatusFilter,
  rowStatus: string,
): boolean {
  if (status === 'all') return true
  return rowStatus === status
}

export function executionInDateRange(isoDay: string, from: string, to: string): boolean {
  const day = isoDay.slice(0, 10)
  if (from && day < from) return false
  if (to && day > to) return false
  return true
}

export function executionMatchesCorrelationKeyword(
  row: Pick<ExecutionRow, 'executionId' | 'scenarioId'> & { userIdMasked: string },
  raw: string,
): boolean {
  const k = raw.trim().toLowerCase()
  if (!k) return true
  return (
    row.executionId.toLowerCase().includes(k) ||
    row.userIdMasked.toLowerCase().includes(k) ||
    row.scenarioId.toLowerCase().includes(k)
  )
}

export function executionMatchesScenarioParam(row: Pick<ExecutionRow, 'scenarioId'>, raw: string): boolean {
  const s = raw.trim()
  if (!s) return true
  return row.scenarioId === s
}

export function executionMatchesIntent(row: Pick<ExecutionRow, 'intent'>, raw: string): boolean {
  const t = raw.trim().toLowerCase()
  if (!t) return true
  return row.intent.toLowerCase().includes(t)
}