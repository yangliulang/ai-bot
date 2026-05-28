<!--
作者: 杨永的Agent
日期: 2026-05-28
修改功能: MR-MEM-01 · 澄清会话快照 / resume_classified 时间线展示块
作者: 杨永的Agent
日期: 2026-05-18
修改功能: 写路径治理条 · `binding_resolved` → `spec_read` → 确认；STM/LTM 记忆事件块（FE_HANDOFF 2026-05-27）
作者: 杨永的Agent
日期: 2026-05-18
修改功能: **`agent.prompt.binding_resolved`** / **`agent.skill.spec_read`** 治理事件展示（拼装层 / Skill 版本行 · FE_HANDOFF 2026-05-26）
作者: 杨永的Agent
日期: 2026-05-18
修改功能: **`trade.spot.cancel_order`** 时间线：**`cancel_order`** 流程条 + 侧栏徽标（撤单摘要 / 交易所撤单 · FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **时间轴**左侧 **竖线与圆点对齐**：窄轨 **`left-1/2 -translate-x-1/2`** + flex 分列（替代边框 + 魔法偏移）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 时间线引言仅 **`ts` + `(UTC+8)`/`(UTC)`** 后缀，去掉墙钟冗述
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 时间线 **`ts`** 与 Admin 全局时点模式一致；**`summary.venue` / `canonicalOp`** 徽标与摘要（ADR-004）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: **`trading.exchange_public`** / **`exchange_read`** · **`exchangeReadPreviewSummary`** / **`routing.read.*`**（§5.2.2）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: `orderRequest.flashMarketMeta` 协查块（volume 语义 · BUY 计价 / SELL base）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: 现货闪兑场景 · 消费 `transitionTrigger`/`stepKind`；`trade.spot.flash_convert` 对照 §5.2.1 流程摘要条
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { AppError } from '@/shared/api/errors'
import {
  getAdminObservabilityExecutionTimeline,
  type ObservabilityFlashMarketMeta,
  type ObservabilityLimitOrderMeta,
  type ObservabilityOrderRequestSnapshot,
  type ObservabilityTimelineItem,
  type ObservabilityTimelineSummary,
} from '@/shared/api/admin-observability'
import { adminTimeZoneParenSuffix } from '@/shared/lib/admin-datetime-display'
import { formatPromptPackVersionLabel, summarizeTradingPromptBinding } from '@/shared/lib/execution-prompt-meta'
import {
  PROMPT_BINDING_RESOLVED_EVENT,
  SKILL_SPEC_READ_EVENT,
  bindingToAssemblyLayers,
  parseSkillSpecReadFromTimeline,
  resolvePromptBindingForExecution,
} from '@/shared/lib/execution-prompt-assembly'
import { formatIsoTime } from '@/shared/copy/zh-runtime'
import {
  MEMORY_LTM_REVOKE_REQUESTED_EVENT,
  MEMORY_LTM_REVOKE_USER_HINT,
  MEMORY_RESUME_CLASSIFIED_EVENT,
  MEMORY_SESSION_CLEARED_EVENT,
  MEMORY_STM_CLEAR_USER_HINT,
  isWritePathScenario,
} from '@/shared/lib/write-path-display'
import {
  formatResolvedSlotsSoFar,
  parseClarifySessionFromSummary,
  parseResumeClassifiedFromSummary,
  zhClarifyLifecycleState,
  zhResumeClassifierDecision,
} from '@/shared/lib/clarify-session-display'

const FLASH_SCENARIO_ID = 'trade.spot.flash_convert'
const LIMIT_SCENARIO_ID = 'trade.spot.limit_order'
const CANCEL_SCENARIO_ID = 'trade.spot.cancel_order'

/** Telegram 托管预览 LLM 叙述 · **`agent_execution_event.event_name`** / `summary.stepKind`（FE_HANDOFF 0014～0016） */
const TIMELINE_EVENT_LLM_READ_MARKET_TICKER = 'llm.read.market.ticker'
const TIMELINE_EVENT_LLM_READ_MARKET_DEPTH = 'llm.read.market.depth'
const TIMELINE_EVENT_LLM_READ_MARKET_TRADES = 'llm.read.market.trades'
const TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE = 'llm.read.account.balance'
const TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ = 'llm.wealth.holdings_read'

const STEP_KIND_READ_MARKET_TICKER_LLM = 'read_market_ticker_llm'
const STEP_KIND_READ_MARKET_DEPTH_LLM = 'read_market_depth_llm'
const STEP_KIND_READ_MARKET_TRADES_LLM = 'read_market_trades_llm'
const STEP_KIND_READ_ACCOUNT_BALANCE_LLM = 'read_account_balance_llm'
const STEP_KIND_WEALTH_HOLDINGS_READ_LLM = 'wealth_holdings_read_llm'

const TIMELINE_EVENT_LLM_RUNTIME_CLARIFY = 'llm.agent.runtime.runtime_clarify'

type TimelineEventFilter = 'all' | 'runtime_clarify'

const timelineEventFilter = ref<TimelineEventFilter>('all')

const LLM_READ_MARKET_NARRATION_EVENT_NAMES = new Set<string>([
  TIMELINE_EVENT_LLM_READ_MARKET_TICKER,
  TIMELINE_EVENT_LLM_READ_MARKET_DEPTH,
  TIMELINE_EVENT_LLM_READ_MARKET_TRADES,
  TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE,
  TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ,
])

function expectedReadMarketStepKindConstant(eventName: string): string {
  switch (eventName) {
    case TIMELINE_EVENT_LLM_READ_MARKET_TICKER:
      return STEP_KIND_READ_MARKET_TICKER_LLM
    case TIMELINE_EVENT_LLM_READ_MARKET_DEPTH:
      return STEP_KIND_READ_MARKET_DEPTH_LLM
    case TIMELINE_EVENT_LLM_READ_MARKET_TRADES:
      return STEP_KIND_READ_MARKET_TRADES_LLM
    case TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE:
      return STEP_KIND_READ_ACCOUNT_BALANCE_LLM
    case TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ:
      return STEP_KIND_WEALTH_HOLDINGS_READ_LLM
    default:
      return '—'
  }
}
const ROUTING_READ_TRIGGER_ZH: Record<string, string> = {
  'routing.read.public_ticker': '公开 ticker',
  'routing.read.public_depth': '公开深度',
  'routing.read.public_trades': '公开成交',
  'routing.read.private_account': '账户只读',
  'routing.read.failed': '只读失败',
}

/** 限价写路径 `transitionTrigger`（HTTP / Telegram） */
const LIMIT_TRANSITION_ZH: Record<string, string> = {
  'limit.quote.public_ticker_band': '公开价 + 带宽校验',
  'limit.price_band_rejected': '限价偏离被拒',
  'limit.skip_public_quote': '跳过公开询价',
  'limit.order.submit': '限价提交',
  'limit.quote.public_ticker': '公开 ticker（TG）',
  'limit.confirm.type_a_offered': 'Type-A 确认提示',
}
const props = defineProps<{
  executionId: string
  /** 来自执行主表；传入可避免首屏时间线未到前无法识别闪兑 / 限价场景 */
  scenarioId?: string | null
}>()

const timelineTsParen = computed(() => adminTimeZoneParenSuffix())

const loading = ref(false)
const notFound = ref(false)
const errorText = ref<string | null>(null)
const items = ref<ObservabilityTimelineItem[]>([])

const idTrimmed = computed(() => props.executionId.trim())

async function fetchTimeline() {
  const id = idTrimmed.value
  if (!id) {
    items.value = []
    notFound.value = false
    errorText.value = null
    loading.value = false
    return
  }
  loading.value = true
  notFound.value = false
  errorText.value = null
  items.value = []
  try {
    const res = await getAdminObservabilityExecutionTimeline(id)
    items.value = res.items
  } catch (e) {
    if (e instanceof AppError && e.status === 404) {
      notFound.value = true
    } else {
      errorText.value = e instanceof AppError ? e.message : '时间线加载失败'
    }
  } finally {
    loading.value = false
  }
}

watch(
  idTrimmed,
  () => {
    timelineEventFilter.value = 'all'
    void fetchTimeline()
  },
  { immediate: true },
)

function readStepKind(summary: ObservabilityTimelineSummary): string | null {
  return typeof summary.stepKind === 'string' ? summary.stepKind : null
}

const VOLUME_SEMANTICS_ZH: Record<string, string> = {
  market_buy_quote_amount: '市价买：wire 上 volume = 计价币种金额（非 base 数量）。',
  market_sell_base_qty: '市价卖：wire 上 volume = base 数量。',
  limit_base_qty: '限价：wire 上 volume = base 数量（与用户意向一致）。',
}

