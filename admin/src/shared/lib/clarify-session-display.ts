// 作者: 杨永的Agent
// 日期: 2026-05-28
// 修改功能: MR-MEM-01 · 澄清会话协查展示（lifecycleState / clarifyTurn / resolvedSlotsSoFar）

export const MEMORY_RESUME_CLASSIFIED_EVENT = 'agent.memory.resume_classified' as const

export type ClarifyLifecycleState = 'active' | 'stale' | 'abandoned'

export interface ClarifySessionSnapshotView {
  lifecycleState: ClarifyLifecycleState | string
  clarifyTurn: number | string | null
  resolvedSlotsSoFar: Record<string, string>
  pendingClarifyKind?: string | null
  sessionId?: string | null
  executionId?: string | null
  sourceEventName?: string | null
}

export type ResumeClassifierDecision =
  | 'resume_prior_write'
  | 'new_intent'
  | 'need_one_clarify'
  | string

export interface ResumeClassifiedEventView {
  sessionId: string
  executionId?: string | null
  decision: ResumeClassifierDecision
  confidence?: number | null
  episodePickReason?: string | null
}

const LIFECYCLE_ZH: Record<string, string> = {
  active: '活跃',
  stale: '已 stale',
  abandoned: '已放弃',
}

const RESUME_DECISION_ZH: Record<string, string> = {
  resume_prior_write: '续单（resume_prior_write）',
  new_intent: '新意图（new_intent）',
  need_one_clarify: '需开放澄清（need_one_clarify）',
}

export function zhClarifyLifecycleState(state: string | null | undefined): string {
  const s = (state ?? '').trim()
  if (!s) return '—'
  return LIFECYCLE_ZH[s] ?? s
}

export function zhResumeClassifierDecision(decision: string | null | undefined): string {
  const d = (decision ?? '').trim()
  if (!d) return '—'
  return RESUME_DECISION_ZH[d] ?? d
}

function readStringRecord(raw: unknown): Record<string, string> {
  if (!raw || typeof raw !== 'object') return {}
  const out: Record<string, string> = {}
  for (const [k, v] of Object.entries(raw as Record<string, unknown>)) {
    if (typeof v === 'string' && v.trim()) out[k] = v.trim()
    else if (v != null && typeof v !== 'object') out[k] = String(v)
  }
  return out
}

function readClarifyTurn(raw: unknown): number | string | null {
  if (typeof raw === 'number' && Number.isFinite(raw)) return raw
  if (typeof raw === 'string' && raw.trim()) return raw.trim()
  return null
}

/** 从 timeline summary / payload 提取 ClarifySessionSnapshot 下限字段 */
export function parseClarifySessionFromSummary(
  summary: Record<string, unknown> | null | undefined,
  eventName?: string | null,
): ClarifySessionSnapshotView | null {
  if (!summary || typeof summary !== 'object') return null

  const nested =
    summary.clarifySession ??
    summary.clarifySessionSnapshot ??
    summary.agentRuntimeMemoryContext

  const src =
    nested && typeof nested === 'object'
      ? (nested as Record<string, unknown>)
      : summary

  const lifecycleRaw =
    src.lifecycleState ?? src.lifecycle_state ?? summary.lifecycleState ?? summary.lifecycle_state
  const lifecycleState =
    typeof lifecycleRaw === 'string' && lifecycleRaw.trim() ? lifecycleRaw.trim() : null

  const turnRaw = src.clarifyTurn ?? src.clarify_turn ?? summary.clarifyTurn ?? summary.clarify_turn
  const clarifyTurn = readClarifyTurn(turnRaw)

  const slotsRaw =
    src.resolvedSlotsSoFar ??
    src.resolved_slots_so_far ??
    summary.resolvedSlotsSoFar ??
    summary.resolved_slots_so_far
  const resolvedSlotsSoFar = readStringRecord(slotsRaw)

  const pendingRaw =
    src.pendingClarifyKind ?? src.pending_clarify_kind ?? summary.pendingClarifyKind
  const pendingClarifyKind =
    typeof pendingRaw === 'string' && pendingRaw.trim() ? pendingRaw.trim() : null

  const sessionRaw = src.sessionId ?? src.session_id ?? summary.sessionId
  const sessionId = typeof sessionRaw === 'string' && sessionRaw.trim() ? sessionRaw.trim() : null

  const execRaw = src.executionId ?? src.execution_id ?? summary.executionId
  const executionId = typeof execRaw === 'string' && execRaw.trim() ? execRaw.trim() : null

  if (!lifecycleState && clarifyTurn == null && Object.keys(resolvedSlotsSoFar).length === 0) {
    const l1 = summary.shortTermL1 ?? src.shortTermL1
    if (Array.isArray(l1)) {
      for (const block of l1) {
        if (!block || typeof block !== 'object') continue
        const b = block as Record<string, unknown>
        const cs = b.clarifySummary
        if (cs && typeof cs === 'object') {
          const nestedView = parseClarifySessionFromSummary(cs as Record<string, unknown>, eventName)
          if (nestedView) {
            return {
              ...nestedView,
              executionId: nestedView.executionId ?? executionId,
              sessionId: nestedView.sessionId ?? sessionId,
              sourceEventName: eventName ?? null,
            }
          }
          const human = (cs as Record<string, unknown>).resolvedSlotsHumanSummary
          if (typeof human === 'string' && human.trim()) {
            return {
              lifecycleState: 'active',
              clarifyTurn: readClarifyTurn((cs as Record<string, unknown>).clarifyTurn),
              resolvedSlotsSoFar: { _humanSummary: human.trim() },
              pendingClarifyKind:
                typeof (cs as Record<string, unknown>).pendingMissingHumanSummary === 'string'
                  ? String((cs as Record<string, unknown>).pendingMissingHumanSummary)
                  : null,
              sessionId,
              executionId: typeof b.executionId === 'string' ? b.executionId : executionId,
              sourceEventName: eventName ?? null,
            }
          }
        }
      }
    }
    return null
  }

  return {
    lifecycleState: lifecycleState ?? '—',
    clarifyTurn,
    resolvedSlotsSoFar,
    pendingClarifyKind,
    sessionId,
    executionId,
    sourceEventName: eventName ?? null,
  }
}

