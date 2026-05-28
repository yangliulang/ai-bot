<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 拦截流水分页工具条页码文案与 **`ADMIN_TOOLBAR_META_CLASS`** 对齐
作者: 杨永的Agent
日期: 2026-05-21
修改功能: 列表/抽屉优先 **`row.title`**（`resolvePromptPackDisplayTitle` · FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 安全防护页 /prompts/safety（prompt-safety 聚合 API + SAFETY 包 prompt-packs CRUD）
修改功能: 修复「新建安全规则」弹窗内多语句 @click 模板解析错误
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import {
  explainPromptPackApiError,
  normalizeDetailVariableSchema,
} from '@/pages/prompts/usePromptPackEditor'
import { PHASE1_PLATFORM_PROMPT_PLACEHOLDER_EXAMPLES } from '@/shared/copy/prompt-platform-placeholders'
import {
  createPromptPack,
  getPromptPack,
  resolvePromptPackDisplayTitle,
  type PromptPackDetail,
  type PromptPackSummary,
} from '@/shared/api/admin-prompt-packs'
import {
  explainPromptSafetyError,
  getPromptSafetyOverview,
  getPromptSafetyRuntimeGovernance,
  getPromptSafetySessionPolicy,
  getPromptSafetyToolPolicies,
  listPromptSafetyIntercepts,
  listPromptSafetyPacks,
  type RuntimeSafetyGovernanceRow,
  type SafetyInterceptCategory,
  type SafetyInterceptItem,
  type SafetyOverview,
  type SessionSafetyPolicyItem,
  type ToolSafetyPolicyRow,
} from '@/shared/api/admin-prompt-safety'
import { AppError } from '@/shared/api/errors'
import { adminNotifyManualRefresh, adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import { formatAdminApiTime } from '@/shared/lib/admin-datetime-display'
import AdminPage from '@/shared/ui/AdminPage.vue'
import {
  ADMIN_TOOLBAR_CLUSTER_CLASS,
  ADMIN_TOOLBAR_META_CLASS,
  AdminPageHeader,
  UiButton,
  UiInput,
  UiModal,
  UiSelect,
  UiTableAction,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
  type UiSelectOption,
} from '@/shared/ui'

type SafetyPanelKey = 'strategy' | 'intercepts'
type StrategyTabKey = 'prompt' | 'runtime' | 'tool' | 'session'

const PLATFORM_SAFETY_SCENARIO = 'agent.runtime.platform_safety'

const route = useRoute()
const router = useRouter()

const overview = ref<SafetyOverview | null>(null)
const overviewLoading = ref(false)
const overviewError = ref<string | null>(null)

const safetyPacks = ref<PromptPackSummary[]>([])
const packsLoading = ref(false)
const packsError = ref<string | null>(null)

const runtimeRows = ref<RuntimeSafetyGovernanceRow[]>([])
const runtimeLoading = ref(false)
const runtimeError = ref<string | null>(null)

const toolRows = ref<ToolSafetyPolicyRow[]>([])
const toolLoading = ref(false)
const toolError = ref<string | null>(null)

const sessionRows = ref<SessionSafetyPolicyItem[]>([])
const sessionLoading = ref(false)
const sessionError = ref<string | null>(null)

const interceptItems = ref<SafetyInterceptItem[]>([])
const interceptTotal = ref(0)
const interceptLoading = ref(false)
const interceptError = ref<string | null>(null)
const interceptCategory = ref<SafetyInterceptCategory | '__all__'>('__all__')
const interceptPage = ref(1)
const interceptPageSize = 10

const newRuleModalOpen = ref(false)
const safetyDraftModalOpen = ref(false)
const draftScenarioId = ref(PLATFORM_SAFETY_SCENARIO)
const draftPromptPackId = ref('')
const createLoading = ref(false)
const createError = ref<string | null>(null)

const detail = ref<PromptPackDetail | null>(null)
const detailLoading = ref(false)
const detailError = ref<string | null>(null)
const messagesRaw = ref('')
const variableSchemaRaw = ref('{}')

const DOC_PLACEHOLDER_EXAMPLE = '{{ticker}}'
const DOC_EMPTY_SCHEMA_OBJECT = '{}'

const activePanel = computed<SafetyPanelKey>(() => {
  const p = route.query.panel
  const raw = Array.isArray(p) ? p[0] : p
  return raw === 'intercepts' ? 'intercepts' : 'strategy'
})

const activeTab = computed<StrategyTabKey>(() => {
  const t = route.query.tab
  const raw = Array.isArray(t) ? t[0] : t
  if (raw === 'runtime' || raw === 'tool' || raw === 'session') return raw
  return 'prompt'
})

const packIdFromRoute = computed(() => {
  const raw = route.query.pack
  const s = Array.isArray(raw) ? raw[0] : raw
  return typeof s === 'string' && s.trim() !== '' ? s.trim() : ''
})

const drawerOpen = computed(() => Boolean(packIdFromRoute.value))

const interceptTableScrollX = computed(
  () => !interceptLoading.value && interceptItems.value.length > 0,
)

const interceptTotalPages = computed(() =>
  Math.max(1, Math.ceil(interceptTotal.value / interceptPageSize)),
)

const INTERCEPT_CATEGORY_OPTIONS: UiSelectOption[] = [
  { value: '__all__', label: '全部分类' },
  { value: 'runtime', label: '运行时' },
  { value: 'prompt', label: 'Prompt' },
  { value: 'tool', label: '工具' },
  { value: 'session', label: '会话' },
]

const CATEGORY_META: Record<
  SafetyInterceptCategory,
  { label: string; badgeClass: string }
> = {
  runtime: { label: '运行时', badgeClass: 'border-rose-500/35 bg-rose-500/10 text-rose-200' },
  prompt: { label: 'Prompt', badgeClass: 'border-sky-500/35 bg-sky-500/10 text-sky-200' },
  tool: { label: '工具', badgeClass: 'border-orange-500/35 bg-orange-500/10 text-orange-200' },
  session: { label: '会话', badgeClass: 'border-violet-500/35 bg-violet-500/10 text-violet-200' },
}

const TOOL_POLICY_LABEL: Record<ToolSafetyPolicyRow['policy'], string> = {
  deny: '禁止',
  allowlist: '白名单',
  shadow: '审计与降级',
}

const TOOL_ENFORCEMENT_LABEL: Record<ToolSafetyPolicyRow['enforcementMode'], string> = {
  default_deny: '默认拒绝',
  allowlist_only: '仅白名单',
  approve_then_allow: '审批后放行',
}

function mergeQuery(updates: Record<string, string | undefined>) {
  const next = { ...route.query } as Record<string, string | string[] | undefined>
  for (const [k, v] of Object.entries(updates)) {
    if (v === undefined || v === '') delete next[k]
    else next[k] = v
  }
  void router.replace({ query: next })
}

function setPanel(key: SafetyPanelKey) {
  mergeQuery({
    panel: key === 'strategy' ? undefined : key,
    tab: undefined,
    pack: undefined,
  })
}

function setStrategyTab(key: StrategyTabKey) {
  mergeQuery({
    tab: key === 'prompt' ? undefined : key,
    pack: undefined,
  })
}

function fmtJson(v: unknown): string {
  return JSON.stringify(v, null, 2)
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

function runtimeHref(row: RuntimeSafetyGovernanceRow): string {
  if (row.hrefKind === 'confirmation') return '/ai/confirmation-rules'
  if (row.hrefKind === 'policy') return '/ai/runtime-orchestration?tab=policy'
  return '/ai/runtime-orchestration?tab=routing'
}

function runtimeHrefLabel(row: RuntimeSafetyGovernanceRow): string {
  if (row.hrefKind === 'confirmation') return '确认规则'
  if (row.hrefKind === 'policy') return '风险与策略'
  return '运行场景'
}

function riskLevelBadgeClass(label: string): string {
  if (label === '高') return 'border-rose-500/35 bg-rose-500/10 text-rose-200'
  if (label === '中') return 'border-amber-500/35 bg-amber-500/10 text-amber-200'
  if (label === '低') return 'border-emerald-500/35 bg-emerald-500/10 text-emerald-200'
  return 'border-slate-600 bg-slate-800/60 text-slate-400'
}

function sessionStatusClass(status: SessionSafetyPolicyItem['status']): string {
  if (status === 'enabled') return 'border-emerald-500/35 bg-emerald-500/10 text-emerald-200'
  if (status === 'warning') return 'border-amber-500/35 bg-amber-500/10 text-amber-200'
  return 'border-sky-500/35 bg-sky-500/10 text-sky-200'
}

function sessionStatusLabel(status: SessionSafetyPolicyItem['status']): string {
  if (status === 'enabled') return '已启用'
  if (status === 'warning') return '监测中'
  return '说明'
}

async function loadOverview() {
  overviewLoading.value = true
  overviewError.value = null
  try {
    overview.value = await getPromptSafetyOverview()
  } catch (e) {
    overview.value = null
    overviewError.value = explainPromptSafetyError(e, '加载总览失败')
  } finally {
    overviewLoading.value = false
  }
}

async function loadSafetyPacks() {
  packsLoading.value = true
  packsError.value = null
  try {
    const res = await listPromptSafetyPacks()
    safetyPacks.value = res.items ?? []
    const pid = packIdFromRoute.value
    if (pid && !safetyPacks.value.some((r) => r.promptPackId === pid)) {
      mergeQuery({ pack: undefined })
    }
  } catch (e) {
    safetyPacks.value = []
    packsError.value = explainPromptSafetyError(e, '加载 SAFETY 列表失败')
  } finally {
    packsLoading.value = false
  }
}

async function loadRuntimeGovernance() {
  runtimeLoading.value = true
  runtimeError.value = null
  try {
    const res = await getPromptSafetyRuntimeGovernance()
    runtimeRows.value = res.items ?? []
  } catch (e) {
    runtimeRows.value = []
    runtimeError.value = explainPromptSafetyError(e, '加载 Runtime 治理失败')
  } finally {
    runtimeLoading.value = false
  }
}

async function loadToolPolicies() {
  toolLoading.value = true
  toolError.value = null
  try {
    const res = await getPromptSafetyToolPolicies()
    toolRows.value = res.items ?? []
  } catch (e) {
    toolRows.value = []
    toolError.value = explainPromptSafetyError(e, '加载工具策略失败')
  } finally {
    toolLoading.value = false
  }
}

async function loadSessionPolicy() {
  sessionLoading.value = true
  sessionError.value = null
  try {
    const res = await getPromptSafetySessionPolicy()
    sessionRows.value = res.items ?? []
  } catch (e) {
    sessionRows.value = []
    sessionError.value = explainPromptSafetyError(e, '加载会话策略失败')
  } finally {
    sessionLoading.value = false
  }
}

async function loadIntercepts() {
  interceptLoading.value = true
  interceptError.value = null
  try {
    const offset = (interceptPage.value - 1) * interceptPageSize
    const res = await listPromptSafetyIntercepts({
      category: interceptCategory.value === '__all__' ? undefined : interceptCategory.value,
      limit: interceptPageSize,
      offset,
    })
    interceptItems.value = res.items ?? []
    interceptTotal.value = res.total ?? 0
  } catch (e) {
    interceptItems.value = []
    interceptTotal.value = 0
    interceptError.value = explainPromptSafetyError(e, '加载拦截记录失败')
  } finally {
    interceptLoading.value = false
  }
}

async function refreshAll(toastOnSuccess = false) {
  await loadOverview()
  if (activePanel.value === 'intercepts') {
    await loadIntercepts()
  } else if (activeTab.value === 'prompt') await loadSafetyPacks()
  else if (activeTab.value === 'runtime') await loadRuntimeGovernance()
  else if (activeTab.value === 'tool') await loadToolPolicies()
  else await loadSessionPolicy()
  adminNotifyManualRefresh(toastOnSuccess, {
    ok: !overviewError.value,
    successMessage: '已刷新',
    errorMessage: overviewError.value,
  })
}

function openPackDetail(row: PromptPackSummary) {
  mergeQuery({ pack: row.promptPackId })
}

function goToPackEditor(promptPackId: string) {
  void router.push({ name: 'prompts.editor', params: { promptPackId } })
}

function openPackEdit(row: PromptPackSummary) {
  goToPackEditor(row.promptPackId)
}

function closeDrawer() {
  mergeQuery({ pack: undefined })
}

function openSafetyDraftFromNewRule() {
  newRuleModalOpen.value = false
  safetyDraftModalOpen.value = true
}

function openConfirmationRuleCreateFromNewRule() {
  newRuleModalOpen.value = false
  void router.push({ name: 'ai.confirmation-rules.new' })
}

function closeNewRuleModal() {
  newRuleModalOpen.value = false
}

async function submitCreateSafetyDraft() {
  createError.value = null
  createLoading.value = true
  try {
    const body: { promptPackType: string; scenarioId?: string; promptPackId?: string } = {
      promptPackType: 'SAFETY',
    }
    const sid = draftScenarioId.value.trim()
    const pid = draftPromptPackId.value.trim()
    if (sid) body.scenarioId = sid
    if (pid) body.promptPackId = pid
    const created = await createPromptPack(body)
    safetyDraftModalOpen.value = false
    await loadSafetyPacks()
    await loadOverview()
    void router.push({ name: 'prompts.editor', params: { promptPackId: created.promptPackId } })
  } catch (e) {
    createError.value = explainPromptPackApiError(e, '创建 SAFETY 草稿失败')
  } finally {
    createLoading.value = false
  }
}

watch(
  () => [activePanel.value, activeTab.value] as const,
  ([panel, tab]) => {
    if (panel === 'intercepts') {
      void loadIntercepts()
      return
    }
    if (tab === 'prompt') void loadSafetyPacks()
    else if (tab === 'runtime') void loadRuntimeGovernance()
    else if (tab === 'tool') void loadToolPolicies()
    else void loadSessionPolicy()
  },
  { immediate: true },
)

watch(
  () => [interceptCategory.value, interceptPage.value] as const,
  () => {
    if (activePanel.value === 'intercepts') void loadIntercepts()
  },
)

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

watch(safetyDraftModalOpen, (open) => {
  if (!open) return
  createError.value = null
  draftScenarioId.value = PLATFORM_SAFETY_SCENARIO
  draftPromptPackId.value = ''
})

void loadOverview()
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="AI Runtime 安全治理"
      :badges="[{ label: '风控治理', tone: 'rose' }]"
      description="安全策略分层（Prompt / 运行时 / 工具 / 会话）与拦截流水。SAFETY 包编辑与发布走 /api/v1/admin/prompt-packs。"
      dev-meta="pageId · ai.prompt-safety · GET /api/v1/admin/prompt-safety/*"
      :error="overviewError"
    >
      <template #actions>
        <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
          <UiButton type="button" size="sm" @click="newRuleModalOpen = true">新建安全规则</UiButton>
          <UiButton type="button" variant="secondary" size="sm" :loading="overviewLoading" @click="refreshAll(true)">
            刷新
          </UiButton>
        </div>
      </template>
    </AdminPageHeader>

    <section
      v-if="overview && !overviewLoading"
      class="admin-panel mb-4 grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-4"
    >
      <div class="rounded-lg border border-slate-800/90 bg-slate-950/40 px-3 py-2.5">
        <p class="text-[11px] uppercase tracking-wide text-slate-500">用语闸 revision</p>
        <p class="mt-1 font-mono text-sm text-slate-200">{{ overview.safetyPhraseBlocklistRevision }}</p>
        <p class="mt-0.5 text-[11px] text-slate-600">{{ overview.safetyPhraseScanScopeDefault }}</p>
      </div>
      <div class="rounded-lg border border-slate-800/90 bg-slate-950/40 px-3 py-2.5">
        <p class="text-[11px] uppercase tracking-wide text-slate-500">SAFETY 包</p>
        <p class="mt-1 text-sm text-slate-200">
          <span class="tabular-nums">{{ overview.publishedSafetyPackCount }}</span>
          已发布 /
          <span class="tabular-nums">{{ overview.safetyPromptPackCount }}</span>
          总计
        </p>
        <p
          v-if="overview.platformSafetyPack"
          class="mt-1 truncate font-mono text-[11px] text-emerald-300/90"
          :title="overview.platformSafetyPack.promptPackId"
        >
          平台：{{ overview.platformSafetyPack.promptPackId }}
        </p>
      </div>
      <div class="rounded-lg border border-slate-800/90 bg-slate-950/40 px-3 py-2.5">
        <p class="text-[11px] uppercase tracking-wide text-slate-500">人工确认规则</p>
        <p class="mt-1 text-sm text-slate-200">
          已启用
          <span class="tabular-nums font-medium">{{ overview.enabledConfirmationRulesCount }}</span>
          条
        </p>
        <RouterLink
          class="mt-1 inline-block text-xs text-sky-300 underline-offset-4 hover:text-sky-200 hover:underline"
          to="/ai/confirmation-rules"
        >
          管理确认规则
        </RouterLink>
      </div>
      <div class="rounded-lg border border-slate-800/90 bg-slate-950/40 px-3 py-2.5">
        <p class="text-[11px] uppercase tracking-wide text-slate-500">全局闸</p>
        <p class="mt-1 text-sm text-slate-200">
          Agent 开关
          <span
            class="ml-1 rounded border px-1.5 py-0.5 text-[11px]"
            :class="
              overview.globalAgentSwitchOn
                ? 'border-emerald-500/35 bg-emerald-500/10 text-emerald-200'
                : 'border-slate-600 bg-slate-800/60 text-slate-400'
            "
          >
            {{ overview.globalAgentSwitchOn ? '开' : '关' }}
          </span>
        </p>
        <p v-if="overview.opsSuspended" class="mt-1 text-xs text-amber-300">运维挂起中</p>
      </div>
    </section>

    <div class="mb-4 flex flex-wrap gap-2 border-b border-slate-800/80 pb-1">
      <button
        type="button"
        class="admin-seg text-sm"
        :class="activePanel === 'strategy' ? 'admin-seg-active' : 'admin-seg-idle'"
        @click="setPanel('strategy')"
      >
        安全策略
      </button>
      <button
        type="button"
        class="admin-seg text-sm"
        :class="activePanel === 'intercepts' ? 'admin-seg-active' : 'admin-seg-idle'"
        @click="setPanel('intercepts')"
      >
        拦截记录
      </button>
    </div>

    <template v-if="activePanel === 'strategy'">
      <div class="mb-4 flex flex-wrap gap-2">
        <button
          v-for="tab in [
            { key: 'prompt', label: 'Prompt 安全' },
            { key: 'runtime', label: 'Runtime 安全' },
            { key: 'tool', label: 'Tool 安全' },
            { key: 'session', label: 'Session 安全' },
          ]"
          :key="tab.key"
          type="button"
          class="admin-seg text-xs sm:text-sm"
          :class="
            activeTab === tab.key
              ? 'admin-seg-active'
              : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
          "
          @click="setStrategyTab(tab.key as StrategyTabKey)"
        >
          {{ tab.label }}
        </button>
      </div>

      <section v-if="activeTab === 'prompt'" class="admin-panel overflow-hidden p-0">
        <div class="border-b border-slate-800/80 px-4 py-3 sm:px-5">
          <h2 class="text-[15px] font-semibold text-white">
            护栏 Prompt（SAFETY）
            <span class="ml-2 text-xs font-normal text-slate-500">共 {{ safetyPacks.length }} 条</span>
          </h2>
          <p v-if="packsError" class="mt-2 text-sm text-rose-300/95">{{ packsError }}</p>
        </div>
        <div
          class="rounded-lg border-0"
          :class="adminTableHostOverflowClass(!packsLoading && safetyPacks.length > 0)"
        >
          <table class="min-w-[720px] w-full text-left text-sm">
            <thead class="border-b border-slate-800 bg-slate-900/85 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th class="px-4 py-3">Prompt ID</th>
                <th class="px-4 py-3">名称 / 场景</th>
                <th class="whitespace-nowrap px-4 py-3">版本</th>
                <th class="whitespace-nowrap px-4 py-3">状态</th>
                <th class="whitespace-nowrap px-4 py-3 text-right">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/90">
              <UiTableEmptyRow v-if="packsLoading" :colspan="5" state="loading" />
              <UiTableEmptyRow
                v-else-if="safetyPacks.length === 0"
                :colspan="5"
                state="empty"
                title="暂无 SAFETY 包"
                description="可通过「新建安全规则」创建护栏草稿。"
              />
              <tr
                v-for="row in safetyPacks"
                v-else
                :key="row.promptPackId"
                class="cursor-pointer transition-colors hover:bg-slate-900/40"
                @click="openPackDetail(row)"
              >
                <td class="max-w-[14rem] px-4 py-3 font-mono text-xs text-emerald-200/90">
                  <span class="break-all">{{ row.promptPackId }}</span>
                </td>
                <td class="max-w-[12rem] px-4 py-3 text-slate-200">
                  <span class="line-clamp-2">{{ resolvePromptPackDisplayTitle(row) }}</span>
                </td>
                <td class="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-300">
                  {{ row.promptPackVersion != null ? `v${row.promptPackVersion}` : '—' }}
                </td>
                <td class="whitespace-nowrap px-4 py-3 text-slate-400">{{ zhLifecycleRaw(row.lifecycle) }}</td>
                <td class="whitespace-nowrap px-4 py-3 text-right" @click.stop>
                  <div class="flex justify-end gap-1">
                    <UiTableAction variant="sky" icon="eye" @click="openPackDetail(row)">详情</UiTableAction>
                    <UiTableAction variant="slate" icon="file-text" @click="openPackEdit(row)">编辑</UiTableAction>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section v-else-if="activeTab === 'runtime'" class="admin-panel p-4 sm:p-5">
        <h2 class="mb-3 text-[15px] font-semibold text-white">Runtime 安全</h2>
        <p v-if="runtimeError" class="mb-3 text-sm text-rose-300/95">{{ runtimeError }}</p>
        <div
          class="overflow-x-auto rounded-lg border border-slate-800"
          :class="adminTableHostOverflowClass(!runtimeLoading && runtimeRows.length > 0)"
        >
          <table class="min-w-[900px] w-full text-left text-sm">
            <thead class="border-b border-slate-800 bg-slate-900/85 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th class="min-w-[10rem] px-4 py-3">治理项</th>
                <th class="whitespace-nowrap px-4 py-3">风险等级</th>
                <th class="px-4 py-3">自动执行</th>
                <th class="px-4 py-3">人工确认</th>
                <th class="px-4 py-3">熔断策略</th>
                <th class="whitespace-nowrap px-4 py-3">关联配置</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/90">
              <UiTableEmptyRow v-if="runtimeLoading" :colspan="6" state="loading" />
              <UiTableEmptyRow v-else-if="runtimeRows.length === 0" :colspan="6" state="empty" />
              <tr v-for="row in runtimeRows" v-else :key="row.key" class="hover:bg-slate-900/35">
                <td class="px-4 py-3 font-medium text-slate-200">{{ row.name }}</td>
                <td class="whitespace-nowrap px-4 py-3">
                  <span
                    class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                    :class="riskLevelBadgeClass(row.riskLevelLabel)"
                  >
                    {{ row.riskLevelLabel }}
                  </span>
                </td>
                <td class="max-w-[12rem] px-4 py-3 text-xs text-slate-400">
                  <span class="line-clamp-2" :title="row.autoExecSummary">{{ row.autoExecSummary }}</span>
                </td>
                <td class="max-w-[12rem] px-4 py-3 text-xs text-slate-400">
                  <span class="line-clamp-2" :title="row.confirmSummary">{{ row.confirmSummary }}</span>
                </td>
                <td class="max-w-[12rem] px-4 py-3 text-xs text-slate-400">
                  <span class="line-clamp-2" :title="row.breakerSummary">{{ row.breakerSummary }}</span>
                </td>
                <td class="whitespace-nowrap px-4 py-3">
                  <RouterLink
                    class="text-xs text-sky-300 underline-offset-4 hover:text-sky-200 hover:underline"
                    :to="runtimeHref(row)"
                  >
                    {{ runtimeHrefLabel(row) }}
                  </RouterLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="mt-3 flex flex-wrap gap-3 text-xs">
          <RouterLink class="text-sky-300 hover:text-sky-200 hover:underline" to="/ai/confirmation-rules">
            人工确认规则
          </RouterLink>
          <RouterLink
            class="text-sky-300 hover:text-sky-200 hover:underline"
            to="/ai/runtime-orchestration?tab=policy"
          >
            全局风险与执行策略
          </RouterLink>
          <RouterLink
            class="text-sky-300 hover:text-sky-200 hover:underline"
            to="/ai/runtime-orchestration?tab=routing"
          >
            运行场景目录
          </RouterLink>
        </div>
      </section>

      <section v-else-if="activeTab === 'tool'" class="admin-panel p-4 sm:p-5">
        <h2 class="mb-3 text-[15px] font-semibold text-white">工具调用策略</h2>
        <p v-if="toolError" class="mb-3 text-sm text-rose-300/95">{{ toolError }}</p>
        <div
          class="overflow-x-auto rounded-lg border border-slate-800"
          :class="adminTableHostOverflowClass(!toolLoading && toolRows.length > 0)"
        >
          <table class="min-w-[720px] w-full text-left text-sm">
            <thead class="border-b border-slate-800 bg-slate-900/85 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th class="px-4 py-3">工具范围</th>
                <th class="whitespace-nowrap px-4 py-3">生效模式</th>
                <th class="whitespace-nowrap px-4 py-3">处置口径</th>
                <th class="px-4 py-3">说明</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/90">
              <UiTableEmptyRow v-if="toolLoading" :colspan="4" state="loading" />
              <UiTableEmptyRow v-else-if="toolRows.length === 0" :colspan="4" state="empty" />
              <tr v-for="row in toolRows" v-else :key="row.key" class="hover:bg-slate-900/35">
                <td class="px-4 py-3 font-mono text-xs text-slate-300">{{ row.toolPattern }}</td>
                <td class="whitespace-nowrap px-4 py-3 text-xs text-slate-300">
                  {{ TOOL_ENFORCEMENT_LABEL[row.enforcementMode] }}
                </td>
                <td class="whitespace-nowrap px-4 py-3 text-xs text-slate-300">
                  {{ TOOL_POLICY_LABEL[row.policy] }}
                </td>
                <td class="px-4 py-3 text-xs text-slate-400">
                  <span class="line-clamp-2" :title="row.note">{{ row.note }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <RouterLink
          class="mt-3 inline-block text-xs text-sky-300 hover:text-sky-200 hover:underline"
          to="/ai/runtime-orchestration"
        >
          运行编排
        </RouterLink>
      </section>

      <section v-else class="admin-panel p-4 sm:p-5">
        <h2 class="mb-3 text-[15px] font-semibold text-white">会话与行为风控</h2>
        <p class="mb-3 text-xs text-slate-500">Phase1 为说明性条目，具体阈值与熔断以运行编排与后端策略为准。</p>
        <p v-if="sessionError" class="mb-3 text-sm text-rose-300/95">{{ sessionError }}</p>
        <div v-if="sessionLoading" class="space-y-2 py-6" aria-busy="true">
          <div class="h-12 animate-pulse rounded-md bg-slate-800/50" />
          <div class="h-12 animate-pulse rounded-md bg-slate-800/40" />
        </div>
        <dl v-else class="divide-y divide-slate-800/90 rounded-lg border border-slate-800">
          <div
            v-for="row in sessionRows"
            :key="row.key"
            class="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-start sm:justify-between"
          >
            <div class="min-w-0">
              <dt class="text-sm font-medium text-slate-200">{{ row.label }}</dt>
              <dd class="mt-1 text-xs leading-relaxed text-slate-500">{{ row.summary }}</dd>
            </div>
            <span
              class="shrink-0 rounded border px-2 py-0.5 text-[11px] font-medium"
              :class="sessionStatusClass(row.status)"
            >
              {{ sessionStatusLabel(row.status) }}
            </span>
          </div>
          <p v-if="!sessionLoading && sessionRows.length === 0" class="px-4 py-8 text-center text-sm text-slate-500">
            暂无会话策略说明
          </p>
        </dl>
      </section>

      <p class="mt-4 text-xs text-slate-600">
        非护栏类提示词见
        <RouterLink class="text-sky-400/90 hover:text-sky-300 hover:underline" to="/prompts/strategy">
          提示词治理
        </RouterLink>
        。
      </p>
    </template>

    <section v-else class="admin-panel overflow-hidden p-0">
      <div class="flex flex-col gap-3 border-b border-slate-800/80 px-4 py-3 sm:flex-row sm:items-end sm:justify-between sm:px-5">
        <h2 class="text-[15px] font-semibold text-white">拦截记录</h2>
        <div class="w-full sm:w-44">
          <UiSelect
            v-model="interceptCategory"
            label="分类"
            :options="INTERCEPT_CATEGORY_OPTIONS"
            @update:model-value="interceptPage = 1"
          />
        </div>
      </div>
      <p v-if="interceptError" class="px-4 pb-2 text-sm text-rose-300/95 sm:px-5">{{ interceptError }}</p>
      <div
        class="rounded-lg border-0"
        :class="adminTableHostOverflowClass(interceptTableScrollX)"
      >
        <table
          class="w-full text-left text-sm"
          :class="interceptTableScrollX ? 'min-w-[960px]' : ''"
        >
          <thead class="border-b border-slate-800 bg-slate-900/85 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="whitespace-nowrap px-4 py-3">时间</th>
              <th class="whitespace-nowrap px-4 py-3">类型</th>
              <th class="min-w-[10rem] px-4 py-3">场景</th>
              <th class="whitespace-nowrap px-4 py-3">事件</th>
              <th class="min-w-[12rem] px-4 py-3">原因 / 处置</th>
              <th class="whitespace-nowrap px-4 py-3">对象</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/90">
            <UiTableEmptyRow v-if="interceptLoading" :colspan="6" state="loading" />
            <UiTableEmptyRow
              v-else-if="interceptItems.length === 0"
              :colspan="6"
              state="empty"
              title="暂无拦截记录"
            />
            <tr v-for="row in interceptItems" v-else :key="row.id" class="hover:bg-slate-900/35">
              <td class="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-400">
                {{ formatAdminApiTime(row.ts) }}
              </td>
              <td class="whitespace-nowrap px-4 py-3">
                <span
                  class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                  :class="CATEGORY_META[row.category].badgeClass"
                >
                  {{ CATEGORY_META[row.category].label }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-slate-400">
                <span class="line-clamp-2" :title="row.scenarioLabel">{{ row.scenarioLabel }}</span>
              </td>
              <td class="whitespace-nowrap px-4 py-3 text-xs text-slate-300">{{ row.kindLabel }}</td>
              <td class="px-4 py-3 text-xs text-slate-400">
                <span class="line-clamp-2" :title="row.reason">{{ row.reason }}</span>
              </td>
              <td class="max-w-[10rem] px-4 py-3 text-xs text-slate-500">
                <span class="truncate" :title="row.subject ?? undefined">{{ row.subject ?? '—' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div
        class="flex flex-wrap items-center justify-between gap-2 border-t border-slate-800/80 px-4 py-3 sm:px-5"
      >
        <p class="text-xs text-slate-600">
          共 <span class="tabular-nums text-slate-400">{{ interceptTotal }}</span> 条
        </p>
        <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
          <UiButton
            type="button"
            variant="secondary"
            size="sm"
            :disabled="interceptPage <= 1"
            @click="interceptPage -= 1"
          >
            上一页
          </UiButton>
          <span :class="ADMIN_TOOLBAR_META_CLASS">
            {{ interceptPage }} / {{ interceptTotalPages }}
          </span>
          <UiButton
            type="button"
            variant="secondary"
            size="sm"
            :disabled="interceptPage >= interceptTotalPages"
            @click="interceptPage += 1"
          >
            下一页
          </UiButton>
        </div>
      </div>
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
          aria-labelledby="safety-pack-drawer-title"
        >
          <div class="flex items-start justify-between gap-3 border-b border-slate-800/90 px-4 py-4">
            <div class="min-w-0 flex-1">
              <h2 id="safety-pack-drawer-title" class="text-[15px] font-semibold text-white">
                {{ detail ? resolvePromptPackDisplayTitle(detail) : '加载中…' }}
              </h2>
              <p class="mt-1 break-all font-mono text-xs text-slate-500">{{ packIdFromRoute }}</p>
            </div>
            <div class="flex shrink-0 gap-2">
              <UiButton
                v-if="packIdFromRoute"
                type="button"
                variant="secondary"
                size="sm"
                @click="goToPackEditor(packIdFromRoute)"
              >
                编辑
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
            <div v-else-if="detail" class="space-y-4">
              <dl class="grid gap-2 text-xs">
                <div class="flex justify-between gap-3 border-b border-slate-800/60 py-2">
                  <dt class="text-slate-500">lifecycle</dt>
                  <dd class="text-slate-200">{{ detail.lifecycle }}</dd>
                </div>
                <div class="flex justify-between gap-3 py-2">
                  <dt class="text-slate-500">scenarioId</dt>
                  <dd class="break-all font-mono text-slate-200">{{ detail.scenarioId ?? '—' }}</dd>
                </div>
              </dl>
              <p
                v-if="detail.safetyPhraseBlocklistRevision"
                class="rounded border border-rose-900/35 bg-rose-950/20 px-3 py-2 text-xs text-rose-200/90"
              >
                用语闸 revision：<span class="font-mono">{{ detail.safetyPhraseBlocklistRevision }}</span>
              </p>
              <div>
                <label class="text-xs font-medium text-slate-400" for="safety-drawer-messages">messages</label>
                <textarea
                  id="safety-drawer-messages"
                  v-model="messagesRaw"
                  readonly
                  rows="14"
                  class="mt-2 box-border w-full resize-y rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 read-only:opacity-95"
                />
              </div>
              <details class="rounded border border-sky-900/35 bg-slate-950/50 px-3 py-2">
                <summary class="cursor-pointer text-xs text-sky-200/95">占位符白名单（只读）</summary>
                <ul class="mt-2 flex flex-wrap gap-1.5">
                  <li
                    v-for="ex in PHASE1_PLATFORM_PROMPT_PLACEHOLDER_EXAMPLES"
                    :key="ex"
                    class="rounded border border-slate-700/80 px-1.5 py-0.5 font-mono text-[10px] text-slate-300"
                  >
                    {{ ex }}
                  </li>
                </ul>
              </details>
              <div>
                <label class="text-xs font-medium text-slate-400" for="safety-drawer-schema">variableSchema</label>
                <textarea
                  id="safety-drawer-schema"
                  v-model="variableSchemaRaw"
                  readonly
                  rows="6"
                  class="mt-2 box-border w-full font-mono text-xs text-slate-200"
                />
              </div>
            </div>
          </div>
        </aside>
      </Transition>
    </Teleport>

    <UiModal v-model:open="newRuleModalOpen" title="新建安全规则" :show-default-close="true">
      <div class="space-y-3">
        <button
          type="button"
          class="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-3 text-left transition-colors hover:border-slate-600 hover:bg-slate-800/80"
          @click="openSafetyDraftFromNewRule"
        >
          <p class="text-sm font-medium text-white">护栏 Prompt（SAFETY）</p>
          <p class="mt-1 text-xs text-slate-500">语义层防护，创建草稿后进入编辑器。</p>
        </button>
        <button
          type="button"
          class="w-full rounded-lg border border-slate-700 bg-slate-900/60 px-4 py-3 text-left transition-colors hover:border-slate-600 hover:bg-slate-800/80"
          @click="openConfirmationRuleCreateFromNewRule"
        >
          <p class="text-sm font-medium text-white">人工确认规则</p>
          <p class="mt-1 text-xs text-slate-500">风险条件与确认动作。</p>
        </button>
        <RouterLink
          class="block rounded-lg border border-slate-800 bg-slate-950/40 px-4 py-3 text-sm text-sky-300 hover:text-sky-200"
          to="/ai/runtime-orchestration"
          @click="closeNewRuleModal"
        >
          工具与会话策略 → 运行编排
        </RouterLink>
      </div>
    </UiModal>

    <UiModal
      v-model:open="safetyDraftModalOpen"
      title="新建 SAFETY 护栏草稿"
      description="POST /api/v1/admin/prompt-packs · promptPackType=SAFETY"
    >
      <div class="space-y-4">
        <UiInput
          v-model="draftScenarioId"
          label="scenarioId（可选）"
          placeholder="agent.runtime.platform_safety"
          autocomplete="off"
        />
        <UiInput
          v-model="draftPromptPackId"
          label="Prompt ID（可选）"
          placeholder="留空则由服务端生成"
          autocomplete="off"
        />
        <p v-if="createError" class="text-sm text-rose-300/95">{{ createError }}</p>
      </div>
      <template #footer>
        <UiButton type="button" variant="ghost" @click="safetyDraftModalOpen = false">取消</UiButton>
        <UiButton type="button" :loading="createLoading" @click="submitCreateSafetyDraft">创建草稿</UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>