function readOrderRequest(summary: ObservabilityTimelineSummary): ObservabilityOrderRequestSnapshot | null {
  const raw = summary.orderRequest
  if (!raw || typeof raw !== 'object') return null
  return raw as ObservabilityOrderRequestSnapshot
}

function formatObsScalar(v: unknown): string {
  if (v === null || v === undefined) return '—'
  if (typeof v === 'number') return String(v)
  const s = String(v).trim()
  return s || '—'
}

function volumeSemanticsZh(sem: string | undefined): string {
  if (!sem) return ''
  return VOLUME_SEMANTICS_ZH[sem] ?? ''
}

function formatExchangeReadPreviewSummaryText(v: unknown): string | null {
  if (v === null || v === undefined) return null
  if (typeof v === 'string') {
    const t = v.trim()
    return t || null
  }
  if (typeof v === 'number' || typeof v === 'boolean') return String(v)
  if (typeof v === 'object') {
    try {
      return JSON.stringify(v)
    } catch {
      return String(v)
    }
  }
  return String(v)
}

/** 时间线主摘要行防刷屏 */
function formatExchangeReadPreviewSummarySnippet(v: unknown): string | null {
  const full = formatExchangeReadPreviewSummaryText(v)
  if (!full) return null
  return full.length > 140 ? `${full.slice(0, 137)}…` : full
}

function isExchangeReadSummary(summary: ObservabilityTimelineSummary): boolean {
  return readStepKind(summary) === 'exchange_read'
}

function triggerDisplayLine(triggerRaw: string | null): string | null {
  if (!triggerRaw) return null
  const zh =
    LIMIT_TRANSITION_ZH[triggerRaw] ?? ROUTING_READ_TRIGGER_ZH[triggerRaw]
  return zh ? `trigger:${triggerRaw}（${zh}）` : `trigger:${triggerRaw}`
}

function summaryPick(summary: ObservabilityTimelineSummary, key: string): string | null {
  const v = summary[key]
  if (v === null || v === undefined) return null
  if (typeof v === 'string') {
    const t = v.trim()
    return t || null
  }
  if (typeof v === 'number' || typeof v === 'boolean') return String(v)
  return null
}

function readVenue(summary: ObservabilityTimelineSummary): string | null {
  return summaryPick(summary, 'venue')
}

function readCanonicalOp(summary: ObservabilityTimelineSummary): string | null {
  return summaryPick(summary, 'canonicalOp')
}

function summaryPreview(summary: ObservabilityTimelineSummary): string {
  const trigger =
    typeof summary.transitionTrigger === 'string' ? summary.transitionTrigger : null
  const stepKind = readStepKind(summary)
  const outcome = typeof summary.outcome === 'string' ? summary.outcome : null
  const methodPathSummary =
    typeof summary.methodPathSummary === 'string' ? summary.methodPathSummary : null
  const exchangeOutcome =
    typeof summary.exchangeOutcome === 'string' ? summary.exchangeOutcome : null
  const clientOrderRef =
    typeof summary.clientOrderRef === 'string' ? summary.clientOrderRef : null
  const parts = [
    triggerDisplayLine(trigger),
    stepKind,
    outcome,
    methodPathSummary,
    exchangeOutcome,
    clientOrderRef ? `clientOrderRef:${clientOrderRef}` : null,
  ].filter(Boolean)

  const vn = summaryPick(summary, 'venue')
  if (vn) parts.push(`venue:${vn}`)
  const co = summaryPick(summary, 'canonicalOp')
  if (co) parts.push(`canonicalOp:${co}`)

  if (trigger?.startsWith('limit.')) {
    const lp = summaryPick(summary, 'limitPrice')
    if (lp) parts.push(`limitPrice:${lp}`)
    const ls = summaryPick(summary, 'lastPrice')
    if (ls) parts.push(`lastPrice:${ls}`)
    const bc = summary['bandCheck']
    if (bc === true || bc === false) parts.push(`bandCheck:${String(bc)}`)
    const dp = summaryPick(summary, 'deviationPct')
    if (dp) parts.push(`deviationPct:${dp}`)
    const qr = summaryPick(summary, 'quantityRequested')
    if (qr) parts.push(`qtyReq:${qr}`)
  }

  if (isExchangeReadSummary(summary)) {
    const snip = formatExchangeReadPreviewSummarySnippet(summary.exchangeReadPreviewSummary)
    if (snip) parts.push(`readPreview:${snip}`)
    const ac = typeof summary.appErrorCode === 'string' ? summary.appErrorCode.trim() : ''
    if (ac) parts.push(`appErrorCode:${ac}`)
    const hs = summary.httpStatus
    if (hs !== undefined && hs !== null) parts.push(`httpStatus:${String(hs)}`)
  }

  return parts.join(' · ')
}

function stringifySummary(summary: ObservabilityTimelineSummary): string {
  try {
    return JSON.stringify(summary, null, 2)
  } catch {
    return String(summary)
  }
}

function jsonSnippet(obj: unknown): string {
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return String(obj)
  }
}

function isPromptBindingResolvedEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === PROMPT_BINDING_RESOLVED_EVENT
}

function isSkillSpecReadEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === SKILL_SPEC_READ_EVENT
}

function bindingAssemblySnippet(ev: ObservabilityTimelineItem): string | null {
  const binding = resolvePromptBindingForExecution({
    scenarioId: resolvedScenarioId.value,
    resolvedPromptBinding: ev.summary.resolvedPromptBinding ?? ev.summary.promptBindingResolved,
    timelineItems: [ev],
  })
  if (!binding?.systemPromptPackId && !binding?.tradingPromptPackId) return null
  const layers = bindingToAssemblyLayers(binding)
  return layers.map((r) => `${r.layer}:${r.source}`).join(' · ')
}

function skillSpecReadSnippet(ev: ObservabilityTimelineItem): string | null {
  const read = parseSkillSpecReadFromTimeline([ev])
  if (!read) return null
  return `${read.skillId}@${read.skillSpecVersion}`
}

function timelineDotClass(name: string): string {
  if (name === PROMPT_BINDING_RESOLVED_EVENT) {
    return 'bg-violet-500/90 ring-violet-500/40 shadow-[0_0_12px_-2px_rgba(139,92,246,0.45)]'
  }
  if (name === SKILL_SPEC_READ_EVENT) {
    return 'bg-amber-400/95 ring-amber-500/35 shadow-[0_0_12px_-2px_rgba(251,191,36,0.35)]'
  }
  if (name === MEMORY_SESSION_CLEARED_EVENT) {
    return 'bg-sky-400/95 ring-sky-500/40 shadow-[0_0_12px_-2px_rgba(56,189,248,0.38)]'
  }
  if (name === MEMORY_RESUME_CLASSIFIED_EVENT) {
    return 'bg-teal-400/95 ring-teal-500/40 shadow-[0_0_12px_-2px_rgba(45,212,191,0.38)]'
  }
  if (name === MEMORY_LTM_REVOKE_REQUESTED_EVENT) {
    return 'bg-rose-400/95 ring-rose-500/38 shadow-[0_0_12px_-2px_rgba(251,113,133,0.35)]'
  }
  if (name === 'confirmation.required' || name === 'confirm.pending') {
    return 'bg-orange-400/95 ring-orange-500/38 shadow-[0_0_12px_-2px_rgba(251,146,60,0.35)]'
  }
  if (name === 'prompt.snapshot') {
    return 'bg-violet-400/95 ring-violet-500/40 shadow-[0_0_12px_-2px_rgba(167,139,250,0.4)]'
  }
  if (name === 'llm.chat.faq') {
    return 'bg-indigo-400/95 ring-indigo-500/40 shadow-[0_0_12px_-2px_rgba(129,140,248,0.4)]'
  }
  if (name === TIMELINE_EVENT_LLM_RUNTIME_CLARIFY) {
    return 'bg-orange-400/95 ring-orange-500/38 shadow-[0_0_12px_-2px_rgba(251,146,60,0.35)]'
  }
  if (name === TIMELINE_EVENT_LLM_READ_MARKET_TICKER) {
    return 'bg-teal-400/95 ring-teal-500/40 shadow-[0_0_12px_-2px_rgba(45,212,191,0.38)]'
  }
  if (name === TIMELINE_EVENT_LLM_READ_MARKET_DEPTH) {
    return 'bg-emerald-400/95 ring-emerald-500/40 shadow-[0_0_12px_-2px_rgba(52,211,153,0.38)]'
  }
  if (name === TIMELINE_EVENT_LLM_READ_MARKET_TRADES) {
    return 'bg-amber-400/95 ring-amber-500/35 shadow-[0_0_12px_-2px_rgba(251,191,36,0.35)]'
  }
  if (name === TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE) {
    return 'bg-sky-400/95 ring-sky-500/40 shadow-[0_0_12px_-2px_rgba(56,189,248,0.38)]'
  }
  if (name === TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ) {
    return 'bg-fuchsia-400/95 ring-fuchsia-500/38 shadow-[0_0_12px_-2px_rgba(232,121,249,0.38)]'
  }
  if (name === 'trading.exchange_public') {
    return 'bg-cyan-400/95 ring-cyan-500/40 shadow-[0_0_12px_-2px_rgba(34,211,238,0.35)]'
  }
  if (name.includes('exchange') || name.includes('trading')) {
    return 'bg-emerald-400/95 ring-emerald-500/40 shadow-[0_0_14px_-2px_rgba(52,211,153,0.45)]'
  }
  if (name.includes('agent.execution')) {
    return 'bg-sky-400/90 ring-sky-500/35'
  }
  return 'bg-slate-400/85 ring-slate-500/30'
}

