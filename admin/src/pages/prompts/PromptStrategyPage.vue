<!--
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 治理 16 包 pp-* 列表主键 · 隐藏 superseded legacy · 场景 chip 提示对齐 governance-map（FE_HANDOFF 0030）
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 分页工具条 **`UiSelect size=sm`** + **`ADMIN_TOOLBAR_*`** 与按钮行高对齐
作者: 杨永的Agent
日期: 2026-05-21
修改功能: 列表/抽屉/筛选优先 **`row.title`**（`resolvePromptPackDisplayTitle` · FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 修复新建草稿 scenarioId **UiSelect** 崩溃（禁用 `''` 值 · 改用 `__none__` 哨兵）
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 新建草稿 Modal **空白 / 从模板复制**（`admin-seg`）；场景 **Select** 接 **`GET /agent/scenarios`**；**`sourcePromptPackId`**
作者: 杨永的Agent
日期: 2026-05-20
修改功能: LOCKED 行「编辑」先 fork 再跳转新草稿编辑器（FE_HANDOFF 2026-05-20）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 列表「操作」列表头与单元格右对齐（对齐安全防护页）
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 平台 scenarioId / promptPackId 去 phase1 段（对齐迁移 0019 · FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 页面外层 `AdminPage` 使用 full 宽度，与主内容区 max-w-7xl 对齐（不再 max-w-6xl）
作者: 杨永的Agent
日期: 2026-05-21
修改功能: **`/prompts/editor/:promptPackId`**：`PromptPackEditorPage` · 列表「编辑」跳转；抽屉仅详情只读 · `usePromptPackEditor.ts`
日期: 2026-05-21
修改功能: 列表 **详情 / 编辑** · 行点开详情 · `mode=edit` 已由独立编辑页承接（本轮合并：编辑改走 `/prompts/editor/`）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: **`variableSchema`** JSON 编辑 + Phase1 **平台占位符白名单**只读提示；PATCH 与 **messages** 分栏保存（FE_HANDOFF AC-09f）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **Prompt 列表 · 操作「查看」** 改用 **`UiTableAction`**（眼睛图标 + outline）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 编辑抽屉 **`admin-drawer-*`** backdrop 渐入 + 侧栏自右滑入（与全局壳层对齐）
作者: 杨永的Agent
日期: 2026-05-17
修改功能: 新建草稿 POST、抽屉内 DRAFT 发布 POST …/publish；列表 Query 与类型/阶段筛选对齐；409/业务码错误说明
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import {
  createPromptPack,
  forkPromptPack,
  getPromptPack,
  listPromptPacks,
  resolvePromptPackDisplayTitle,
  type CreatePromptPackBody,
  type ListPromptPacksQuery,
  type PromptPackDetail,
  type PromptPackSummary,
} from '@/shared/api/admin-prompt-packs'
import { getAgentScenarios, type AgentScenarioListItem } from '@/shared/api/agent-runtime'
import { PHASE1_PLATFORM_PROMPT_PLACEHOLDER_EXAMPLES } from '@/shared/copy/prompt-platform-placeholders'
import { AppError } from '@/shared/api/errors'
import { adminNotifyManualRefresh, adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminPageHeader from '@/shared/ui/AdminPageHeader.vue'
import UiButton from '@/shared/ui/UiButton.vue'
import UiInput from '@/shared/ui/UiInput.vue'
import UiModal from '@/shared/ui/UiModal.vue'
import UiSelect, { type UiSelectOption } from '@/shared/ui/UiSelect.vue'
import UiTableAction from '@/shared/ui/UiTableAction.vue'
import { ADMIN_TOOLBAR_CLUSTER_CLASS, ADMIN_TOOLBAR_META_CLASS } from '@/shared/ui/toolbar-controls'

import { explainPromptPackApiError } from '@/pages/prompts/usePromptPackEditor'
import {
  ANALYSIS_CORE_SCENARIO_ID,
  filterSupersededLegacyPacks,
  governancePackHintForScenarioChip,
} from '@/shared/lib/prompt-governance-catalog'

type GovernanceKindFilter = '__all__' | 'SYSTEM' | 'SAFETY' | 'TRADING' | 'ANALYSIS'
type StrategyDraftPackType = 'SYSTEM' | 'TRADING' | 'ANALYSIS'
type DraftCreateMode = 'blank' | 'template'
type LifecycleListFilter =
  | '__all__'
  | 'draft'
  | 'published'
  | 'locked'
  | 'iterate'
  | 'deprecated'

/** 策略页新建草稿可选类型（不含 SAFETY · 走安全防护专区） */
const STRATEGY_DRAFT_PACK_TYPE_OPTIONS: UiSelectOption[] = [
  { value: 'SYSTEM', label: '系统' },
  { value: 'TRADING', label: '交易' },
  { value: 'ANALYSIS', label: '分析' },
]

const DRAFT_CREATE_MODE_SEGMENTS: { key: DraftCreateMode; label: string }[] = [
  { key: 'blank', label: '空白草稿' },
  { key: 'template', label: '从模板复制' },
]

/** UiSelect / Reka 禁止 `value: ''` · SYSTEM 可选场景用哨兵 */
const DRAFT_SCENARIO_NONE = '__none__'
const DRAFT_TEMPLATE_NONE = '__no_template__'

/** 编排场景 category · TRADING/ANALYSIS 场景 Select 筛选 */
const OPERATIONAL_SCENARIO_CATEGORIES = new Set([
  'read',
  'trade',
  'wealth',
  'chat',
  'margin',
  'automation',
])

/** 平台拼装种子 scenarioId · 迁移 `0013` 写入、`0019` 去 phase1 段 · BACKEND_SPEC §11 */
const PLATFORM_PROMPT_ASSEMBLY_SEEDS: { scenarioId: string; shortLabel: string }[] = [
  { scenarioId: 'agent.runtime.platform_system', shortLabel: 'SYSTEM 平台' },
  { scenarioId: 'agent.runtime.platform_safety', shortLabel: 'SAFETY 平台' },
  { scenarioId: 'chat.faq', shortLabel: 'TRADING · FAQ' },
]

const PLATFORM_ASSEMBLY_SCENARIO_ID_SET = new Set(PLATFORM_PROMPT_ASSEMBLY_SEEDS.map((s) => s.scenarioId))

const READ_SCENARIO_CHIP_ROWS = [
  { scenarioId: 'read.market.ticker', shortLabel: 'read.market.ticker（读侧）', tag: '0030' as const },
  { scenarioId: 'read.market.depth', shortLabel: 'read.market.depth（读侧）', tag: '0030' as const },
  { scenarioId: 'read.market.trades', shortLabel: 'read.market.trades（读侧）', tag: '0030' as const },
  { scenarioId: 'read.account.balance', shortLabel: 'read.account.balance（读侧）', tag: '0030' as const },
  { scenarioId: 'wealth.holdings_read', shortLabel: 'wealth.holdings_read（读侧）', tag: '0030' as const },
] as const

const PROMPT_SCENARIO_EXACT_CHIP_ROWS = [
  ...PLATFORM_PROMPT_ASSEMBLY_SEEDS.map((s) => ({
    scenarioId: s.scenarioId,
    shortLabel: s.shortLabel,
    tag: '0013' as const,
    packHint: governancePackHintForScenarioChip(s.scenarioId),
  })),
  ...READ_SCENARIO_CHIP_ROWS.map((row) => ({
    ...row,
    packHint: governancePackHintForScenarioChip(row.scenarioId),
  })),
]

const GOVERNANCE_KIND_OPTIONS: UiSelectOption[] = [
  { value: '__all__', label: '全部类型' },
  { value: 'SYSTEM', label: '系统' },
  { value: 'SAFETY', label: '安全防护' },
  { value: 'TRADING', label: '交易' },
  { value: 'ANALYSIS', label: '分析' },
]

const LIFECYCLE_OPTIONS: UiSelectOption[] = [
  { value: '__all__', label: '全部阶段' },
  { value: 'draft', label: '草稿线（DRAFT）' },
  { value: 'published', label: '已发布（PUBLISHED）' },
  { value: 'locked', label: '已锁定（LOCKED）' },
  { value: 'iterate', label: '生效包·有未发草稿' },
  { value: 'deprecated', label: '下线标记' },
]

const PAGE_SIZE_OPTIONS: UiSelectOption[] = [
  { value: '10', label: '每页 10 条' },
  { value: '20', label: '每页 20 条' },
  { value: '50', label: '每页 50 条' },
]

/** 抽屉说明占位符字面量 · 避免 template `\{\{\}\}` 嵌套触发解析歧义 */
const DOC_PLACEHOLDER_EXAMPLE = '{{ slug }}'
const DOC_EMPTY_SCHEMA_OBJECT = '{}'

const route = useRoute()
const router = useRouter()

const items = ref<PromptPackSummary[]>([])
const listLoading = ref(false)
const listError = ref<string | null>(null)
const forkPackIdLoading = ref<string | null>(null)

const promptKeyword = ref('')
const governanceKind = ref<GovernanceKindFilter>('__all__')
const lifecycleFilter = ref<LifecycleListFilter>('__all__')

let keywordDebounceTimer: ReturnType<typeof setTimeout> | null = null

const draftModalOpen = ref(false)

const draftCreateMode = ref<DraftCreateMode>('blank')
const draftPackType = ref<StrategyDraftPackType>('TRADING')
const draftScenarioId = ref(DRAFT_SCENARIO_NONE)
const draftPromptPackId = ref('')
const draftSourcePackId = ref(DRAFT_TEMPLATE_NONE)
const scenarioRegistry = ref<AgentScenarioListItem[]>([])
const scenariosLoading = ref(false)
const createLoading = ref(false)
const createError = ref<string | null>(null)

const detail = ref<PromptPackDetail | null>(null)
const detailLoading = ref(false)
const detailError = ref<string | null>(null)
const messagesRaw = ref('')
const variableSchemaRaw = ref('{}')

const pageSizeStr = ref('10')
const pageIndex = ref(1)

const pageSizeNum = computed(() => {
  const n = Number(pageSizeStr.value)
  return Number.isFinite(n) && n > 0 ? n : 10
})

const packIdFromRoute = computed(() => {
  const raw = route.query.pack
  const s = Array.isArray(raw) ? raw[0] : raw
  return typeof s === 'string' && s.trim() !== '' ? s.trim() : ''
})

/** 抽屉仅 **详情**：编辑走独立页 **`/prompts/editor/:promptPackId`**（与原型 `PromptPacksTable` 一致） */
const drawerOpen = computed(() => Boolean(packIdFromRoute.value))

function fmtJson(v: unknown): string {
  return JSON.stringify(v, null, 2)
}

function normalizeDetailVariableSchema(d: PromptPackDetail | null): Record<string, unknown> {
  if (!d?.variableSchema || typeof d.variableSchema !== 'object' || Array.isArray(d.variableSchema))
    return {}
  return { ...(d.variableSchema as Record<string, unknown>) }
}



function zhPromptPackKind(k: string): string {
  const m: Record<string, string> = {
    SYSTEM: '系统',
    TRADING: '交易',
    ANALYSIS: '分析',
    SAFETY: '安全防护',
  }
  return m[k] ?? k
}

function zhLifecycleRaw(lc: string | null | undefined): string {
  const u = (lc ?? '').toUpperCase()
  const map: Record<string, string> = {
    DRAFT: '草稿',
    PUBLISHED: '已发布',
    LOCKED: '已锁定',
    DEPRECATED: '已下线',
    DISABLED: '已停用',
  }
  return (map[u] ?? u) || '—'
}

function kindBadgeClass(k: string): string {
  if (k === 'SYSTEM') return 'border-slate-600/70 bg-slate-800/60 text-slate-200'
  if (k === 'SAFETY') return 'border-rose-600/45 bg-rose-950/30 text-rose-200/90'
  if (k === 'TRADING') return 'border-amber-600/45 bg-amber-950/35 text-amber-200/95'
  if (k === 'ANALYSIS') return 'border-cyan-700/45 bg-cyan-950/25 text-cyan-200/90'
  return 'border-slate-700 bg-slate-900/50 text-slate-400'
}

/** 列表「阶段」列：Phase1 仅 lifecycle 字符串，无 hasDraft 时不展示「迭代」实质数据 */
function lifecyclePhasePresentation(row: PromptPackSummary): { label: string; badgeClass: string } {
  const lc = (row.lifecycle ?? '').toUpperCase()
  if (lc === 'DEPRECATED' || lc === 'DISABLED') {
    return { label: '下线中', badgeClass: 'border-slate-600 bg-slate-800/50 text-slate-400' }
  }
  if (lc === 'DRAFT') return { label: '草稿线', badgeClass: 'border-slate-600 bg-slate-900/60 text-slate-300' }
  if (lc === 'LOCKED') return { label: '已锁定包', badgeClass: 'border-rose-700/40 bg-rose-950/25 text-rose-200/90' }
  if (lc === 'PUBLISHED') return { label: '已发布', badgeClass: 'border-emerald-600/45 bg-emerald-950/30 text-emerald-200/95' }
  return { label: zhLifecycleRaw(row.lifecycle), badgeClass: 'border-slate-700 bg-slate-900/40 text-slate-500' }
}



function readKindFromRoute(): GovernanceKindFilter {
  const raw = String(route.query.kind ?? '').toUpperCase()
  if (raw === 'SYSTEM' || raw === 'SAFETY' || raw === 'TRADING' || raw === 'ANALYSIS') return raw
  return '__all__'
}

function readLifeFromRoute(): LifecycleListFilter {
  const raw = String(route.query.life ?? '').toLowerCase()
  if (
    raw === 'draft' ||
    raw === 'published' ||
    raw === 'locked' ||
    raw === 'iterate' ||
    raw === 'deprecated'
  ) {
    return raw as LifecycleListFilter
  }
  return '__all__'
}

function keywordFromRoute(): string {
  const q = route.query.q
  const s = Array.isArray(q) ? q[0] : q
  if (typeof s === 'string' && s.trim()) return s.trim()
  const id = route.query.id
  const idS = Array.isArray(id) ? id[0] : id
  if (typeof idS === 'string' && idS.trim()) return idS.trim()
  const title = route.query.title
  const tS = Array.isArray(title) ? title[0] : title
  if (typeof tS === 'string' && tS.trim()) return tS.trim()
  return ''
}



/** 服务端列表 **精确** scenarioId（`GET …/prompt-packs?scenarioId=`）*/
const scenarioQueryParam = computed(() => {
  const raw = route.query.scenario
  const s = Array.isArray(raw) ? raw[0] : raw
  return typeof s === 'string' ? s.trim() : ''
})

function buildListQuery(): ListPromptPacksQuery | undefined {
  const q: ListPromptPacksQuery = {}
  if (governanceKind.value !== '__all__') {
    q.promptPackType = governanceKind.value
  }
  const life = lifecycleFilter.value
  if (life === 'draft') q.lifecycle = 'DRAFT'
  else if (life === 'published') q.lifecycle = 'PUBLISHED'
  else if (life === 'locked') q.lifecycle = 'LOCKED'
  const sc = scenarioQueryParam.value
  if (sc) q.scenarioId = sc
  if (Object.keys(q).length === 0) return undefined
  return q
}

function mergeQuery(updates: Record<string, string | undefined>) {
  const next = { ...route.query } as Record<string, string | string[] | undefined>
  for (const [k, v] of Object.entries(updates)) {
    if (v === undefined || v === '') delete next[k]
    else next[k] = v
  }
  void router.replace({ query: next })
}

function scheduleKeywordRouteSync() {
  if (keywordDebounceTimer !== null) clearTimeout(keywordDebounceTimer)
  keywordDebounceTimer = setTimeout(() => {
    keywordDebounceTimer = null
    const trim = promptKeyword.value.trim()
    mergeQuery({
      q: trim || undefined,
      id: undefined,
      title: undefined,
    })
  }, 420)
}

/**
 * 平台 SAFETY **种子包**在正常列表可见；其余 SAFETY 仍建议走「安全防护」专区。
 * 带 **scenarioId** 服务端筛选时：展示服务端返回的 SAFETY 行。
 */
const listSourceRows = computed(() => {
  const afterLegacy = filterSupersededLegacyPacks(items.value, lifecycleFilter.value)
  return afterLegacy.filter((p) => {
    const t = String(p.promptPackType ?? '').toUpperCase()
    if (t !== 'SAFETY') return true
    if (scenarioQueryParam.value) return true
    const sid = (p.scenarioId ?? '').trim()
    return PLATFORM_ASSEMBLY_SCENARIO_ID_SET.has(sid)
  })
})

function matchesLifecycleFilter(row: PromptPackSummary, f: LifecycleListFilter): boolean {
  if (f === '__all__') return true
  const lc = (row.lifecycle ?? '').toUpperCase()
  if (f === 'deprecated') return lc === 'DEPRECATED' || lc === 'DISABLED'
  if (f === 'draft') return lc === 'DRAFT'
  if (f === 'published') return lc === 'PUBLISHED'
  if (f === 'locked') return lc === 'LOCKED'
  if (f === 'iterate') return false
  return true
}

const queryFilteredRows = computed(() => {
  const kq = promptKeyword.value.trim().toLowerCase()
  let rows = listSourceRows.value
  if (governanceKind.value !== '__all__') {
    rows = rows.filter((p) => String(p.promptPackType ?? '').toUpperCase() === governanceKind.value)
  }
  rows = rows.filter((p) => matchesLifecycleFilter(p, lifecycleFilter.value))
  if (kq) {
    rows = rows.filter((p) => {
      const sid = (p.scenarioId ?? '').toLowerCase()
      const pid = p.promptPackId.toLowerCase()
      const title = (p.title ?? '').toLowerCase()
      return pid.includes(kq) || sid.includes(kq) || title.includes(kq)
    })
  }
  return rows
})

const totalFiltered = computed(() => queryFilteredRows.value.length)
const totalPages = computed(() => Math.max(1, Math.ceil(totalFiltered.value / pageSizeNum.value)))

const pagedRows = computed(() => {
  const ps = pageSizeNum.value
  const start = (pageIndex.value - 1) * ps
  return queryFilteredRows.value.slice(start, start + ps)
})

watch([totalFiltered, pageSizeNum], () => {
  if (pageIndex.value > totalPages.value) pageIndex.value = totalPages.value
})

watch(pageSizeStr, () => {
  pageIndex.value = 1
})

watch(
  () => `${promptKeyword.value}\t${governanceKind.value}\t${lifecycleFilter.value}\t${scenarioQueryParam.value}`,
  () => {
    pageIndex.value = 1
  },
)

watch(governanceKind, (k) => {
  mergeQuery({ kind: k === '__all__' ? undefined : k })
})

watch(lifecycleFilter, (life) => {
  mergeQuery({ life: life === '__all__' ? undefined : life })
})

const routeListKey = computed(() => {
  const rawK = route.query.kind
  const k = Array.isArray(rawK) ? rawK[0] : rawK
  const rawL = route.query.life
  const l = Array.isArray(rawL) ? rawL[0] : rawL
  const rawS = route.query.scenario
  const sc = Array.isArray(rawS) ? rawS[0] : rawS
  return `${typeof k === 'string' ? k : ''}\t${typeof l === 'string' ? l : ''}\t${typeof sc === 'string' ? sc : ''}`
})

watch(
  routeListKey,
  () => {
    applyRouteToFilters()
    void refreshList()
  },
  { immediate: true },
)

watch(promptKeyword, () => {
  scheduleKeywordRouteSync()
})

watch(draftModalOpen, (open) => {
  if (!open) return
  createError.value = null
  draftPackType.value = 'SYSTEM'
  draftScenarioId.value = ''
  draftPromptPackId.value = ''
})

watch(packIdFromRoute, async (id) => {
  detail.value = null
  messagesRaw.value = ''
  variableSchemaRaw.value = '{}'
  detailError.value = null
  if (!id) return
  detailLoading.value = true
  try {
    const d = await getPromptPack(id)
    detail.value = d
    messagesRaw.value = fmtJson(d.messages)
    variableSchemaRaw.value = fmtJson(normalizeDetailVariableSchema(d))
  } catch (e) {
    detailError.value = e instanceof AppError ? e.message : '加载详情失败'
    mergeQuery({ pack: undefined })
  } finally {
    detailLoading.value = false
  }
})

function applyRouteToFilters() {
  governanceKind.value = readKindFromRoute()
  lifecycleFilter.value = readLifeFromRoute()
  promptKeyword.value = keywordFromRoute()
}

watch(
  () => route.query,
  () => {
    applyRouteToFilters()
  },
)

async function refreshList(toastOnSuccess = false) {
  listError.value = null
  listLoading.value = true
  try {
    const res = await listPromptPacks(buildListQuery())
    items.value = res.items ?? []
    const pid = packIdFromRoute.value
    if (pid && !items.value.some((r) => r.promptPackId === pid)) {
      mergeQuery({ pack: undefined })
    }
    adminNotifyManualRefresh(toastOnSuccess, { ok: true, successMessage: '已刷新列表' })
  } catch (e) {
    items.value = []
    const msg = e instanceof AppError ? e.message : '加载列表失败'
    listError.value = msg
    adminNotifyManualRefresh(toastOnSuccess, {
      ok: false,
      successMessage: '已刷新列表',
      errorMessage: msg,
    })
  } finally {
    listLoading.value = false
  }
}

function openPackDetail(row: PromptPackSummary) {
  mergeQuery({ pack: row.promptPackId })
}

function goToPackEditor(id: string) {
  void router.push({ name: 'prompts.editor', params: { promptPackId: id } })
}

async function openPackEdit(row: PromptPackSummary) {
  const lc = String(row.lifecycle ?? '').toUpperCase()
  if (lc === 'LOCKED') {
    forkPackIdLoading.value = row.promptPackId
    listError.value = null
    try {
      const next = await forkPromptPack(row.promptPackId)
      goToPackEditor(next.promptPackId)
    } catch (e) {
      listError.value = explainPromptPackApiError(e, '复制草稿失败')
    } finally {
      forkPackIdLoading.value = null
    }
    return
  }
  goToPackEditor(row.promptPackId)
}


function closeDrawer() {
  mergeQuery({ pack: undefined })
}

function applyPhase1AssemblyScenario(scenarioId: string) {
  const govId = governancePackHintForScenarioChip(scenarioId)
  if (govId === 'pp-analysis-core') {
    mergeQuery({
      scenario: ANALYSIS_CORE_SCENARIO_ID,
      kind: 'ANALYSIS',
      q: undefined,
    })
    return
  }
  mergeQuery({
    scenario: scenarioId || undefined,
    kind: undefined,
  })
}

function clearScenarioScope() {
  mergeQuery({ scenario: undefined })
}

function onResetQuery() {
  promptKeyword.value = ''
  governanceKind.value = '__all__'
  lifecycleFilter.value = '__all__'
  mergeQuery({
    q: undefined,
    id: undefined,
    title: undefined,
    kind: undefined,
    life: undefined,
    scenario: undefined,
    pack: undefined,
  })
}

function scenariosForPackType(ptype: StrategyDraftPackType): AgentScenarioListItem[] {
  const all = scenarioRegistry.value
  if (ptype === 'SYSTEM') {
    return all
      .filter((s) => s.scenarioId.startsWith('agent.runtime.'))
      .sort((a, b) => a.scenarioId.localeCompare(b.scenarioId))
  }
  return all
    .filter((s) => !s.scenarioId.startsWith('agent.runtime.'))
    .filter((s) => s.readiness === 'ready' || s.readiness === 'phase1_stub')
    .filter((s) => s.category && OPERATIONAL_SCENARIO_CATEGORIES.has(s.category))
    .sort((a, b) => a.scenarioId.localeCompare(b.scenarioId))
}

function pickFirstScenarioId(ptype: StrategyDraftPackType): string | null {
  return scenariosForPackType(ptype)[0]?.scenarioId ?? null
}

function draftScenarioIdForSubmit(selectValue: string): string {
  return selectValue === DRAFT_SCENARIO_NONE ? '' : selectValue.trim()
}

/** 保证 v-model 始终落在 options 内（避免 Reka Select 读 null.type 崩溃） */
function resolveDraftScenarioSelectValue(raw: string, ptype: StrategyDraftPackType): string {
  const sid = raw.trim()
  const allowed = new Set(scenariosForPackType(ptype).map((s) => s.scenarioId))
  if (sid && sid !== DRAFT_SCENARIO_NONE && allowed.has(sid)) return sid
  if (ptype === 'SYSTEM') return DRAFT_SCENARIO_NONE
  return pickFirstScenarioId(ptype) ?? DRAFT_SCENARIO_NONE
}

const draftScenarioOptions = computed<UiSelectOption[]>(() => {
  const rows = scenariosForPackType(draftPackType.value)
  const opts = rows.map((s) => ({
    value: s.scenarioId,
    label: `${s.title?.trim() || s.scenarioId} · ${s.category ?? '—'} · ${s.readiness}`,
  }))
  if (draftPackType.value === 'SYSTEM') {
    return [{ value: DRAFT_SCENARIO_NONE, label: '无（留空）' }, ...opts]
  }
  if (opts.length === 0) {
    return [{ value: DRAFT_SCENARIO_NONE, label: '（场景寄存器暂无可用项）', disabled: true }]
  }
  return opts
})

const templatePackOptions = computed<UiSelectOption[]>(() => {
  const rows = [...listSourceRows.value]
    .sort((a, b) => {
      const aGov = a.promptPackId.startsWith('pp-') ? 0 : 1
      const bGov = b.promptPackId.startsWith('pp-') ? 0 : 1
      return aGov - bGov || a.promptPackId.localeCompare(b.promptPackId)
    })
    .map((p) => ({
      value: p.promptPackId,
      label: `${resolvePromptPackDisplayTitle(p)} · ${zhPromptPackKind(String(p.promptPackType ?? ''))} · ${p.promptPackId}`,
    }))
  if (rows.length === 0) {
    return [{ value: DRAFT_TEMPLATE_NONE, label: '（列表暂无包）', disabled: true }]
  }
  return rows
})

const draftScenarioRequired = computed(
  () => draftPackType.value === 'TRADING' || draftPackType.value === 'ANALYSIS',
)

const draftSubmitLabel = computed(() =>
  draftCreateMode.value === 'template' ? '复制并打开' : '创建并打开',
)

async function loadScenarioRegistry() {
  scenariosLoading.value = true
  try {
    const res = await getAgentScenarios()
    scenarioRegistry.value = res.scenarios ?? []
  } catch {
    scenarioRegistry.value = []
  } finally {
    scenariosLoading.value = false
    draftScenarioId.value = resolveDraftScenarioSelectValue(draftScenarioId.value, draftPackType.value)
  }
}

function resetDraftForm() {
  draftCreateMode.value = 'blank'
  draftPackType.value = 'TRADING'
  draftPromptPackId.value = ''
  draftSourcePackId.value = listSourceRows.value[0]?.promptPackId ?? DRAFT_TEMPLATE_NONE
  draftScenarioId.value = resolveDraftScenarioSelectValue(DRAFT_SCENARIO_NONE, 'TRADING')
  createError.value = null
}

watch(draftModalOpen, (open) => {
  if (!open) return
  resetDraftForm()
  void loadScenarioRegistry()
})

watch(draftPackType, (ptype) => {
  draftScenarioId.value = resolveDraftScenarioSelectValue(draftScenarioId.value, ptype)
})

watch(draftSourcePackId, (id) => {
  if (id === DRAFT_TEMPLATE_NONE) return
  const row = listSourceRows.value.find((p) => p.promptPackId === id)
  if (!row) return
  const t = String(row.promptPackType ?? '').toUpperCase()
  if (t === 'SYSTEM' || t === 'TRADING' || t === 'ANALYSIS') {
    draftPackType.value = t
  }
  const sid = (row.scenarioId ?? '').trim()
  draftScenarioId.value = resolveDraftScenarioSelectValue(sid || DRAFT_SCENARIO_NONE, draftPackType.value)
})

async function submitCreateDraft() {
  createError.value = null

  if (draftCreateMode.value === 'template') {
    if (!draftSourcePackId.value.trim() || draftSourcePackId.value === DRAFT_TEMPLATE_NONE) {
      createError.value = '请选择一个已有 Prompt 作为模板'
      return
    }
  }

  const ptype = draftPackType.value
  const sid = draftScenarioIdForSubmit(draftScenarioId.value)
  if ((ptype === 'TRADING' || ptype === 'ANALYSIS') && !sid) {
    createError.value = `${ptype} 类草稿须选择 scenarioId（场景寄存器）`
    return
  }

  createLoading.value = true
  try {
    const body: CreatePromptPackBody = {
      promptPackType: ptype,
      scenarioId: sid || undefined,
      promptPackId: draftPromptPackId.value.trim() || undefined,
    }
    if (draftCreateMode.value === 'template') {
      body.sourcePromptPackId = draftSourcePackId.value.trim()
    }
    const created = await createPromptPack(body)
    draftModalOpen.value = false
    await refreshList()
    goToPackEditor(created.promptPackId)
  } catch (e) {
    createError.value = explainPromptPackApiError(e, '创建草稿失败')
  } finally {
    createLoading.value = false
  }
}

function prevPage() {
  pageIndex.value = Math.max(1, pageIndex.value - 1)
}

function nextPage() {
  pageIndex.value = Math.min(totalPages.value, pageIndex.value + 1)
}
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="提示词治理"
      description="类型列为拼装大类（PromptPackType）。"
    >
      <template #dev>
        Admin
        <code class="text-slate-500">GET/POST/PATCH /api/v1/admin/prompt-packs</code>（Body：
        <code class="text-slate-600">messages</code> /
        <code class="text-slate-600">variableSchema</code> 至少其一）· POST
        <code class="text-slate-500">/{id}/publish</code>
        · 运行时只读
        <code class="text-slate-500">GET /api/v1/internal/prompts/effective?scenarioId=</code>
      </template>
      <template #extra>
        <p class="text-sm">
          <RouterLink
            class="font-medium text-emerald-400/95 underline-offset-4 transition-colors duration-200 ease-ui hover:text-emerald-300 hover:underline"
            to="/ai-settings"
          >
            模型与网关默认
          </RouterLink>
          <span class="text-slate-600"> · </span>
          <RouterLink
            class="font-medium text-slate-400 underline-offset-4 transition-colors duration-200 ease-ui hover:text-slate-200 hover:underline"
            to="/prompts/safety"
          >
            安全防护
          </RouterLink>
        </p>
      </template>
      <template #actions>
        <UiButton type="button" size="sm" @click="draftModalOpen = true">新建草稿</UiButton>
        <UiButton type="button" variant="secondary" size="sm" :loading="listLoading" @click="refreshList(true)">
          刷新列表
        </UiButton>
      </template>
    </AdminPageHeader>

    <div
      v-if="listError"
      class="rounded-[var(--radius-ui-lg)] border-l-[3px] border-amber-500/70 bg-amber-950/20 px-4 py-3 text-[13px] text-amber-100"
      role="status"
    >
      {{ listError }}
    </div>

    <section class="admin-panel px-3 py-3 sm:px-4 sm:py-3">
      <h2 class="text-xs font-semibold uppercase tracking-wide text-slate-400">查询条件</h2>
      <div class="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-12 lg:gap-x-4">
        <div class="lg:col-span-6">
          <UiInput
            v-model="promptKeyword"
            label="Prompt ID / 名称"
            placeholder="匹配 title、Prompt ID 或 scenarioId（模糊）"
            autocomplete="off"
          />
          <p class="mt-1 text-[11px] text-slate-600">地址栏同步为 <span class="font-mono">q</span>（防抖）</p>
        </div>
        <div class="lg:col-span-6">
          <UiSelect
            v-model="governanceKind"
            label="类型"
            :options="GOVERNANCE_KIND_OPTIONS"
            placeholder="请选择类型"
          />
          <p class="mt-1 text-[11px] text-slate-600">OpenAPI：<span class="font-mono">PromptPackType</span></p>
        </div>
        <div class="lg:col-span-6">
          <UiSelect
            v-model="lifecycleFilter"
            label="生命周期阶段"
            :options="LIFECYCLE_OPTIONS"
            placeholder="全部阶段"
          />
        </div>
        <div class="flex flex-col gap-2 border-t border-slate-800/65 pt-3 sm:col-span-2 lg:col-span-12">
          <p class="text-[11px] leading-relaxed text-slate-500">
            治理 **16 包**（迁移 <span class="font-mono text-slate-600">0030</span>）：编辑主键为
            <span class="font-mono text-emerald-200/80">pp-*</span>（如
            <span class="font-mono text-slate-600">pp-system-core</span>、
            <span class="font-mono text-slate-600">pp-analysis-core</span>）；旧
            <span class="font-mono text-slate-600">pack_*</span> 已下线，可在「下线标记」筛选查看。
            读侧场景 chip 仍按 <span class="font-mono text-slate-600">scenarioId</span> 精确筛选，列表以 API 返回的治理包为准。
          </p>
          <div class="flex flex-wrap items-center gap-2">
            <button
              v-for="row in PROMPT_SCENARIO_EXACT_CHIP_ROWS"
              :key="row.scenarioId"
              type="button"
              class="rounded-full border px-2.5 py-1 text-[11px] font-medium transition-colors duration-200 ease-ui"
              :class="
                scenarioQueryParam === row.scenarioId
                  ? 'border-sky-500/55 bg-sky-950/40 text-sky-100'
                  : 'border-slate-700 bg-slate-900/55 text-slate-400 hover:border-slate-600 hover:text-slate-200'
              "
              :title="
                row.packHint
                  ? `${row.scenarioId} · 治理包 ${row.packHint} · ${row.tag}`
                  : `${row.scenarioId} · ${row.tag}`
              "
              @click="applyPhase1AssemblyScenario(row.scenarioId)"
            >
              {{ row.shortLabel }}
            </button>
            <UiButton
              v-if="scenarioQueryParam"
              type="button"
              variant="ghost"
              size="sm"
              class="text-slate-500"
              @click="clearScenarioScope"
            >
              清除 scenario 筛选
            </UiButton>
          </div>
          <p v-if="scenarioQueryParam" class="break-all font-mono text-[10px] leading-relaxed text-slate-600">
            当前：<span class="text-slate-500">{{ scenarioQueryParam }}</span>
          </p>
        </div>
      </div>
    </section>

    <section class="admin-panel overflow-hidden">
      <template v-if="listLoading && items.length === 0">
        <div class="space-y-3 px-4 py-8" aria-busy="true">
          <div class="h-10 animate-pulse rounded-md bg-slate-800/70" />
          <div class="h-32 animate-pulse rounded-md bg-slate-800/40" />
        </div>
      </template>
      <template v-else-if="!listLoading && items.length === 0">
        <div class="px-6 py-14 text-center">
          <p class="text-sm text-slate-500">服务端未返回任何 Prompt 包</p>
          <UiButton type="button" class="mt-4" @click="draftModalOpen = true">新建草稿</UiButton>
        </div>
      </template>
      <template v-else-if="queryFilteredRows.length === 0">
        <div class="px-6 py-14 text-center">
          <p class="text-sm text-slate-500">没有符合当前筛选条件的条目</p>
          <div class="mt-4 flex flex-wrap justify-center gap-2">
            <UiButton type="button" @click="onResetQuery">清空筛选</UiButton>
            <UiButton type="button" variant="secondary" @click="draftModalOpen = true">新建草稿</UiButton>
          </div>
        </div>
      </template>
      <template v-else>
        <div class="overflow-x-auto border-b border-slate-800/80">
          <table class="min-w-[720px] w-full border-collapse text-left text-sm">
            <thead>
              <tr class="border-b border-slate-800/90 text-xs font-medium uppercase tracking-wide text-slate-500">
                <th class="whitespace-nowrap px-4 py-3">Prompt ID</th>
                <th class="whitespace-nowrap px-4 py-3">Prompt 名称</th>
                <th class="whitespace-nowrap px-4 py-3">类型</th>
                <th class="whitespace-nowrap px-4 py-3">版本</th>
                <th class="whitespace-nowrap px-4 py-3">状态</th>
                <th class="whitespace-nowrap px-4 py-3">阶段</th>
                <th class="whitespace-nowrap px-4 py-3 text-right text-slate-600">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/80">
              <tr
                v-for="row in pagedRows"
                :key="row.promptPackId"
                class="cursor-pointer transition-colors duration-200 ease-ui hover:bg-slate-800/25"
                @click="openPackDetail(row)"
              >
                <td class="max-w-[14rem] px-4 py-3 font-mono text-xs text-emerald-200/90">
                  <span class="break-all">{{ row.promptPackId }}</span>
                </td>
                <td class="max-w-[12rem] px-4 py-3 font-medium text-slate-200">
                  <span class="line-clamp-2">{{ resolvePromptPackDisplayTitle(row) }}</span>
                </td>
                <td class="whitespace-nowrap px-4 py-3">
                  <span
                    class="inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium"
                    :class="kindBadgeClass(String(row.promptPackType ?? ''))"
                  >
                    {{ zhPromptPackKind(String(row.promptPackType ?? '')) }}
                  </span>
                </td>
                <td class="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-300">
                  {{ row.promptPackVersion != null ? `v${row.promptPackVersion}` : '—' }}
                  <span
                    v-if="String(row.lifecycle ?? '').toUpperCase() === 'PUBLISHED'"
                    class="ml-2 inline-flex rounded border border-emerald-600/40 bg-emerald-950/35 px-1.5 py-0 text-[10px] font-medium text-emerald-300/95"
                  >
                    生效
                  </span>
                </td>
                <td class="whitespace-nowrap px-4 py-3 text-slate-400">{{ zhLifecycleRaw(row.lifecycle) }}</td>
                <td class="whitespace-nowrap px-4 py-3">
                  <span
                    class="inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium"
                    :class="lifecyclePhasePresentation(row).badgeClass"
                  >
                    {{ lifecyclePhasePresentation(row).label }}
                  </span>
                </td>
                <td class="whitespace-nowrap px-4 py-3 text-right" @click.stop>
                  <div class="flex flex-wrap items-center justify-end gap-1.5">
                    <UiTableAction variant="sky" icon="eye" @click="openPackDetail(row)">详情</UiTableAction>
                    <UiTableAction
                      variant="slate"
                      icon="file-text"
                      :loading="forkPackIdLoading === row.promptPackId"
                      @click="openPackEdit(row)"
                    >
                      编辑
                    </UiTableAction>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div
          class="flex flex-col gap-3 px-4 py-3 sm:flex-row sm:items-center sm:justify-between sm:gap-4"
        >
          <p class="text-xs text-slate-600">
            共 <span class="tabular-nums text-slate-400">{{ totalFiltered }}</span> 条（默认隐藏已替代的
            <span class="font-mono text-slate-500">pack_*</span>；含 Phase1 SAFETY 种子；
            <span class="font-mono text-slate-500">scenario</span> 筛选时对 SAFETY 以服务端为准）
          </p>
          <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
            <div class="w-[10rem] shrink-0">
              <UiSelect
                v-model="pageSizeStr"
                size="sm"
                :options="PAGE_SIZE_OPTIONS"
                placeholder="每页条数"
              />
            </div>
            <UiButton type="button" variant="secondary" size="sm" :disabled="pageIndex <= 1" @click="prevPage">
              上一页
            </UiButton>
            <span :class="ADMIN_TOOLBAR_META_CLASS">
              {{ pageIndex }} / {{ totalPages }}
            </span>
            <UiButton
              type="button"
              variant="secondary"
              size="sm"
              :disabled="pageIndex >= totalPages"
              @click="nextPage"
            >
              下一页
            </UiButton>
          </div>
        </div>
      </template>
    </section>

    <Teleport to="body">
      <Transition name="admin-drawer-scrim">
        <button
          v-if="drawerOpen"
          type="button"
          class="fixed inset-0 z-40 bg-slate-950/65 backdrop-blur-[2px]"
          aria-label="关闭抽屉"
          @click="closeDrawer"
        />
      </Transition>
      <Transition name="admin-drawer-panel">
        <aside
          v-if="drawerOpen"
          class="fixed inset-y-0 right-0 z-50 flex w-full max-w-[480px] flex-col border-l border-slate-700 bg-slate-900 shadow-[inset_1px_0_0_0_rgb(255_255_255/0.04)]"
          role="dialog"
          aria-modal="true"
          aria-labelledby="prompt-drawer-title"
        >
            <div class="flex items-start justify-between gap-3 border-b border-slate-800/90 px-4 py-4">
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <h2 id="prompt-drawer-title" class="text-[15px] font-semibold leading-snug text-white">
                    {{ detail ? resolvePromptPackDisplayTitle(detail) : '加载中…' }}
                  </h2>
                  <span
                    v-if="detail && !detailLoading"
                    class="shrink-0 rounded border border-slate-600/70 px-2 py-0.5 text-[10px] font-medium text-slate-400"
                  >
                    详情 · 只读
                  </span>
                </div>
                <p class="mt-1 break-all font-mono text-xs text-slate-500">{{ packIdFromRoute }}</p>
              </div>
              <div class="flex shrink-0 flex-wrap items-start justify-end gap-2">
                <UiButton
                  v-if="packIdFromRoute"
                  type="button"
                  variant="secondary"
                  size="sm"
                  @click="goToPackEditor(packIdFromRoute)"
                >
                  在新页编辑
                </UiButton>
                <UiButton type="button" variant="ghost" size="sm" @click="closeDrawer">关闭</UiButton>
              </div>
            </div>
            <div class="min-h-0 flex-1 overflow-y-auto px-4 py-4">
              <div v-if="detailLoading" class="space-y-3" aria-busy="true">
                <div class="h-6 w-3/4 animate-pulse rounded bg-slate-800/80" />
                <div class="h-40 animate-pulse rounded-md bg-slate-800/45" />
              </div>
              <p v-else-if="detailError" class="text-sm text-amber-300">{{ detailError }}</p>
              <div v-else-if="detail" class="space-y-5">
                <dl class="grid gap-2 text-xs">
                  <div class="flex justify-between gap-3 border-b border-slate-800/60 py-2">
                    <dt class="text-slate-500">promptPackVersion</dt>
                    <dd class="font-mono text-slate-200">{{ detail.promptPackVersion }}</dd>
                  </div>
                  <div class="flex justify-between gap-3 border-b border-slate-800/60 py-2">
                    <dt class="text-slate-500">lifecycle</dt>
                    <dd class="text-slate-200">{{ detail.lifecycle }}</dd>
                  </div>
                  <div class="flex justify-between gap-3 py-2">
                    <dt class="text-slate-500">scenarioId</dt>
                    <dd class="break-all font-mono text-slate-200">{{ detail.scenarioId ?? '—' }}</dd>
                  </div>
                </dl>
                <div class="rounded-[var(--radius-ui)] border border-slate-700/80 bg-slate-950/50 px-3 py-2.5 text-xs leading-relaxed text-slate-400">
                  正文编辑与草稿发布请在
                  <RouterLink
                    v-if="packIdFromRoute"
                    class="font-medium text-emerald-400 underline-offset-4 hover:text-emerald-300 hover:underline"
                    :to="{ name: 'prompts.editor', params: { promptPackId: packIdFromRoute } }"
                  >
                    独立编辑器页（/prompts/editor/{{ packIdFromRoute }}）
                  </RouterLink>
                  <span v-else>独立编辑器页</span>
                  完成；或通过列表「编辑」进入。
                </div>
                <div class="rounded-[var(--radius-ui)] border border-slate-800/90 bg-slate-950/40 p-3">
                  <p class="text-xs font-medium uppercase tracking-wide text-slate-500">resolvedPromptBinding</p>
                  <pre class="mt-2 max-h-36 overflow-auto font-mono text-[11px] text-slate-500">{{ fmtJson(detail.resolvedPromptBinding) }}</pre>
                </div>
                <details
                  class="rounded-[var(--radius-ui)] border border-sky-900/35 bg-slate-950/50 px-3 py-2 [&_summary::-webkit-details-marker]:hidden"
                >
                  <summary
                    class="cursor-pointer list-none text-xs font-medium text-sky-200/95 transition-colors hover:text-sky-100"
                  >
                    占位符校验 · Phase1 平台白名单（只读）
                    <span class="ml-1 text-[11px] font-normal text-slate-500">· BACKEND_SPEC / pytest 对齐 ·</span>
                  </summary>
                  <p class="mt-2 text-[11px] leading-relaxed text-slate-500">
                    消息中的 <code class="rounded bg-slate-800 px-1 font-mono text-[10px]">{{ DOC_PLACEHOLDER_EXAMPLE }}</code>
                    ：当 <span class="font-mono text-slate-600">variableSchema</span>
                    为<strong class="font-medium text-slate-400">非空 JSON 对象</strong>时，须在
                    <strong class="font-medium text-slate-400">本题键 ∪ 下行列表</strong>。仅填空对象
                    <code class="font-mono text-[10px] text-slate-600">{{ DOC_EMPTY_SCHEMA_OBJECT }}</code>
                    等价于不显式扩展允许键（仍执行 denylist 等 Phase1 规则）。报错见业务码
                    <code class="font-mono text-[10px] text-slate-600">PROMPT_VALIDATION_FAILED</code>
                    （HTTP 422）。
                  </p>
                  <ul class="mt-2 flex flex-wrap gap-1.5">
                    <li
                      v-for="ex in PHASE1_PLATFORM_PROMPT_PLACEHOLDER_EXAMPLES"
                      :key="ex"
                      class="rounded border border-slate-700/80 bg-slate-900/60 px-1.5 py-0.5 font-mono text-[10px] text-slate-300"
                    >
                      {{ ex }}
                    </li>
                  </ul>
                </details>
                <div>
                  <label class="text-xs font-medium text-slate-400" for="drawer-variable-schema-json">
                    variableSchema（JSON object）
                  </label>
                  <textarea
                    id="drawer-variable-schema-json"
                    v-model="variableSchemaRaw"
                    spellcheck="false"
                    rows="7"
                    readonly
                    class="mt-2 box-border w-full resize-y rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 [color-scheme:dark] read-only:cursor-default read-only:border-slate-800/90 read-only:bg-slate-950/70 read-only:opacity-95"
                  />
                </div>
                <div>
                  <label class="text-xs font-medium text-slate-400" for="drawer-messages-json">messages</label>
                  <textarea
                    id="drawer-messages-json"
                    v-model="messagesRaw"
                    spellcheck="false"
                    rows="14"
                    readonly
                    class="mt-2 box-border min-h-[12rem] w-full resize-y rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 [color-scheme:dark] read-only:cursor-default read-only:border-slate-800/90 read-only:bg-slate-950/70 read-only:opacity-95"
                  />
                </div>
              </div>
            </div>
        </aside>
      </Transition>
    </Teleport>

    <UiModal
      v-model:open="draftModalOpen"
      title="新建 Prompt 草稿"
      description="创建后为 DRAFT；成功后将跳转到 /prompts/editor/:promptPackId 编辑正文并发布。"
    >
      <div class="space-y-4">
        <div class="flex flex-wrap gap-2">
          <button
            v-for="seg in DRAFT_CREATE_MODE_SEGMENTS"
            :key="seg.key"
            type="button"
            class="admin-seg text-sm"
            :class="
              draftCreateMode === seg.key
                ? 'admin-seg-active'
                : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
            "
            @click="draftCreateMode = seg.key"
          >
            {{ seg.label }}
          </button>
        </div>

        <template v-if="draftCreateMode === 'blank'">
          <p class="text-[13px] leading-relaxed text-slate-500">
            通过 <span class="font-mono text-slate-600">POST /api/v1/admin/prompt-packs</span>
            创建服务端 DRAFT；TRADING / ANALYSIS 须绑定场景寄存器内的
            <span class="font-mono text-slate-600">scenarioId</span>。
          </p>
          <UiSelect
            v-model="draftPackType"
            label="类型（promptPackType）"
            :options="STRATEGY_DRAFT_PACK_TYPE_OPTIONS"
            placeholder="选择类型"
          />
          <UiSelect
            v-model="draftScenarioId"
            :label="draftScenarioRequired ? 'scenarioId（必填）' : 'scenarioId（可选）'"
            :options="draftScenarioOptions"
            :placeholder="scenariosLoading ? '加载场景寄存器…' : '从 GET /agent/scenarios 选择'"
            :disabled="scenariosLoading"
          />
          <UiInput
            v-model="draftPromptPackId"
            label="Prompt ID（可选）"
            placeholder="留空则由服务端生成 pack_draft_* / pack_{scenario}_*"
            autocomplete="off"
          />
        </template>

        <template v-else>
          <p class="text-[13px] leading-relaxed text-slate-500">
            复制所选包的 messages 与 variableSchema 到新 DRAFT，不会覆盖原包。可改
            <span class="font-mono text-slate-600">scenarioId</span> 后再创建。
          </p>
          <UiSelect
            v-model="draftSourcePackId"
            label="模板包（sourcePromptPackId）"
            :options="templatePackOptions"
            placeholder="从当前列表选择"
            :disabled="templatePackOptions.length === 0"
          />
          <p v-if="templatePackOptions.length === 0" class="text-xs text-amber-300/90">
            当前列表无可用模板，请刷新列表或改用空白草稿。
          </p>
          <UiSelect
            v-model="draftPackType"
            label="目标类型（promptPackType）"
            :options="STRATEGY_DRAFT_PACK_TYPE_OPTIONS"
            placeholder="选择类型"
          />
          <UiSelect
            v-model="draftScenarioId"
            :label="draftScenarioRequired ? 'scenarioId（必填，可覆盖）' : 'scenarioId（可选，可覆盖）'"
            :options="draftScenarioOptions"
            :placeholder="scenariosLoading ? '加载场景寄存器…' : '从场景寄存器选择'"
            :disabled="scenariosLoading"
          />
          <UiInput
            v-model="draftPromptPackId"
            label="新 Prompt ID（可选）"
            placeholder="留空则由服务端生成"
            autocomplete="off"
          />
        </template>

        <p v-if="createError" class="text-sm text-rose-300/95">{{ createError }}</p>
      </div>
      <template #footer>
        <UiButton type="button" variant="ghost" @click="draftModalOpen = false">取消</UiButton>
        <UiButton type="button" :loading="createLoading" @click="submitCreateDraft">
          {{ draftSubmitLabel }}
        </UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>