export function parseResumeClassifiedFromSummary(
  summary: Record<string, unknown> | null | undefined,
): ResumeClassifiedEventView | null {
  if (!summary || typeof summary !== 'object') return null
  const sessionRaw = summary.sessionId ?? summary.session_id
  const sessionId = typeof sessionRaw === 'string' ? sessionRaw.trim() : ''
  const decisionRaw = summary.decision
  const decision = typeof decisionRaw === 'string' ? decisionRaw.trim() : ''
  if (!sessionId || !decision) return null

  const execRaw = summary.executionId ?? summary.execution_id
  const executionId =
    typeof execRaw === 'string' && execRaw.trim() ? execRaw.trim() : null

  const confRaw = summary.confidence
  const confidence =
    typeof confRaw === 'number' && Number.isFinite(confRaw) ? confRaw : null

  const reasonRaw = summary.episodePickReason ?? summary.episode_pick_reason
  const episodePickReason =
    typeof reasonRaw === 'string' && reasonRaw.trim() ? reasonRaw.trim() : null

  return { sessionId, executionId, decision, confidence, episodePickReason }
}

export function formatResolvedSlotsSoFar(slots: Record<string, string>): string {
  const keys = Object.keys(slots)
  if (keys.length === 0) return '（无）'
  if (keys.length === 1 && keys[0] === '_humanSummary') return slots._humanSummary ?? '（无）'
  return keys.map((k) => `${k}=${slots[k]}`).join(' · ')
}

/** 从时间线条目列表取最新一条可展示的澄清快照 */
export function pickLatestClarifySessionFromTimeline(
  items: ReadonlyArray<{ eventName?: string | null; summary?: Record<string, unknown> | null }>,
): ClarifySessionSnapshotView | null {
  let latest: ClarifySessionSnapshotView | null = null
  for (const ev of items) {
    const summary = ev.summary ?? null
    if (!summary) continue
    const name = ev.eventName ?? null
    if (name === MEMORY_RESUME_CLASSIFIED_EVENT) continue
    const parsed = parseClarifySessionFromSummary(summary, name)
    if (parsed) latest = parsed
  }
  return latest
}

export function pickLatestResumeClassifiedFromTimeline(
  items: ReadonlyArray<{ eventName?: string | null; summary?: Record<string, unknown> | null }>,
): ResumeClassifiedEventView | null {
  let latest: ResumeClassifiedEventView | null = null
  for (const ev of items) {
    if (ev.eventName !== MEMORY_RESUME_CLASSIFIED_EVENT) continue
    const parsed = parseResumeClassifiedFromSummary(ev.summary ?? null)
    if (parsed) latest = parsed
  }
  return latest
}