const orderedItems = computed(() =>
  [...items.value].sort((a, b) => new Date(a.ts).getTime() - new Date(b.ts).getTime()),
)

function flashVolumeExplain(summary: ObservabilityTimelineSummary): {
  or: ObservabilityOrderRequestSnapshot
  fm: ObservabilityFlashMarketMeta
} | null {
  const or = readOrderRequest(summary)
  const fm = or?.flashMarketMeta
  if (!or || !fm || typeof fm !== 'object') return null
  return { or, fm }
}

function limitVolumeExplain(summary: ObservabilityTimelineSummary): {
  or: ObservabilityOrderRequestSnapshot
  lm: ObservabilityLimitOrderMeta
} | null {
  const or = readOrderRequest(summary)
  const lm = or?.limitOrderMeta
  if (!or || !lm || typeof lm !== 'object') return null
  return { or, lm }
}

const runtimeClarifyEventCount = computed(
  () => orderedItems.value.filter((ev) => ev.eventName === TIMELINE_EVENT_LLM_RUNTIME_CLARIFY).length,
)

const filteredOrderedItems = computed(() => {
  if (timelineEventFilter.value !== 'runtime_clarify') return orderedItems.value
  return orderedItems.value.filter((ev) => ev.eventName === TIMELINE_EVENT_LLM_RUNTIME_CLARIFY)
})

const timelineRows = computed(() =>
  filteredOrderedItems.value.map((ev) => ({
    ev,
    flash: flashVolumeExplain(ev.summary),
    limit: limitVolumeExplain(ev.summary),
  })),
)

const resolvedScenarioId = computed(() => {
  const fromProp = typeof props.scenarioId === 'string' ? props.scenarioId.trim() : ''
  if (fromProp) return fromProp
  for (const ev of orderedItems.value) {
    const sid = ev.summary?.scenarioId
    if (typeof sid === 'string' && sid.trim()) return sid.trim()
  }
  return ''
})

const isFlashConvert = computed(() => resolvedScenarioId.value === FLASH_SCENARIO_ID)

const isLimitOrder = computed(() => resolvedScenarioId.value === LIMIT_SCENARIO_ID)

const isSpotCancelOrder = computed(() => resolvedScenarioId.value === CANCEL_SCENARIO_ID)

const isWritePath = computed(() => isWritePathScenario(resolvedScenarioId.value))

type WriteGovernancePhaseRow = {
  key: string
  label: string
  docHint: string
  match: (ev: ObservabilityTimelineItem) => boolean
}

const WRITE_GOVERNANCE_PHASES: WriteGovernancePhaseRow[] = [
  {
    key: 'binding',
    label: 'Prompt 绑定',
    docHint: PROMPT_BINDING_RESOLVED_EVENT,
    match: (ev) => ev.eventName === PROMPT_BINDING_RESOLVED_EVENT,
  },
  {
    key: 'spec_read',
    label: 'Skill Spec',
    docHint: SKILL_SPEC_READ_EVENT,
    match: (ev) => ev.eventName === SKILL_SPEC_READ_EVENT,
  },
  {
    key: 'confirm',
    label: 'Type-A 确认',
    docHint: 'confirmation.required · confirm.pending · confirm_prompt',
    match: (ev) => {
      if (ev.eventName === 'confirmation.required' || ev.eventName === 'confirm.pending') {
        return true
      }
      const sk = readStepKind(ev.summary)
      return (
        ev.eventName === 'agent.execution.step' &&
        (sk === 'confirm_prompt' || sk === 'confirm_accept')
      )
    },
  },
]

type FlashPhaseStatus = 'done' | 'pending' | 'skipped'

type FlashPhaseRow = {
  key: string
  label: string
  docHint: string
  telegramOnly?: boolean
  match: (ev: ObservabilityTimelineItem) => boolean
}

const FLASH_PHASES: FlashPhaseRow[] = [
  {
    key: 'quote',
    label: '询价',
    docHint: 'agent.execution.step · quote',
    match: (ev) => ev.eventName === 'agent.execution.step' && readStepKind(ev.summary) === 'quote',
  },
  {
    key: 'confirm_prompt',
    label: '确认提示',
    docHint: 'agent.execution.step · confirm_prompt',
    telegramOnly: true,
    match: (ev) =>
      ev.eventName === 'agent.execution.step' && readStepKind(ev.summary) === 'confirm_prompt',
  },
  {
    key: 'confirm_accept',
    label: '用户确认',
    docHint: 'agent.execution.step · confirm_accept',
    telegramOnly: true,
    match: (ev) =>
      ev.eventName === 'agent.execution.step' && readStepKind(ev.summary) === 'confirm_accept',
  },
  {
    key: 'submit_agent',
    label: '提交订单（摘要）',
    docHint: 'agent.execution.step · submit_order',
    match: (ev) =>
      ev.eventName === 'agent.execution.step' && readStepKind(ev.summary) === 'submit_order',
  },
  {
    key: 'exchange_private',
    label: '交易所下单',
    docHint: 'trading.exchange_private · submit_order',
    match: (ev) =>
      ev.eventName === 'trading.exchange_private' && readStepKind(ev.summary) === 'submit_order',
  },
]

const flashPhaseStrip = computed(() => {
  if (!isFlashConvert.value) return []
  const list = orderedItems.value
  const [q, cp, ca, , ex] = FLASH_PHASES
  const hasQuote = q ? list.some(q.match) : false
  const hasPrompt = cp ? list.some(cp.match) : false
  const hasAccept = ca ? list.some(ca.match) : false
  const hasExchange = ex ? list.some(ex.match) : false
  /** HTTP 直连典型路径：无 Telegram 二次确认事件（见 API 文档 §5.2.1） */
  const httpDirectLikely = hasQuote && hasExchange && !hasPrompt && !hasAccept

  return FLASH_PHASES.map((phase): { phase: FlashPhaseRow; status: FlashPhaseStatus } => {
    const done = list.some(phase.match)
    if (done) return { phase, status: 'done' }
    if (phase.telegramOnly && httpDirectLikely) return { phase, status: 'skipped' }
    return { phase, status: 'pending' }
  })
})

const limitPhaseStrip = computed(() => {
  if (!isLimitOrder.value) return []
  const list = orderedItems.value
  const [q, cp, ca, , ex] = FLASH_PHASES
  const hasQuote = q ? list.some(q.match) : false
  const hasPrompt = cp ? list.some(cp.match) : false
  const hasAccept = ca ? list.some(ca.match) : false
  const hasExchange = ex ? list.some(ex.match) : false
  const httpDirectLikely = hasQuote && hasExchange && !hasPrompt && !hasAccept

  return FLASH_PHASES.map((phase): { phase: FlashPhaseRow; status: FlashPhaseStatus } => {
    const done = list.some(phase.match)
    if (done) return { phase, status: 'done' }
    if (phase.telegramOnly && httpDirectLikely) return { phase, status: 'skipped' }
    return { phase, status: 'pending' }
  })
})

