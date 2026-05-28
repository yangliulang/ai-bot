<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 应用检索/复制链接反馈改用全局 **`adminToast`**；按钮 loading
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 执行列表空态 **`UiTableEmptyRow`**；无数据时取消表格横向滚动
作者: 杨永的Agent
日期: 2026-05-18
修改功能: **执行列表**列 **`promptPackVersion` · 交易绑定摘要**（与 Runtime 同源 · FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 执行列表「复制 ID」→ **`UiClipboardTipAction`**（回退剪贴板 + 浮动提示）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: 协查时间线传入列表解析的 **`scenarioId`**（与 executionId 对齐）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: 执行 Tab 增加意图调试面板（S11 plan.clarify · FE_HANDOFF 2026-05-27）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: `/observability` 执行链路协查 · `?tab=execution` 默认；执行 Tab 列表 + 时间线（FR-MC801）；其余 Tab 占位
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import IntentRecognizeProbePanel from '@/features/observability/IntentRecognizeProbePanel.vue'
import ObservabilityExecutionTimelinePanel from '@/features/observability/ObservabilityExecutionTimelinePanel.vue'
import { AppError } from '@/shared/api/errors'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import {
  getAdminObservabilityLlm,
  getAdminObservabilityToolCalls,
  listAdminObservabilityExecutions,
  type AdminAgentExecutionItem,
  type ObservabilityLlmUsageResponse,
  type ObservabilityToolCallItem,
} from '@/shared/api/admin-observability'
import { formatPromptPackVersionLabel, summarizeTradingPromptBinding } from '@/shared/lib/execution-prompt-meta'
import { formatIsoTime, zhExecutionRuntimeStatus } from '@/shared/copy/zh-runtime'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminTimeTh from '@/shared/ui/AdminTimeTh.vue'
import {
  AdminPageHeader,
  UiButton,
  UiClipboardTipAction,
  UiInput,
  UiTableAction,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
} from '@/shared/ui'
import {
  buildObservabilitySearch,
  isObservabilityTab,
  type ObservabilityTab,
} from '@/shared/utils/observability-deep-link'

const TAB_SEQUENCE: ObservabilityTab[] = ['execution', 'tool', 'llm', 'billing', 'audit']

const TAB_LABELS: Record<ObservabilityTab, string> = {
  execution: '执行',
  tool: '工具调用',
  llm: '大模型',
  billing: '计费',
  audit: '审计',
}

const route = useRoute()
const router = useRouter()

const draftExecutionId = ref('')
const draftUserId = ref('')
const draftTraceId = ref('')

const items = ref<AdminAgentExecutionItem[]>([])
const total = ref(0)
const offset = ref(0)
const pageSize = ref(15)
const loading = ref(false)
const listError = ref<string | null>(null)
const applyFiltersLoading = ref(false)
const copyLinkLoading = ref(false)

const toolItems = ref<ObservabilityToolCallItem[]>([])
const toolLoading = ref(false)
const toolError = ref<string | null>(null)

const llmData = ref<ObservabilityLlmUsageResponse | null>(null)
const llmLoading = ref(false)
const llmError = ref<string | null>(null)

const detailExecutionId = computed(() => firstQueryString(route.query.executionId)?.trim() ?? '')

function firstQueryString(value: unknown): string | undefined {
  if (typeof value === 'string') return value
  if (Array.isArray(value) && typeof value[0] === 'string') return value[0]
  return undefined
}

const activeTab = computed((): ObservabilityTab => {
  const s = firstQueryString(route.query.tab)
  if (s && isObservabilityTab(s)) return s
  return 'execution'
})

watch(
  () => route.fullPath,
  () => {
    draftExecutionId.value = firstQueryString(route.query.executionId) ?? ''
    draftUserId.value = firstQueryString(route.query.userId) ?? ''
    const tidRaw = route.query.traceId ?? route.query.traceKey
    draftTraceId.value = firstQueryString(tidRaw) ?? ''
  },
  { immediate: true },
)

watch(
  () => route.query.tab,
  (t) => {
    const s = firstQueryString(t)
    if (s && isObservabilityTab(s)) return
    void router.replace({
      path: '/observability',
      query: { ...route.query, tab: 'execution' },
    })
  },
  { immediate: true },
)