const CANCEL_PHASES: FlashPhaseRow[] = [
  {
    key: 'cancel_step',
    label: '撤单（摘要）',
    docHint: 'agent.execution.step · cancel_order',
    match: (ev) =>
      ev.eventName === 'agent.execution.step' && readStepKind(ev.summary) === 'cancel_order',
  },
  {
    key: 'cancel_exchange',
    label: '交易所撤单',
    docHint: 'trading.exchange_private · cancel_order',
    match: (ev) =>
      ev.eventName === 'trading.exchange_private' && readStepKind(ev.summary) === 'cancel_order',
  },
]

const cancelPhaseStrip = computed(() => {
  if (!isSpotCancelOrder.value) return []
  const list = orderedItems.value
  return CANCEL_PHASES.map((phase): { phase: FlashPhaseRow; status: FlashPhaseStatus } => ({
    phase,
    status: list.some(phase.match) ? 'done' : 'pending',
  }))
})

const writePathGovernanceStrip = computed(() => {
  if (!isWritePath.value) return []
  const list = orderedItems.value
  return WRITE_GOVERNANCE_PHASES.map(
    (phase): { phase: WriteGovernancePhaseRow; status: FlashPhaseStatus } => ({
      phase,
      status: list.some(phase.match) ? 'done' : 'pending',
    }),
  )
})

const writePathOrderHint = computed((): string | null => {
  if (!isWritePath.value) return null
  const list = orderedItems.value
  const specIdx = list.findIndex((ev) => ev.eventName === SKILL_SPEC_READ_EVENT)
  const confirmIdx = list.findIndex((ev) => WRITE_GOVERNANCE_PHASES[2]?.match(ev))
  if (specIdx < 0) {
    return '写路径时间线尚未出现 agent.skill.spec_read（Type-A 前应加载 Skill Spec）。'
  }
  if (confirmIdx >= 0 && specIdx > confirmIdx) {
    return 'agent.skill.spec_read 应早于确认相关事件（binding → spec_read → confirmation）。'
  }
  return null
})

function isMemorySessionClearedEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === MEMORY_SESSION_CLEARED_EVENT
}

function isMemoryResumeClassifiedEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === MEMORY_RESUME_CLASSIFIED_EVENT
}

function clarifySessionFromEv(ev: ObservabilityTimelineItem) {
  return parseClarifySessionFromSummary(ev.summary as Record<string, unknown>, ev.eventName)
}

function resumeClassifiedFromEv(ev: ObservabilityTimelineItem) {
  return parseResumeClassifiedFromSummary(ev.summary as Record<string, unknown>)
}

function isMemoryLtmRevokeEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === MEMORY_LTM_REVOKE_REQUESTED_EVENT
}

function isConfirmationRequiredEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === 'confirmation.required'
}

function memoryTimelineHeadline(ev: ObservabilityTimelineItem): string {
  const tr =
    typeof ev.summary.transitionTrigger === 'string' ? ev.summary.transitionTrigger.trim() : ''
  if (isMemoryLtmRevokeEv(ev)) {
    return tr ? `${tr} · LTM 撤销筹备中` : 'LTM 撤销筹备中（不清 STM-only）'
  }
  if (isMemorySessionClearedEv(ev)) return tr ? `${tr} · STM 已清空` : '本会话短期记忆已清空'
  return summaryPreview(ev.summary)
}

function spotCancelTimelineBadge(ev: ObservabilityTimelineItem): string | null {
  if (!isSpotCancelOrder.value) return null
  const sk = readStepKind(ev.summary)
  if (ev.eventName === 'agent.execution.step' && sk === 'cancel_order') return '撤单（摘要）'
  if (ev.eventName === 'trading.exchange_private' && sk === 'cancel_order') return '交易所撤单'
  return null
}

function flashRowBadge(ev: ObservabilityTimelineItem): string | null {
  if (!isFlashConvert.value && !isLimitOrder.value) return null
  const row = FLASH_PHASES.find((p) => p.match(ev))
  return row ? row.label : null
}

function flashDocFallbackBadge(ev: ObservabilityTimelineItem): string | null {
  const cancelBadge = spotCancelTimelineBadge(ev)
  if (cancelBadge) return cancelBadge
  if (!isFlashConvert.value && !isLimitOrder.value) return null
  const sk = readStepKind(ev.summary)
  if (!sk) return null
  if (ev.eventName === 'agent.execution.step') {
    const map: Record<string, string> = {
      quote: '询价',
      confirm_prompt: '确认提示',
      confirm_accept: '用户确认',
      submit_order: '提交订单（摘要）',
    }
    return map[sk] ?? `step:${sk}`
  }
  if (ev.eventName === 'trading.exchange_private' && sk === 'submit_order') return '交易所下单'
  return null
}

function readRouteBadge(ev: ObservabilityTimelineItem): string | null {
  if (!isExchangeReadSummary(ev.summary)) return null
  const trRaw = ev.summary.transitionTrigger
  const tr = typeof trRaw === 'string' ? trRaw.trim() : ''
  if (tr && ROUTING_READ_TRIGGER_ZH[tr]) return ROUTING_READ_TRIGGER_ZH[tr]
  if (ev.eventName === 'agent.execution.step') return '只读失败（step）'
  if (ev.eventName === 'trading.exchange_public') return '公开接口 · exchange_read'
  if (ev.eventName === 'trading.exchange_private') return '私有接口 · exchange_read'
  return 'exchange_read'
}

function exchangeReadBlockPreview(summary: ObservabilityTimelineSummary): string | null {
  return formatExchangeReadPreviewSummaryText(summary.exchangeReadPreviewSummary)
}

function isPromptSnapshotTimelineEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === 'prompt.snapshot'
}

function isLlmChatFaqTimelineEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === 'llm.chat.faq'
}

function isRuntimeClarifyTimelineEv(ev: ObservabilityTimelineItem): boolean {
  return ev.eventName === TIMELINE_EVENT_LLM_RUNTIME_CLARIFY
}

function isLlmReadMarketNarrationTimelineEv(ev: ObservabilityTimelineItem): boolean {
  return LLM_READ_MARKET_NARRATION_EVENT_NAMES.has(ev.eventName)
}

function llmReadMarketNarrationTitle(ev: ObservabilityTimelineItem): string {
  switch (ev.eventName) {
    case TIMELINE_EVENT_LLM_READ_MARKET_TICKER:
      return 'LLM · read.market.ticker（公开 ticker 叙述）'
    case TIMELINE_EVENT_LLM_READ_MARKET_DEPTH:
      return 'LLM · read.market.depth（深度叙述）'
    case TIMELINE_EVENT_LLM_READ_MARKET_TRADES:
      return 'LLM · read.market.trades（公开成交叙述）'
    case TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE:
      return 'LLM · read.account.balance（账户余额叙述）'
    case TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ:
      return 'LLM · wealth.holdings_read（持仓只读叙述）'
    default:
      return 'LLM · exchange_read 预览叙述'
  }
}

function llmReadMarketNarrationPanelClass(ev: ObservabilityTimelineItem): string {
  const base =
    'mt-2 rounded-lg border px-3 py-2.5 text-xs leading-relaxed text-slate-300'
  switch (ev.eventName) {
    case TIMELINE_EVENT_LLM_READ_MARKET_TICKER:
      return `${base} border-teal-500/25 bg-teal-950/20`
    case TIMELINE_EVENT_LLM_READ_MARKET_DEPTH:
      return `${base} border-emerald-500/25 bg-emerald-950/20`
    case TIMELINE_EVENT_LLM_READ_MARKET_TRADES:
      return `${base} border-amber-500/25 bg-amber-950/20`
    case TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE:
      return `${base} border-sky-500/25 bg-sky-950/20`
    case TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ:
      return `${base} border-fuchsia-500/25 bg-fuchsia-950/25`
    default:
      return `${base} border-teal-500/25 bg-teal-950/20`
  }
}

function llmReadMarketNarrationHeadlineAccentClass(ev: ObservabilityTimelineItem): string {
  switch (ev.eventName) {
    case TIMELINE_EVENT_LLM_READ_MARKET_TICKER:
      return 'text-teal-100/95'
    case TIMELINE_EVENT_LLM_READ_MARKET_DEPTH:
      return 'text-emerald-100/95'
    case TIMELINE_EVENT_LLM_READ_MARKET_TRADES:
      return 'text-amber-100/95'
    case TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE:
      return 'text-sky-100/95'
    case TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ:
      return 'text-fuchsia-100/95'
    default:
      return 'text-teal-100/95'
  }
}