async function loadList() {
  if (activeTab.value !== 'execution') return
  loading.value = true
  listError.value = null
  try {
    const executionIdRaw = route.query.executionId
    const userIdRaw = route.query.userId
    const executionId =
      (firstQueryString(executionIdRaw)?.trim()) || undefined
    const userId =
      (firstQueryString(userIdRaw)?.trim()) || undefined

    const res = await listAdminObservabilityExecutions({
      limit: pageSize.value,
      offset: offset.value,
      executionId,
      userId,
    })
    items.value = res.items
    total.value = res.total
  } catch (e) {
    listError.value = e instanceof AppError ? e.message : '加载失败'
    items.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

watch(
  () =>
    [
      activeTab.value,
      route.query.executionId,
      route.query.userId,
      offset.value,
      pageSize.value,
    ] as const,
  () => {
    if (activeTab.value === 'execution') void loadList()
  },
  { immediate: true },
)

function setTab(tab: ObservabilityTab) {
  void router.replace({
    path: '/observability',
    query: { ...route.query, tab },
  })
}

async function applyTraceFilters() {
  if (applyFiltersLoading.value) return
  applyFiltersLoading.value = true
  try {
    const q: Record<string, string> = { tab: activeTab.value }
    const e = draftExecutionId.value.trim()
    const u = draftUserId.value.trim()
    const tr = draftTraceId.value.trim()
    if (e) q.executionId = e
    if (u) q.userId = u
    if (tr) q.traceId = tr
    await router.replace({ path: '/observability', query: q })
    offset.value = 0
    adminToastSuccess('检索条件已更新')
  } finally {
    applyFiltersLoading.value = false
  }
}

function clearTraceFilters() {
  void router.replace({ path: '/observability', query: { tab: activeTab.value } })
  offset.value = 0
}

const timelineExecutionId = computed(() => {
  const q = firstQueryString(route.query.executionId)?.trim() ?? ''
  if (q) return q
  if (items.value.length === 1) {
    const row = items.value[0]
    return row ? row.executionId : ''
  }
  return ''
})

/** 与当前时间线 executionId 对应的列表行（用于闪兑流程条等） */
const timelineScenarioId = computed(() => {
  const id = timelineExecutionId.value.trim()
  if (!id) return null as string | null
  const row = items.value.find((r) => r.executionId === id)
  return row?.scenarioId ?? null
})

async function copyShareLink() {
  if (copyLinkLoading.value) return
  copyLinkLoading.value = true
  const e = firstQueryString(route.query.executionId)?.trim()
  const u = firstQueryString(route.query.userId)?.trim()
  const tr = firstQueryString(route.query.traceId)?.trim()
  const path = `/observability${buildObservabilitySearch({
    executionId: e,
    userId: u,
    traceId: tr,
    tab: 'execution',
  })}`
  try {
    await navigator.clipboard.writeText(`${window.location.origin}${path}`)
    adminToastSuccess('已复制当前协查链接')
  } catch {
    adminToastError('复制失败（浏览器权限）')
  } finally {
    copyLinkLoading.value = false
  }
}

function statusTagClass(status: string): string {
  if (status === 'SUCCEEDED') return 'border-emerald-500/35 bg-emerald-500/10 text-emerald-300'
  if (status === 'ACCEPTED') return 'border-sky-500/35 bg-sky-500/10 text-sky-300'
  if (status === 'CANCELLED') return 'border-slate-600 bg-slate-800/80 text-slate-300'
  if (status === 'FAILED') return 'border-rose-500/35 bg-rose-500/10 text-rose-300'
  return 'border-slate-600 bg-slate-800/80 text-slate-300'
}

function maskUserId(raw: string): string {
  const s = raw.trim()
  if (s.length <= 10) return s
  return `${s.slice(0, 5)}…${s.slice(-4)}`
}

function prevPage() {
  offset.value = Math.max(0, offset.value - pageSize.value)
}

function nextPage() {
  if (offset.value + pageSize.value < total.value) offset.value += pageSize.value
}

const rangeStart = computed(() => (total.value === 0 ? 0 : offset.value + 1))

const executionListTableScrollX = computed(() => !loading.value && items.value.length > 0)
const rangeEnd = computed(() =>
  total.value === 0 ? 0 : Math.min(offset.value + items.value.length, total.value),
)

const llmTableScrollX = computed(() => !llmLoading.value && (llmData.value?.calls.length ?? 0) > 0)
const toolTableScrollX = computed(() => !toolLoading.value && toolItems.value.length > 0)

async function loadToolCalls(executionId: string) {
  toolLoading.value = true
  toolError.value = null
  toolItems.value = []
  try {
    const res = await getAdminObservabilityToolCalls(executionId)
    toolItems.value = res.items
  } catch (e) {
    toolItems.value = []
    if (e instanceof AppError && e.status === 404) {
      toolError.value = '执行记录不存在'
    } else {
      toolError.value = e instanceof AppError ? e.message : '加载失败'
    }
  } finally {
    toolLoading.value = false
  }
}

async function loadLlm(executionId: string) {
  llmLoading.value = true
  llmError.value = null
  llmData.value = null
  try {
    llmData.value = await getAdminObservabilityLlm(executionId)
  } catch (e) {
    llmData.value = null
    if (e instanceof AppError && e.status === 404) {
      llmError.value = '执行记录不存在'
    } else {
      llmError.value = e instanceof AppError ? e.message : '加载失败'
    }
  } finally {
    llmLoading.value = false
  }
}

async function loadDetailTab() {
  const tab = activeTab.value
  if (tab !== 'tool' && tab !== 'llm') return
  const eid = detailExecutionId.value
  if (!eid) {
    toolItems.value = []
    toolError.value = null
    toolLoading.value = false
    llmData.value = null
    llmError.value = null
    llmLoading.value = false
    return
  }
  if (tab === 'tool') await loadToolCalls(eid)
  if (tab === 'llm') await loadLlm(eid)
}

watch(
  () => [activeTab.value, detailExecutionId.value] as const,
  () => {
    void loadDetailTab()
  },
  { immediate: true },
)

function goExecutionTabWithId(executionId?: string) {
  const eid = executionId?.trim() || draftExecutionId.value.trim()
  const q: Record<string, string> = { tab: 'execution' }
  if (eid) q.executionId = eid
  void router.replace({ path: '/observability', query: q })
}

function observabilityTabHref(tab: 'tool' | 'llm', executionId: string) {
  return `/observability${buildObservabilitySearch({ tab, executionId })}`
}

</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="执行链路协查"
      dev-meta="pageId · obs.traces-logs"
    >
      <template #extra>
        <p class="max-w-3xl text-sm leading-relaxed text-slate-400">
          按工单
          <code class="rounded bg-slate-800 px-1 font-mono text-xs text-slate-500">executionId</code>
          查看持久化执行与时间线；与
          <RouterLink class="text-emerald-400/90 hover:text-emerald-300" to="/runtime/executions">
            执行记录
          </RouterLink>
          同源数据。
        </p>
      </template>
      <template #actions>
        <UiButton
          type="button"
          variant="secondary"
          size="sm"
          :loading="copyLinkLoading"
          @click="copyShareLink"
        >
          复制协查链接
        </UiButton>
      </template>
    </AdminPageHeader>

    <div class="flex flex-wrap gap-2 border-b border-slate-800 pb-2 transition-opacity duration-150">
      <button
        v-for="t in TAB_SEQUENCE"
        :key="t"
        type="button"
        class="admin-seg"
        :class="
          activeTab === t
            ? 'admin-seg-active'
            : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
        "
        @click="setTab(t)"
      >
        {{ TAB_LABELS[t] }}
      </button>
    </div>

    <div v-if="activeTab === 'execution'" class="space-y-4">
      <section class="admin-panel overflow-hidden p-0 transition-colors duration-150">
        <div class="border-b border-slate-800/90 px-4 py-2.5 sm:px-5">
          <h2 class="text-sm font-medium text-slate-200">协查条件</h2>
          <p class="mt-1 text-xs text-slate-500">
            <code class="font-mono text-[11px] text-slate-500">traceId</code>
            预留给计费联合检索；当前 Phase1 列表仅按 execution / user 精确筛选。
          </p>
        </div>
        <div class="space-y-3 p-4 sm:p-5">
          <div class="grid grid-cols-12 gap-3">
            <div class="col-span-12 md:col-span-4">
              <UiInput v-model="draftExecutionId" label="executionId" placeholder="精确执行 ID" />
            </div>
            <div class="col-span-12 md:col-span-4">
              <UiInput v-model="draftUserId" label="userId" placeholder="用户标识" />
            </div>
            <div class="col-span-12 md:col-span-4">
              <UiInput v-model="draftTraceId" label="traceId" placeholder="计费 trace / 关联键" />
            </div>
          </div>
          <div class="flex flex-wrap gap-2">
            <UiButton
              type="button"
              variant="primary"
              size="sm"
              :loading="applyFiltersLoading"
              @click="applyTraceFilters"
            >
              应用检索
            </UiButton>
            <UiButton type="button" variant="ghost" size="sm" @click="clearTraceFilters">清空条件</UiButton>
          </div>
        </div>
      </section>

      <section class="admin-panel overflow-hidden p-0 transition-colors duration-150">
        <div class="border-b border-slate-800/90 px-4 py-2.5 sm:px-5">
          <h2 class="text-sm font-medium text-slate-200">执行列表</h2>
        </div>
        <div class="space-y-3 p-3 sm:p-4">
          <p v-if="listError" class="text-sm text-rose-400">{{ listError }}</p>
          <div
            v-if="!listError && total > 0"
            class="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500"
          >
            <span class="tabular-nums">{{ rangeStart }}-{{ rangeEnd }} / 共 {{ total }} 条</span>
            <div class="inline-flex flex-wrap items-center gap-2">
              <UiButton type="button" variant="secondary" size="sm" :disabled="offset <= 0 || loading" @click="prevPage">
                上一页
              </UiButton>
              <UiButton
                type="button"
                variant="secondary"
                size="sm"
                :disabled="loading || offset + pageSize >= total"
                @click="nextPage"
              >
                下一页
              </UiButton>
            </div>
          </div>

          <div
            class="rounded-lg border border-slate-800"
            :class="adminTableHostOverflowClass(executionListTableScrollX)"
          >
            <table
              class="w-full divide-y divide-slate-800 text-sm"
              :class="executionListTableScrollX ? 'min-w-[1040px]' : ''"
            >
              <thead class="bg-slate-900/85 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th class="px-3 py-3">执行 ID</th>
                  <th class="px-3 py-3">用户</th>
                  <th class="px-3 py-3">场景</th>
                  <th class="px-3 py-3 font-normal normal-case tracking-normal">Prompt</th>
                  <th class="px-3 py-3">状态</th>
                  <th class="px-3 py-3 font-mono normal-case">
                    <AdminTimeTh>创建时间</AdminTimeTh>
                  </th>
                  <th class="px-3 py-3 text-right">操作</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800">
                <UiTableEmptyRow v-if="loading" :colspan="7" state="loading" />
                <UiTableEmptyRow v-else-if="items.length === 0" :colspan="7" state="filtered" />
                <tr
                  v-for="r in items"
                  v-else
                  :key="r.executionId"
                  class="transition-colors hover:bg-slate-900/55"
                >
                  <td class="max-w-[14rem] px-3 py-2.5 font-mono text-xs text-slate-200">
                    <span class="line-clamp-2 break-all">{{ r.executionId }}</span>
                  </td>
                  <td class="max-w-[8rem] truncate px-3 py-2.5 font-mono text-xs text-slate-400" :title="r.userId">
                    {{ maskUserId(r.userId) }}
                  </td>
                  <td class="max-w-[10rem] truncate px-3 py-2.5 font-mono text-xs text-slate-400">
                    {{ r.scenarioId ?? '—' }}
                  </td>
                  <td class="max-w-[12rem] px-3 py-2.5 align-top text-[11px] leading-snug text-slate-500">
                    <div class="font-mono text-sky-300/90">{{ formatPromptPackVersionLabel(r.promptPackVersion) }}</div>
                    <div
                      class="mt-0.5 line-clamp-2 break-all font-mono text-[10px] text-slate-500"
                      :title="summarizeTradingPromptBinding(r.resolvedPromptBinding ?? null)"
                    >
                      {{ summarizeTradingPromptBinding(r.resolvedPromptBinding ?? null) }}
                    </div>
                  </td>
                  <td class="px-3 py-2.5">
                    <span
                      class="inline-flex rounded-md border px-2 py-0.5 text-[11px] font-medium"
                      :class="statusTagClass(r.state)"
                    >
                      {{ zhExecutionRuntimeStatus(r.state) }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-3 py-2.5 font-mono text-xs tabular-nums text-slate-500">
                    {{ formatIsoTime(r.createdAt) }}
                  </td>
                  <td class="px-3 py-2.5 text-right">
                    <div class="flex flex-wrap items-center justify-end gap-1.5">
                      <UiClipboardTipAction variant="slate" :text="r.executionId" />
                      <UiTableAction
                        variant="emerald"
                        icon="clock"
                        :to="{
                          name: 'runtime.execution-detail',
                          params: { executionId: r.executionId },
                          query: { tab: 'timeline' },
                        }"
                      >
                        详情 · 时间线
                      </UiTableAction>
                      <UiTableAction variant="slate" :to="observabilityTabHref('tool', r.executionId)">
                        工具
                      </UiTableAction>
                      <UiTableAction variant="slate" :to="observabilityTabHref('llm', r.executionId)">
                        LLM
                      </UiTableAction>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <IntentRecognizeProbePanel />

      <section class="admin-panel overflow-hidden p-0 transition-colors duration-150">
        <div class="border-b border-slate-800/90 px-4 py-2.5 sm:px-5">
          <h2 class="text-sm font-medium text-slate-200">执行时间线</h2>
          <p class="mt-1 text-xs text-slate-500">
            来源
            <code class="rounded bg-slate-800 px-1 font-mono text-[11px]">GET /api/v1/admin/observability/executions/{executionId}/timeline</code>
          </p>
        </div>
        <div class="p-4 sm:p-5">
          <ObservabilityExecutionTimelinePanel
            :execution-id="timelineExecutionId"
            :scenario-id="timelineScenarioId"
          />
        </div>
      </section>
    </div>

    <section
      v-else-if="activeTab === 'tool' || activeTab === 'llm'"
      class="admin-panel overflow-hidden p-0 transition-colors duration-150"
    >
      <div class="border-b border-slate-800/90 px-4 py-2.5 sm:px-5">
        <h2 class="text-sm font-medium text-slate-200">{{ TAB_LABELS[activeTab] }}</h2>
        <p class="mt-1 text-xs text-slate-500">
          <code class="font-mono text-[11px]">
            GET /api/v1/admin/observability/executions/{executionId}/{{ activeTab === 'tool' ? 'tool-calls' : 'llm' }}
          </code>
        </p>
      </div>

      <div v-if="!detailExecutionId" class="space-y-3 p-6 text-sm text-slate-400">
        <p>请先在「执行」Tab 检索并选择 <code class="font-mono text-xs text-slate-300">executionId</code>，或在本页协查条件中填写后应用检索。</p>
        <UiButton type="button" variant="primary" size="sm" @click="goExecutionTabWithId()">
          前往执行列表
        </UiButton>
      </div>

      <template v-else>
        <div class="border-b border-slate-800/80 px-4 py-2 text-xs text-slate-500 sm:px-5">
          当前 executionId：
          <code class="font-mono text-slate-300">{{ detailExecutionId }}</code>
        </div>

        <template v-if="activeTab === 'tool'">
          <p v-if="toolError" class="px-4 py-3 text-sm text-rose-400 sm:px-5">{{ toolError }}</p>
          <div
            class="p-3 sm:p-4"
            :class="adminTableHostOverflowClass(toolTableScrollX)"
          >
            <table class="w-full divide-y divide-slate-800 text-sm" :class="toolTableScrollX ? 'min-w-[880px]' : ''">
              <thead class="bg-slate-900/85 text-left text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th class="px-3 py-3">#</th>
                  <th class="px-3 py-3">toolId</th>
                  <th class="px-3 py-3">状态</th>
                  <th class="px-3 py-3">phase</th>
                  <th class="px-3 py-3">eventName</th>
                  <th class="px-3 py-3">stepKind</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-800">
                <UiTableEmptyRow v-if="toolLoading" :colspan="6" state="loading" />
                <UiTableEmptyRow v-else-if="toolItems.length === 0" :colspan="6" state="filtered" />
                <tr
                  v-for="row in toolItems"
                  v-else
                  :key="`${row.toolCallSeq}-${row.toolId}`"
                  class="hover:bg-slate-900/55"
                >
                  <td class="px-3 py-2.5 font-mono text-xs text-slate-500">{{ row.toolCallSeq }}</td>
                  <td class="max-w-[16rem] px-3 py-2.5 font-mono text-xs text-slate-200 break-all">
                    {{ row.toolId }}
                  </td>
                  <td class="px-3 py-2.5 text-xs text-emerald-300">{{ row.invocationState }}</td>
                  <td class="px-3 py-2.5 font-mono text-xs text-slate-400">{{ row.phase ?? '—' }}</td>
                  <td class="max-w-[12rem] truncate px-3 py-2.5 font-mono text-xs text-slate-400" :title="row.eventName ?? ''">
                    {{ row.eventName ?? '—' }}
                  </td>
                  <td class="px-3 py-2.5 font-mono text-xs text-slate-500">{{ row.stepKind ?? '—' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>

        <template v-else>
          <p v-if="llmError" class="px-4 py-3 text-sm text-rose-400 sm:px-5">{{ llmError }}</p>
          <div v-else class="space-y-3 p-4 sm:p-5">
            <dl class="grid gap-2 text-sm sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <dt class="text-xs text-slate-500">modelId</dt>
                <dd class="font-mono text-slate-200">{{ llmData?.modelId ?? '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">inputTokens</dt>
                <dd class="font-mono tabular-nums text-slate-300">{{ llmData?.inputTokens ?? '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">outputTokens</dt>
                <dd class="font-mono tabular-nums text-slate-300">{{ llmData?.outputTokens ?? '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">totalTokens</dt>
                <dd class="font-mono tabular-nums text-slate-300">{{ llmData?.totalTokens ?? '—' }}</dd>
              </div>
            </dl>
            <div :class="adminTableHostOverflowClass(llmTableScrollX)">
              <table class="w-full divide-y divide-slate-800 text-sm" :class="llmTableScrollX ? 'min-w-[720px]' : ''">
                <thead class="bg-slate-900/85 text-left text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th class="px-3 py-3">#</th>
                    <th class="px-3 py-3">eventName</th>
                    <th class="px-3 py-3">outcome</th>
                    <th class="px-3 py-3">gatewayModelId</th>
                    <th class="px-3 py-3 font-normal normal-case">
                      <AdminTimeTh>时间</AdminTimeTh>
                    </th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-800">
                  <UiTableEmptyRow v-if="llmLoading" :colspan="5" state="loading" />
                  <UiTableEmptyRow
                    v-else-if="!llmData?.calls?.length"
                    :colspan="5"
                    state="filtered"
                  />
                  <tr
                    v-for="c in llmData?.calls ?? []"
                    v-else
                    :key="`${c.toolCallSeq}-${c.eventName}`"
                    class="hover:bg-slate-900/55"
                  >
                    <td class="px-3 py-2.5 font-mono text-xs text-slate-500">{{ c.toolCallSeq }}</td>
                    <td class="max-w-[14rem] truncate px-3 py-2.5 font-mono text-xs text-violet-300/90" :title="c.eventName">
                      {{ c.eventName }}
                    </td>
                    <td class="px-3 py-2.5 text-xs text-slate-300">{{ c.outcome ?? '—' }}</td>
                    <td class="max-w-[10rem] truncate px-3 py-2.5 font-mono text-xs text-slate-400">
                      {{ c.gatewayModelId ?? '—' }}
                    </td>
                    <td class="whitespace-nowrap px-3 py-2.5 font-mono text-xs text-slate-500">
                      {{ formatIsoTime(c.ts) }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </template>
    </section>

    <section
      v-else
      class="admin-panel rounded-lg border border-slate-800 bg-slate-950/35 p-6 text-sm leading-relaxed text-slate-500 transition-colors duration-150"
    >
      <p class="font-medium text-slate-400">{{ TAB_LABELS[activeTab] }}</p>
      <p class="mt-2">
        本 Tab（计费 / 审计 / 联合检索）不在功能包
        <code class="rounded bg-slate-800 px-1 font-mono text-[11px]">2026-05-26--admin-observability</code>
        范围内，后续迭代再接。
      </p>
    </section>
  </AdminPage>
</template>