function llmReadMarketNarrationStepSpanClass(ev: ObservabilityTimelineItem): string {
  switch (ev.eventName) {
    case TIMELINE_EVENT_LLM_READ_MARKET_TICKER:
      return 'text-teal-200/75'
    case TIMELINE_EVENT_LLM_READ_MARKET_DEPTH:
      return 'text-emerald-200/75'
    case TIMELINE_EVENT_LLM_READ_MARKET_TRADES:
      return 'text-amber-200/80'
    case TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE:
      return 'text-sky-200/80'
    case TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ:
      return 'text-fuchsia-200/85'
    default:
      return 'text-teal-200/75'
  }
}
function timelineHeadline(ev: ObservabilityTimelineItem): string {
  const s = ev.summary
  if (
    isPromptSnapshotTimelineEv(ev) ||
    isLlmChatFaqTimelineEv(ev) ||
    isLlmReadMarketNarrationTimelineEv(ev)
  ) {
    const sk = readStepKind(s) ?? '—'
    const oc = typeof s.outcome === 'string' && s.outcome.trim() ? s.outcome : '—'
    return `${sk} · outcome:${oc}`
  }
  return summaryPreview(s)
}

/** NLU effective 快照：system 包一行 */
function systemPromptBindingBrief(summary: ObservabilityTimelineSummary): string | null {
  const b = summary.resolvedPromptBinding
  if (b == null || typeof b !== 'object') return null
  const o = b as Record<string, unknown>
  const id = typeof o.systemPromptPackId === 'string' ? o.systemPromptPackId.trim() : ''
  const ver = typeof o.systemPromptPackVersion === 'string' ? o.systemPromptPackVersion.trim() : ''
  if (!id && !ver) return null
  const tail = ver ? ` · v${ver}` : ''
  return `${id || '—'}${tail}`
}

function eventNameBadgeClass(name: string): string {
  if (name === PROMPT_BINDING_RESOLVED_EVENT) {
    return 'border-violet-500/40 bg-violet-500/15 text-violet-100/95'
  }
  if (name === SKILL_SPEC_READ_EVENT) {
    return 'border-amber-500/35 bg-amber-500/12 text-amber-100/95'
  }
  if (name === MEMORY_SESSION_CLEARED_EVENT) {
    return 'border-sky-500/35 bg-sky-500/12 text-sky-100/95'
  }
  if (name === MEMORY_RESUME_CLASSIFIED_EVENT) {
    return 'border-teal-500/35 bg-teal-500/12 text-teal-100/95'
  }
  if (name === MEMORY_LTM_REVOKE_REQUESTED_EVENT) {
    return 'border-rose-500/35 bg-rose-500/12 text-rose-100/95'
  }
  if (name === 'confirmation.required' || name === 'confirm.pending') {
    return 'border-orange-500/35 bg-orange-500/12 text-orange-100/95'
  }
  if (name === 'prompt.snapshot') {
    return 'border-violet-500/35 bg-violet-500/12 text-violet-100/95'
  }
  if (name === 'llm.chat.faq') {
    return 'border-indigo-500/35 bg-indigo-500/12 text-indigo-100/95'
  }
  if (name === TIMELINE_EVENT_LLM_RUNTIME_CLARIFY) {
    return 'border-orange-500/35 bg-orange-500/12 text-orange-100/95'
  }
  if (name === TIMELINE_EVENT_LLM_READ_MARKET_TICKER) {
    return 'border-teal-500/35 bg-teal-500/12 text-teal-100/95'
  }
  if (name === TIMELINE_EVENT_LLM_READ_MARKET_DEPTH) {
    return 'border-emerald-500/35 bg-emerald-500/12 text-emerald-100/95'
  }
  if (name === TIMELINE_EVENT_LLM_READ_MARKET_TRADES) {
    return 'border-amber-500/35 bg-amber-500/12 text-amber-100/95'
  }
  if (name === TIMELINE_EVENT_LLM_READ_ACCOUNT_BALANCE) {
    return 'border-sky-500/35 bg-sky-500/12 text-sky-100/95'
  }
  if (name === TIMELINE_EVENT_LLM_WEALTH_HOLDINGS_READ) {
    return 'border-fuchsia-500/35 bg-fuchsia-500/12 text-fuchsia-100/95'
  }
  return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200/90'
}

function llmChatFaqOutcomeClass(outcomeRaw: unknown): string {
  const o = typeof outcomeRaw === 'string' ? outcomeRaw.trim().toLowerCase() : ''
  if (o === 'success') return 'text-emerald-200/95'
  if (o === 'failure' || o === 'failed') return 'text-rose-200/95'
  return 'text-slate-200'
}
</script>

<template>
  <div class="space-y-3">
    <p v-if="!idTrimmed" class="text-sm text-slate-500">
      暂无 executionId · 请先输入或选中一条执行记录。
    </p>
    <p v-else-if="loading" class="text-sm text-slate-500">加载时间线…</p>
    <p v-else-if="errorText" class="text-sm text-rose-400">{{ errorText }}</p>
    <p v-else-if="notFound" class="text-sm text-rose-400">
      未找到该 execution（404 · AGENT_ADMIN_EXECUTION_NOT_FOUND）；无父行则无时间线。
    </p>
    <template v-else-if="items.length === 0">
      <p class="text-sm text-slate-500">当前执行尚无事件条目（Phase1 · Telegram 闪兑确认等路径写入后可见）。</p>
    </template>
    <template v-else>
      <div class="flex flex-wrap items-center gap-2">
        <span class="text-[11px] text-slate-500">事件筛选</span>
        <button
          type="button"
          class="rounded-md border px-2 py-1 font-mono text-[11px] transition-colors"
          :class="
            timelineEventFilter === 'all'
              ? 'border-slate-600 bg-slate-800 text-slate-200'
              : 'border-slate-800 bg-transparent text-slate-500 hover:border-slate-700 hover:text-slate-300'
          "
          @click="timelineEventFilter = 'all'"
        >
          全部（{{ orderedItems.length }}）
        </button>
        <button
          type="button"
          class="rounded-md border px-2 py-1 font-mono text-[11px] transition-colors"
          :class="
            timelineEventFilter === 'runtime_clarify'
              ? 'border-orange-500/45 bg-orange-500/12 text-orange-100/95'
              : 'border-slate-800 bg-transparent text-slate-500 hover:border-slate-700 hover:text-slate-300'
          "
          @click="timelineEventFilter = 'runtime_clarify'"
        >
          runtime_clarify（{{ runtimeClarifyEventCount }}）
        </button>
      </div>
      <p
        v-if="timelineEventFilter === 'runtime_clarify' && timelineRows.length === 0"
        class="text-sm text-slate-500"
      >
        当前执行无 <code class="font-mono text-xs">llm.agent.runtime.runtime_clarify</code> 事件（需开启
        intentClarifyUseLlm 且走 CLARIFY 润色路径）。
      </p>
      <p class="text-[11px] text-slate-500">
        时间列 <code class="font-mono">ts</code
        ><span class="font-medium text-slate-400">{{ timelineTsParen }}</span>。
      </p>
      <div
        v-if="isFlashConvert && flashPhaseStrip.length"
        class="rounded-lg border border-slate-800 bg-slate-900/45 px-3 py-2.5 text-xs leading-relaxed text-slate-400"
      >
        <p class="font-medium text-slate-300">现货闪兑流程（对照 API §5.2.1）</p>
        <p class="mt-1 text-[11px] text-slate-500">
          quote → confirm → order；HTTP 直连可无中间确认步（以下为推测「跳过」，以时间线事实为准）。
        </p>
        <ol class="mt-2 flex flex-wrap gap-2">
          <li
            v-for="row in flashPhaseStrip"
            :key="row.phase.key"
            class="inline-flex max-w-full items-center gap-1.5 rounded-md border px-2 py-1 font-mono text-[11px]"
            :class="{
              'border-emerald-500/35 bg-emerald-500/10 text-emerald-200/95': row.status === 'done',
              'border-slate-700/90 bg-slate-950/40 text-slate-500': row.status === 'pending',
              'border-slate-700/60 bg-slate-950/25 text-slate-600 line-through decoration-slate-600':
                row.status === 'skipped',
            }"
            :title="row.phase.docHint"
          >
            <span class="truncate">{{ row.phase.label }}</span>
            <span v-if="row.status === 'done'" aria-hidden="true">✓</span>
            <span v-else-if="row.status === 'skipped'" class="text-[10px] normal-case no-underline text-slate-600">
              跳过
            </span>
          </li>
        </ol>
      </div>
      <div
        v-if="isLimitOrder && limitPhaseStrip.length"
        class="rounded-lg border border-amber-900/40 bg-slate-900/45 px-3 py-2.5 text-xs leading-relaxed text-slate-400"
      >
        <p class="font-medium text-amber-100/90">现货限价流程（FE_HANDOFF §2.2 · <code class="text-[10px]">trade.spot.limit_order</code>）</p>
        <p class="mt-1 text-[11px] text-slate-500">
          quote（可选 band）→ confirm → submit → exchange_private；HTTP 可无 Telegram 确认步（「跳过」为推测）。
        </p>
        <ol class="mt-2 flex flex-wrap gap-2">
          <li
            v-for="row in limitPhaseStrip"
            :key="'lim-' + row.phase.key"
            class="inline-flex max-w-full items-center gap-1.5 rounded-md border px-2 py-1 font-mono text-[11px]"
            :class="{
              'border-amber-500/35 bg-amber-500/10 text-amber-100/95': row.status === 'done',
              'border-slate-700/90 bg-slate-950/40 text-slate-500': row.status === 'pending',
              'border-slate-700/60 bg-slate-950/25 text-slate-600 line-through decoration-slate-600':
                row.status === 'skipped',
            }"
            :title="row.phase.docHint"
          >
            <span class="truncate">{{ row.phase.label }}</span>
            <span v-if="row.status === 'done'" aria-hidden="true">✓</span>
            <span v-else-if="row.status === 'skipped'" class="text-[10px] normal-case no-underline text-slate-600">
              跳过
            </span>
          </li>
        </ol>
      </div>
      <div
        v-if="isWritePath && writePathGovernanceStrip.length"
        class="rounded-lg border border-violet-900/35 bg-slate-900/45 px-3 py-2.5 text-xs leading-relaxed text-slate-400"
      >
        <p class="font-medium text-violet-100/90">
          写路径治理顺序 · <code class="text-[10px] text-violet-200/85">{{ resolvedScenarioId }}</code>
        </p>
        <p class="mt-1 text-[11px] text-slate-500">
          Type-A 前须完成 Prompt 绑定与 Skill Spec 读取，再进入确认（含 Telegram 与 HTTP 闪兑/限价等）。
        </p>
        <ol class="mt-2 flex flex-wrap gap-2">
          <li
            v-for="row in writePathGovernanceStrip"
            :key="'wp-' + row.phase.key"
            class="inline-flex max-w-full items-center gap-1.5 rounded-md border px-2 py-1 font-mono text-[11px]"
            :class="{
              'border-violet-500/35 bg-violet-500/10 text-violet-100/95': row.status === 'done',
              'border-slate-700/90 bg-slate-950/40 text-slate-500': row.status === 'pending',
            }"
            :title="row.phase.docHint"
          >
            <span class="truncate">{{ row.phase.label }}</span>
            <span v-if="row.status === 'done'" aria-hidden="true">✓</span>
          </li>
        </ol>
        <p v-if="writePathOrderHint" class="mt-2 text-[11px] text-amber-200/90">{{ writePathOrderHint }}</p>
      </div>
      <div
        v-if="isSpotCancelOrder && cancelPhaseStrip.length"
        class="rounded-lg border border-rose-900/35 bg-slate-900/45 px-3 py-2.5 text-xs leading-relaxed text-slate-400"
      >
        <p class="font-medium text-rose-100/90">
          现货撤单流程 · <code class="text-[10px] text-rose-200/85">{{ CANCEL_SCENARIO_ID }}</code>
        </p>
        <p class="mt-1 text-[11px] text-slate-500">
          execution_accept → agent.execution.step（<strong class="font-medium text-slate-400">cancel_order</strong>）→
          trading.exchange_private。
        </p>
        <ol class="mt-2 flex flex-wrap gap-2">
          <li
            v-for="row in cancelPhaseStrip"
            :key="'cancel-' + row.phase.key"
            class="inline-flex max-w-full items-center gap-1.5 rounded-md border px-2 py-1 font-mono text-[11px]"
            :class="{
              'border-rose-500/35 bg-rose-500/10 text-rose-100/95': row.status === 'done',
              'border-slate-700/90 bg-slate-950/40 text-slate-500': row.status === 'pending',
            }"
            :title="row.phase.docHint"
          >
            <span class="truncate">{{ row.phase.label }}</span>
            <span v-if="row.status === 'done'" aria-hidden="true">✓</span>
          </li>
        </ol>
      </div>
      <ol class="relative m-0 list-none space-y-0 p-0">
      <li
        v-for="(row, idx) in timelineRows"
        :key="`${idx}-${row.ev.ts}-${row.ev.eventName}`"
        class="flex gap-4 transition-colors [&:not(:last-child)]:pb-6"
      >
        <div class="relative flex w-5 shrink-0 justify-center self-stretch pt-1.5">
          <div
            v-if="idx < timelineRows.length - 1"
            class="pointer-events-none absolute left-1/2 top-[17px] z-0 h-[calc(100%+1.875rem-17px)] w-px -translate-x-1/2 bg-slate-800/95"
            aria-hidden="true"
          />
          <span
            class="relative z-[1] mt-px h-2.5 w-2.5 shrink-0 rounded-full ring-2 ring-offset-2 ring-offset-slate-950"
            :class="timelineDotClass(row.ev.eventName)"
            aria-hidden="true"
          />
        </div>
        <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-baseline gap-x-2 gap-y-1">
          <time class="font-mono text-[11px] tabular-nums text-slate-500">{{ formatIsoTime(row.ev.ts) }}</time>
          <span
            class="rounded border px-1.5 py-px font-mono text-[11px]"
            :class="eventNameBadgeClass(row.ev.eventName)"
          >
            {{ row.ev.eventName }}
          </span>
          <span
            v-if="readStepKind(row.ev.summary)"
            class="rounded border border-sky-500/25 bg-sky-500/10 px-1.5 py-px font-mono text-[11px] text-sky-200/90"
          >
            {{ readStepKind(row.ev.summary) }}
          </span>
          <span
            v-if="readVenue(row.ev.summary)"
            class="rounded border border-violet-500/25 bg-violet-500/10 px-1.5 py-px font-mono text-[11px] text-violet-100/90"
          >
            venue:{{ readVenue(row.ev.summary) }}
          </span>
          <span
            v-if="readCanonicalOp(row.ev.summary)"
            class="rounded border border-fuchsia-500/25 bg-fuchsia-500/10 px-1.5 py-px font-mono text-[11px] text-fuchsia-100/90"
          >
            op:{{ readCanonicalOp(row.ev.summary) }}
          </span>
          <span
            v-if="readRouteBadge(row.ev)"
            class="rounded border border-cyan-500/25 bg-cyan-500/10 px-1.5 py-px text-[11px] font-medium text-cyan-100/90"
          >
            {{ readRouteBadge(row.ev) }}
          </span>
          <span
            v-if="flashRowBadge(row.ev) || flashDocFallbackBadge(row.ev)"
            class="rounded border border-amber-500/25 bg-amber-500/10 px-1.5 py-px text-[11px] font-medium text-amber-100/90"
          >
            {{ flashRowBadge(row.ev) ?? flashDocFallbackBadge(row.ev) }}
          </span>
        </div>
        <p class="mt-1.5 text-sm text-slate-200">
          <template v-if="timelineHeadline(row.ev).trim().length > 0">
            {{ timelineHeadline(row.ev) }}
          </template>
          <span v-else class="text-slate-500">摘要字段见下方原始 JSON。</span>
        </p>
        <div
          v-if="isPromptBindingResolvedEv(row.ev)"
          class="mt-2 rounded-lg border border-violet-500/30 bg-violet-950/30 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-violet-100/95">Prompt 绑定已解析 · binding_resolved</p>
          <p v-if="bindingAssemblySnippet(row.ev)" class="mt-2 break-all font-mono text-[11px] text-slate-400">
            {{ bindingAssemblySnippet(row.ev) }}
          </p>
          <p class="mt-2 break-all font-mono text-[11px] text-slate-500">
            {{ summarizeTradingPromptBinding(row.ev.summary.resolvedPromptBinding ?? row.ev.summary.promptBindingResolved ?? null) }}
          </p>
        </div>
        <div
          v-if="isSkillSpecReadEv(row.ev)"
          class="mt-2 rounded-lg border border-amber-500/28 bg-amber-950/20 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-amber-100/95">Skill Spec 已加载 · spec_read</p>
          <p v-if="skillSpecReadSnippet(row.ev)" class="mt-2 font-mono text-[11px] text-slate-200">
            {{ skillSpecReadSnippet(row.ev) }}
          </p>
          <p
            v-if="row.ev.summary.specDigest && typeof row.ev.summary.specDigest === 'string'"
            class="mt-1 break-all font-mono text-[10px] text-slate-500"
          >
            digest: {{ row.ev.summary.specDigest }}
          </p>
        </div>
        <div
          v-if="isConfirmationRequiredEv(row.ev)"
          class="mt-2 rounded-lg border border-orange-500/28 bg-orange-950/20 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-orange-100/95">需要用户确认 · confirmation.required</p>
          <p class="mt-1 text-[11px] text-slate-400">
            写路径 Type-A：须在用户确认后继续下单（Telegram 点按或 HTTP 隐式确认路径见后续 step）。
          </p>
        </div>
        <div
          v-if="isMemorySessionClearedEv(row.ev)"
          class="mt-2 rounded-lg border border-sky-500/28 bg-sky-950/25 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-sky-100/95">会话记忆已清空 · STM</p>
          <p class="mt-2 text-[11px] text-slate-400">{{ memoryTimelineHeadline(row.ev) }}</p>
          <p class="mt-2 text-[11px] text-slate-500">{{ MEMORY_STM_CLEAR_USER_HINT }}</p>
        </div>
        <div
          v-if="isMemoryLtmRevokeEv(row.ev)"
          class="mt-2 rounded-lg border border-rose-500/28 bg-rose-950/25 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-rose-100/95">长期记忆撤销请求 · LTM</p>
          <p class="mt-2 text-[11px] text-slate-400">{{ memoryTimelineHeadline(row.ev) }}</p>
          <p class="mt-2 text-[11px] text-slate-500">{{ MEMORY_LTM_REVOKE_USER_HINT }}</p>
        </div>
        <div
          v-if="isMemoryResumeClassifiedEv(row.ev)"
          class="mt-2 rounded-lg border border-teal-500/28 bg-teal-950/25 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-teal-100/95">Resume 分类 · resume_classified</p>
          <dl v-if="resumeClassifiedFromEv(row.ev)" class="mt-2 grid gap-2 sm:grid-cols-2">
            <div>
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">decision</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ zhResumeClassifierDecision(resumeClassifiedFromEv(row.ev)!.decision) }}
              </dd>
            </div>
            <div v-if="resumeClassifiedFromEv(row.ev)!.confidence != null">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">confidence</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ resumeClassifiedFromEv(row.ev)!.confidence }}
              </dd>
            </div>
            <div v-if="resumeClassifiedFromEv(row.ev)!.episodePickReason" class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">episodePickReason</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-400">
                {{ resumeClassifiedFromEv(row.ev)!.episodePickReason }}
              </dd>
            </div>
          </dl>
        </div>
        <div
          v-if="clarifySessionFromEv(row.ev)"
          class="mt-2 rounded-lg border border-amber-500/25 bg-amber-950/20 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-amber-100/95">澄清会话快照</p>
          <dl class="mt-2 grid gap-2 sm:grid-cols-2">
            <div>
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">lifecycleState</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ zhClarifyLifecycleState(String(clarifySessionFromEv(row.ev)!.lifecycleState)) }}
              </dd>
            </div>
            <div v-if="clarifySessionFromEv(row.ev)!.clarifyTurn != null">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">clarifyTurn</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ clarifySessionFromEv(row.ev)!.clarifyTurn }}
              </dd>
            </div>
            <div class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">resolvedSlotsSoFar</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-400">
                {{ formatResolvedSlotsSoFar(clarifySessionFromEv(row.ev)!.resolvedSlotsSoFar) }}
              </dd>
            </div>
            <div v-if="clarifySessionFromEv(row.ev)!.pendingClarifyKind" class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">pendingClarifyKind</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-400">
                {{ clarifySessionFromEv(row.ev)!.pendingClarifyKind }}
              </dd>
            </div>
          </dl>
        </div>
        <div
          v-if="isPromptSnapshotTimelineEv(row.ev)"
          class="mt-2 rounded-lg border border-violet-500/25 bg-violet-950/25 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-violet-100/95">Prompt 快照 · NLU 包（effective 同源）</p>
          <dl class="mt-2 grid gap-x-4 gap-y-2 sm:grid-cols-2">
            <div v-if="row.ev.summary.scenarioId" class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">scenarioId</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">{{ row.ev.summary.scenarioId }}</dd>
            </div>
            <div>
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">promptPackVersion</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-sky-200/90">
                {{ formatPromptPackVersionLabel(row.ev.summary.promptPackVersion) }}
              </dd>
            </div>
            <div v-if="systemPromptBindingBrief(row.ev.summary)">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">system 包</dt>
              <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-200">
                {{ systemPromptBindingBrief(row.ev.summary) }}
              </dd>
            </div>
            <div class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">trade 绑定摘要</dt>
              <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-400">
                {{ summarizeTradingPromptBinding(row.ev.summary.resolvedPromptBinding ?? null) }}
              </dd>
            </div>
          </dl>
          <details
            v-if="row.ev.summary.resolvedPromptBinding != null"
            class="mt-2 rounded border border-violet-800/50 bg-slate-950/50"
          >
            <summary class="cursor-pointer px-2 py-1.5 text-[11px] text-violet-200/90">resolvedPromptBinding（JSON）</summary>
            <pre class="max-h-36 overflow-auto border-t border-violet-900/40 p-2 font-mono text-[10px] text-slate-500">{{
              jsonSnippet({ resolvedPromptBinding: row.ev.summary.resolvedPromptBinding })
            }}</pre>
          </details>
        </div>
        <div
          v-if="isRuntimeClarifyTimelineEv(row.ev)"
          class="mt-2 rounded-lg border border-orange-500/28 bg-orange-950/22 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-orange-100/95">运行时澄清 · runtime_clarify（LLM 润色）</p>
          <dl class="mt-2 grid gap-x-4 gap-y-2 sm:grid-cols-2">
            <div v-if="row.ev.summary.targetScenarioId" class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">targetScenarioId</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">{{ row.ev.summary.targetScenarioId }}</dd>
            </div>
            <div v-if="row.ev.summary.scenarioId">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">scenarioId</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">{{ row.ev.summary.scenarioId }}</dd>
            </div>
            <div v-if="row.ev.summary.outcome">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">outcome</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-300">{{ row.ev.summary.outcome }}</dd>
            </div>
          </dl>
        </div>
        <div
          v-if="isLlmChatFaqTimelineEv(row.ev)"
          class="mt-2 rounded-lg border border-indigo-500/25 bg-indigo-950/20 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-indigo-100/95">LLM · chat.faq 网关</p>
          <dl class="mt-2 grid gap-x-4 gap-y-2 sm:grid-cols-2">
            <div>
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">outcome</dt>
              <dd
                class="mt-0.5 font-mono text-[11px] font-medium"
                :class="llmChatFaqOutcomeClass(row.ev.summary.outcome)"
              >
                {{ formatObsScalar(row.ev.summary.outcome) }}
              </dd>
            </div>
            <div>
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">promptPackVersion</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-sky-200/90">
                {{ formatPromptPackVersionLabel(row.ev.summary.promptPackVersion) }}
              </dd>
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">gatewayModelId</dt>
              <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-200">
                {{ summaryPick(row.ev.summary, 'gatewayModelId') }}
              </dd>
              <template v-if="summaryPick(row.ev.summary, 'gatewayUpstreamModel')">
                <dt class="mt-3 text-[10px] uppercase tracking-wide text-slate-600">gatewayUpstreamModel</dt>
                <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-200">
                  {{ summaryPick(row.ev.summary, 'gatewayUpstreamModel') }}
                </dd>
              </template>
            </div>
            <div v-if="summaryPick(row.ev.summary, 'gatewayProviderId')">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">gatewayProviderId</dt>
              <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-200">
                {{ summaryPick(row.ev.summary, 'gatewayProviderId') }}
              </dd>
            </div>
            <div class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">useArkProtocol</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{
                  row.ev.summary.useArkProtocol === true
                    ? 'true（方舟 /api/v3/responses）'
                    : row.ev.summary.useArkProtocol === false
                      ? 'false（OpenAI 兼容 chat/completions）'
                      : '—'
                }}
              </dd>
            </div>
            <div class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">trade / 闲聊绑定摘要</dt>
              <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-400">
                {{ summarizeTradingPromptBinding(row.ev.summary.resolvedPromptBinding ?? null) }}
              </dd>
            </div>
          </dl>
        </div>
        <div
          v-if="isLlmReadMarketNarrationTimelineEv(row.ev)"
          :class="llmReadMarketNarrationPanelClass(row.ev)"
        >
          <p class="font-medium" :class="llmReadMarketNarrationHeadlineAccentClass(row.ev)">
            {{ llmReadMarketNarrationTitle(row.ev) }}
            <span
              class="ml-1 font-normal font-mono text-[10px]"
              :class="llmReadMarketNarrationStepSpanClass(row.ev)"
            >
              · stepKind:{{ expectedReadMarketStepKindConstant(row.ev.eventName) }}
            </span>
          </p>
          <dl class="mt-2 grid gap-x-4 gap-y-2 sm:grid-cols-2">
            <div>
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">outcome</dt>
              <dd
                class="mt-0.5 font-mono text-[11px] font-medium"
                :class="llmChatFaqOutcomeClass(row.ev.summary.outcome)"
              >
                {{ formatObsScalar(row.ev.summary.outcome) }}
              </dd>
            </div>
            <div>
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">promptPackVersion</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-sky-200/90">
                {{ formatPromptPackVersionLabel(row.ev.summary.promptPackVersion) }}
              </dd>
              <dt class="mt-3 text-[10px] uppercase tracking-wide text-slate-600">gatewayModelId</dt>
              <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-200">
                {{ summaryPick(row.ev.summary, 'gatewayModelId') }}
              </dd>
              <template v-if="summaryPick(row.ev.summary, 'gatewayUpstreamModel')">
                <dt class="mt-3 text-[10px] uppercase tracking-wide text-slate-600">gatewayUpstreamModel</dt>
                <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-200">
                  {{ summaryPick(row.ev.summary, 'gatewayUpstreamModel') }}
                </dd>
              </template>
            </div>
            <div v-if="summaryPick(row.ev.summary, 'gatewayProviderId')">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">gatewayProviderId</dt>
              <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-200">
                {{ summaryPick(row.ev.summary, 'gatewayProviderId') }}
              </dd>
            </div>
            <div class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">useArkProtocol</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{
                  row.ev.summary.useArkProtocol === true
                    ? 'true（方舟 /api/v3/responses）'
                    : row.ev.summary.useArkProtocol === false
                      ? 'false（OpenAI 兼容 chat/completions）'
                      : '—'
                }}
              </dd>
            </div>
            <div class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">trade / 绑定摘要</dt>
              <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-400">
                {{ summarizeTradingPromptBinding(row.ev.summary.resolvedPromptBinding ?? null) }}
              </dd>
            </div>
          </dl>
        </div>
        <div
          v-if="isExchangeReadSummary(row.ev.summary)"
          class="mt-2 rounded-lg border border-cyan-500/25 bg-cyan-950/25 px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-cyan-100/95">只读路由 · exchange_read</p>
          <dl class="mt-2 grid gap-x-4 gap-y-2 sm:grid-cols-2">
            <div v-if="row.ev.summary.transitionTrigger" class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">transitionTrigger</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-cyan-200/90">{{ row.ev.summary.transitionTrigger }}</dd>
            </div>
            <div v-if="row.ev.summary.methodPathSummary">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">methodPathSummary</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">{{ row.ev.summary.methodPathSummary }}</dd>
            </div>
            <div v-if="row.ev.summary.outcome">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">outcome</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">{{ row.ev.summary.outcome }}</dd>
            </div>
            <div v-if="exchangeReadBlockPreview(row.ev.summary)" class="sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">exchangeReadPreviewSummary</dt>
              <dd
                class="mt-0.5 max-h-40 overflow-auto whitespace-pre-wrap break-all font-mono text-[11px] text-slate-200"
              >
                {{ exchangeReadBlockPreview(row.ev.summary) }}
              </dd>
            </div>
            <div v-if="row.ev.summary.appErrorCode">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">appErrorCode</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-rose-200/90">{{ row.ev.summary.appErrorCode }}</dd>
            </div>
            <div v-if="row.ev.summary.httpStatus != null">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">httpStatus</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">{{ row.ev.summary.httpStatus }}</dd>
            </div>
          </dl>
        </div>
        <div
          v-if="row.flash"
          class="mt-2 rounded-lg border border-violet-500/25 bg-violet-500/[0.06] px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-violet-100/95">orderRequest · volume 语义</p>
          <p class="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
            <span
              class="rounded border border-violet-400/35 bg-violet-500/15 px-1.5 py-px font-mono text-[10px] text-violet-100"
            >
              {{ row.flash.fm.volumeSemantics ?? '—' }}
            </span>
            <span v-if="volumeSemanticsZh(row.flash.fm.volumeSemantics)" class="text-[11px] text-slate-400">
              {{ volumeSemanticsZh(row.flash.fm.volumeSemantics) }}
            </span>
          </p>
          <p v-if="row.flash.fm.volumeSemanticsNote" class="mt-1.5 text-[11px] leading-snug text-slate-500">
            {{ row.flash.fm.volumeSemanticsNote }}
          </p>
          <dl class="mt-2 grid gap-x-4 gap-y-1.5 sm:grid-cols-2">
            <div class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">wire volume（API 字段）</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.flash.or.volume) }}
              </dd>
            </div>
            <div class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">baseQtyUserRequested</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.flash.fm.baseQtyUserRequested) }}
              </dd>
            </div>
            <div v-if="row.flash.fm.quoteAmountOnWire != null" class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">quoteAmountOnWire（≈ volume · BUY）</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.flash.fm.quoteAmountOnWire) }}
              </dd>
            </div>
            <div v-if="row.flash.fm.baseQtyOnWire != null" class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">baseQtyOnWire（SELL）</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.flash.fm.baseQtyOnWire) }}
              </dd>
            </div>
            <div v-if="row.flash.fm.lastPriceUsed != null" class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">lastPriceUsed（换算参考价）</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.flash.fm.lastPriceUsed) }}
              </dd>
            </div>
            <div v-if="row.flash.fm.userVolumeInput" class="min-w-0 sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">userVolumeInput</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-400">
                {{ row.flash.fm.userVolumeInput }}
              </dd>
            </div>
          </dl>
        </div>
        <div
          v-if="row.limit"
          class="mt-2 rounded-lg border border-orange-500/25 bg-orange-500/[0.06] px-3 py-2.5 text-xs leading-relaxed text-slate-300"
        >
          <p class="font-medium text-orange-100/95">orderRequest · limitOrderMeta</p>
          <p class="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
            <span
              class="rounded border border-orange-400/35 bg-orange-500/15 px-1.5 py-px font-mono text-[10px] text-orange-100"
            >
              {{ row.limit.lm.volumeSemantics ?? '—' }}
            </span>
            <span v-if="volumeSemanticsZh(row.limit.lm.volumeSemantics)" class="text-[11px] text-slate-400">
              {{ volumeSemanticsZh(row.limit.lm.volumeSemantics) }}
            </span>
          </p>
          <dl class="mt-2 grid gap-x-4 gap-y-1.5 sm:grid-cols-2">
            <div class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">wire volume（LIMIT）</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.limit.or.volume) }}
              </dd>
            </div>
            <div class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">wire price</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.limit.or.price) }}
              </dd>
            </div>
            <div class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">limitPriceUserRequested</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.limit.lm.limitPriceUserRequested) }}
              </dd>
            </div>
            <div class="min-w-0">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">baseQtyUserRequested</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.limit.lm.baseQtyUserRequested) }}
              </dd>
            </div>
            <div class="min-w-0 sm:col-span-2">
              <dt class="text-[10px] uppercase tracking-wide text-slate-600">timeInForce</dt>
              <dd class="mt-0.5 font-mono text-[11px] text-slate-200">
                {{ formatObsScalar(row.limit.lm.timeInForce) }}
              </dd>
            </div>
          </dl>
        </div>
        <p class="mt-0.5 text-xs text-slate-500 font-mono">
          <span v-if="row.ev.executionId">{{ row.ev.executionId }}</span>
          <span v-if="row.ev.userId" class="ml-2">{{ row.ev.userId }}</span>
        </p>
        <details class="group mt-2 rounded border border-slate-800 bg-slate-950/65 transition-colors hover:border-slate-700">
          <summary
            class="cursor-pointer select-none px-3 py-2 text-xs font-medium text-slate-400 transition-colors hover:text-slate-200"
          >
            原始 summary（JSON）
          </summary>
          <pre class="max-h-[220px] overflow-auto border-t border-slate-800/90 p-3 font-mono text-[11px] leading-relaxed text-slate-400">{{
            stringifySummary(row.ev.summary)
          }}</pre>
        </details>
        </div>
      </li>
    </ol>
    </template>
  </div>
</template>
