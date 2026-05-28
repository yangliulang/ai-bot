<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 刷新/重置/删除等操作反馈改用全局 **`adminToast`**（移除页内 flash 文案）
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 筛选/分页工具条 **`UiStatChip`** · **`UiSelect size=sm`** · 工具条行高对齐
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 列表空态改用 **`UiTableEmptyRow`**；无数据时取消表格横向滚动
作者: 杨永的Agent
日期: 2026-05-18
修改功能: **Prompt 快照**列与预览抽屉：`promptPackVersion`、`resolvedPromptBinding`（可折叠全文 · FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 分页条每页条数选择改用 `UiSelect`（移除原生 `select`）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 「复制 ID」使用 **`UiClipboardTipAction`**（剪贴板回退 + 复制成功/balloon 提示）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **执行列表**：创建时间 **`col` `min-width`** + 表格 **`min-w`** 略增，避免横向滚动时右侧粘性「操作」列覆盖时间戳末尾
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **预览 Drawer** 使用全局 **`admin-drawer-*`** 缓动（backdrop 渐入 + 侧栏滑入）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **执行列表** 表不换行：**重试次数** / **运行状态** Badge / **操作** 单行；executionId **`truncate`** 控制行高
作者: 杨永的Agent
日期: 2026-05-14
修改功能: 「执行链路协查」deeplink **`tab=execution`**；详情默认「时间线」；行内复制 **executionId**
作者: 杨永的Agent
日期: 2026-05-13
修改功能: Observability **`DELETE …/executions/{id}`**（二次确认、刷新 / 分页兜底）；列表与预览层
-->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { AppError } from '@/shared/api/errors'
import { adminNotifyManualRefresh, adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import {
  deleteAdminObservabilityExecution,
  listAdminObservabilityExecutions,
  type AdminAgentExecutionItem,
} from '@/shared/api/admin-observability'
import { formatPromptPackVersionLabel, summarizeTradingPromptBinding } from '@/shared/lib/execution-prompt-meta'
import { formatIsoTime, zhExecutionRuntimeStatus } from '@/shared/copy/zh-runtime'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminTimeTh from '@/shared/ui/AdminTimeTh.vue'
import { buildObservabilitySearch } from '@/shared/utils/observability-deep-link'
import {
  ADMIN_TOOLBAR_CLUSTER_CLASS,
  ADMIN_TOOLBAR_META_CLASS,
  AdminPageHeader,
  UiButton,
  UiClipboardTipAction,
  UiInput,
  UiModal,
  UiSelect,
  UiStatChip,
  UiTableAction,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
  type UiSelectOption,
} from '@/shared/ui'

const PAGE_SIZE_OPTIONS = [10, 15, 20, 50] as const
const PAGE_SIZE_SELECT_OPTIONS: UiSelectOption[] = PAGE_SIZE_OPTIONS.map((ps) => ({
  value: String(ps),
  label: `${ps} 条/页`,
}))

const STATUS_OPTIONS: UiSelectOption[] = [
  { value: '__all__', label: '全部状态' },
  { value: 'ACCEPTED', label: zhExecutionRuntimeStatus('ACCEPTED') },
  { value: 'SUCCEEDED', label: zhExecutionRuntimeStatus('SUCCEEDED') },
  { value: 'FAILED', label: zhExecutionRuntimeStatus('FAILED') },
  { value: 'CANCELLED', label: zhExecutionRuntimeStatus('CANCELLED') },
]

const router = useRouter()
const route = useRoute()

const items = ref<AdminAgentExecutionItem[]>([])
const total = ref(0)
const offset = ref(0)
const pageSize = ref(15)
const loading = ref(false)
const refreshing = ref(false)
const loadError = ref<string | null>(null)
const previewRow = ref<AdminAgentExecutionItem | null>(null)
const execDeleteOpen = ref(false)
const execPendingDelete = ref<AdminAgentExecutionItem | null>(null)
const execDeleting = ref(false)
const execDeleteError = ref<string | null>(null)

const q = computed(() => (route.query.q as string) ?? '')
const intent = computed(() => (route.query.intent as string) ?? '')
const scenario = computed(() => (route.query.scenario as string) ?? '')
const dateFrom = computed(() => (route.query.from as string) ?? '')
const dateTo = computed(() => (route.query.to as string) ?? '')

const dateRangeInvalid = computed(() => Boolean(dateFrom.value && dateTo.value && dateFrom.value > dateTo.value))

const effectiveDateFrom = computed(() => (dateRangeInvalid.value ? '' : dateFrom.value))
const effectiveDateTo = computed(() => (dateRangeInvalid.value ? '' : dateTo.value))

function apiStateFromRoute(): string | undefined {
  const raw = (route.query.status as string | undefined)?.trim().toUpperCase()
  if (!raw || raw === 'ALL') return undefined
  if (['ACCEPTED', 'SUCCEEDED', 'FAILED', 'CANCELLED'].includes(raw)) return raw
  return undefined
}

const displayItems = computed(() => {
  const needle = intent.value.trim().toLowerCase()
  if (!needle) return items.value
  return items.value.filter((r) => {
    const hay = `${r.note ?? ''} ${r.source ?? ''}`.toLowerCase()
    return hay.includes(needle)
  })
})

const rangeStart = computed(() => (total.value === 0 ? 0 : offset.value + 1))
const rangeEnd = computed(() =>
  total.value === 0 ? 0 : Math.min(offset.value + items.value.length, total.value),
)

const executionTableScrollX = computed(() => !loading.value && displayItems.value.length > 0)

function maskUserId(raw: string): string {
  const s = raw.trim()
  if (s.length <= 10) return s
  return `${s.slice(0, 5)}…${s.slice(-4)}`
}

function observabilityHref(row: AdminAgentExecutionItem): string {
  return `/observability${buildObservabilitySearch({
    executionId: row.executionId,
    userId: row.userId,
    tab: 'execution',
  })}`
}

function fmtPromptBindingFull(row: AdminAgentExecutionItem): string {
  const b = row.resolvedPromptBinding
  if (b == null || typeof b !== 'object') return '{}'
  return JSON.stringify(b, null, 2)
}

async function load() {
  loading.value = true
  loadError.value = null
  try {
    const keyword = q.value.trim() || undefined
    const scenarioId = scenario.value.trim() || undefined
    let createdAfter: string | undefined
    let createdBefore: string | undefined
    if (effectiveDateFrom.value) createdAfter = `${effectiveDateFrom.value}T00:00:00`
    if (effectiveDateTo.value) createdBefore = `${effectiveDateTo.value}T23:59:59.999`
    const res = await listAdminObservabilityExecutions({
      limit: pageSize.value,
      offset: offset.value,
      state: apiStateFromRoute(),
      keyword,
      scenarioId,
      createdAfter,
      createdBefore,
    })
    items.value = res.items
    total.value = res.total
  } catch (e) {
    loadError.value = e instanceof AppError ? e.message : '加载失败'
    items.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function onRefresh() {
  refreshing.value = true
  try {
    await load()
    adminNotifyManualRefresh(true, {
      ok: !loadError.value,
      successMessage: '已刷新列表',
      errorMessage: loadError.value,
    })
  } finally {
    refreshing.value = false
  }
}

onMounted(() => {
  void load()
})

watch(
  () => route.query,
  () => {
    const prev = offset.value
    offset.value = 0
    if (prev === 0) void load()
  },
  { deep: true },
)

watch(offset, () => {
  void load()
})

function setPageSize(n: number) {
  if (!PAGE_SIZE_OPTIONS.includes(n as (typeof PAGE_SIZE_OPTIONS)[number])) return
  if (n === pageSize.value) return
  pageSize.value = n
  const prev = offset.value
  offset.value = 0
  if (prev === 0) void load()
}

const pageSizeModel = computed({
  get: () => String(pageSize.value),
  set: (v: string) => {
    const n = Number(v)
    if (!Number.isFinite(n)) return
    setPageSize(n)
  },
})

function patchQuery(mut: (q: Record<string, string>) => void) {
  const next = { ...route.query } as Record<string, string | undefined>
  const o: Record<string, string> = {}
  for (const [k, v] of Object.entries(next)) {
    if (v !== undefined) o[k] = v
  }
  mut(o)
  router.push({ path: route.path, query: o })
}

function setFilter(key: 'q' | 'intent' | 'scenario' | 'status' | 'from' | 'to', value: string) {
  patchQuery((q_) => {
    const t = value.trim()
    if (!t || (key === 'status' && t === 'all')) delete q_[key]
    else q_[key] = t
  })
}

function clearScenarioFilter() {
  patchQuery((q_) => {
    delete q_.scenario
  })
}

function resetFilters() {
  const hadQuery = Object.keys(route.query).length > 0
  offset.value = 0
  pageSize.value = 15
  router.replace({ path: route.path, query: {} })
  if (!hadQuery) void load()
  adminToastSuccess('已重置筛选条件')
}

const qModel = computed({
  get: () => q.value,
  set: (v: string) => setFilter('q', v),
})

const intentModel = computed({
  get: () => intent.value,
  set: (v: string) => setFilter('intent', v),
})

const statusModel = computed({
  get() {
    const s = apiStateFromRoute()
    return s ?? '__all__'
  },
  set(v: string) {
    if (v === '__all__') setFilter('status', 'all')
    else setFilter('status', v)
  },
})

const dateFromModel = computed({
  get: () => dateFrom.value,
  set: (v: string) => setFilter('from', v),
})

const dateToModel = computed({
  get: () => dateTo.value,
  set: (v: string) => setFilter('to', v),
})

function prevPage() {
  offset.value = Math.max(0, offset.value - pageSize.value)
}

function nextPage() {
  if (offset.value + pageSize.value < total.value) offset.value += pageSize.value
}

function statusTagClass(status: string): string {
  if (status === 'SUCCEEDED') return 'border-emerald-500/35 bg-emerald-500/10 text-emerald-300'
  if (status === 'ACCEPTED') return 'border-sky-500/35 bg-sky-500/10 text-sky-300'
  if (status === 'CANCELLED') return 'border-slate-600 bg-slate-800/80 text-slate-300'
  if (status === 'FAILED') return 'border-rose-500/35 bg-rose-500/10 text-rose-300'
  if (status === 'COMPLETED') return 'border-emerald-500/35 bg-emerald-500/10 text-emerald-300'
  if (status === 'RUNNING') return 'border-sky-500/35 bg-sky-500/10 text-sky-300'
  return 'border-slate-600 bg-slate-800/80 text-slate-300'
}

function onRowClick(e: MouseEvent, row: AdminAgentExecutionItem) {
  const el = e.target as HTMLElement | null
  if (el?.closest('a, button, [role="button"]')) return
  previewRow.value = row
}

function openExecDelete(row: AdminAgentExecutionItem) {
  execPendingDelete.value = row
  execDeleteError.value = null
  execDeleteOpen.value = true
}

function cancelExecDelete() {
  execDeleteOpen.value = false
  execPendingDelete.value = null
  execDeleteError.value = null
}

async function confirmedExecDelete() {
  const row = execPendingDelete.value
  if (!row) return
  execDeleting.value = true
  execDeleteError.value = null
  try {
    await deleteAdminObservabilityExecution(row.executionId)
    execDeleteOpen.value = false
    execPendingDelete.value = null
    if (previewRow.value?.executionId === row.executionId) previewRow.value = null
    const prevOffset = offset.value
    await load()
    if (items.value.length === 0 && total.value > 0 && prevOffset > 0) {
      offset.value = Math.max(0, prevOffset - pageSize.value)
      await load()
    }
    adminToastSuccess('已删除执行记录')
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '删除失败'
    execDeleteError.value = msg
    adminToastError(msg)
  } finally {
    execDeleting.value = false
  }
}

function closePreview() {
  previewRow.value = null
}

function openDetailFromPreview() {
  const r = previewRow.value
  if (!r) return
  void router.push({
    name: 'runtime.execution-detail',
    params: { executionId: r.executionId },
    query: { tab: 'timeline' },
  })
  closePreview()
}

function openDeleteFromPreview() {
  const r = previewRow.value
  if (!r) return
  openExecDelete(r)
  closePreview()
}

const SPEC_FOOTER_PATHS = [
  'admin-console/sitemap.md',
  'admin-console/page-specs.md',
  'Runtime/overview.md',
  'observability/overview.md',
] as const
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="执行记录"
      :badges="[{ label: 'Runtime', tone: 'sky' }]"
      dev-meta="pageId · runtime.executions · GET …/admin/observability/executions"
    >
      <template #actions>
        <UiButton
          type="button"
          variant="secondary"
          size="sm"
          :loading="refreshing"
          :disabled="loading && !refreshing"
          @click="onRefresh"
        >
          刷新
        </UiButton>
      </template>
    </AdminPageHeader>

    <!-- 列表卡：对齐原型 Card title="列表" -->
    <section class="admin-panel overflow-hidden p-0">
      <div class="flex items-center justify-between gap-2 border-b border-slate-800/90 px-4 py-2.5 sm:px-5">
        <h2 class="text-sm font-medium text-slate-200">列表</h2>
      </div>

      <div class="space-y-3 p-3 sm:p-4 sm:pt-3">
        <!-- 场景条件提示 -->
        <div
          v-if="scenario.trim()"
          class="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-sky-500/25 bg-sky-500/5 px-3 py-2.5 text-sm"
        >
          <p class="text-slate-300">
            场景
            <code class="rounded bg-slate-900 px-1.5 py-0.5 font-mono text-xs text-sky-200/90">{{
              scenario.trim()
            }}</code>
          </p>
          <button
            type="button"
            class="text-xs font-medium text-sky-400 hover:text-sky-300"
            @click="clearScenarioFilter"
          >
            清除场景条件
          </button>
        </div>

        <!-- 筛选面：对齐 ExecutionListFilters -->
        <div
          class="rounded-lg border border-slate-800 bg-slate-950/40 px-3 py-3 sm:px-4"
          style="padding-top: 0.65rem; padding-bottom: 0.65rem"
        >
          <div class="mb-2.5 flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2">
            <div class="flex items-center gap-2 text-[15px] font-medium text-slate-200">
              <svg
                class="h-4 w-4 shrink-0 text-slate-500"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                aria-hidden="true"
              >
                <path d="M4 6h16M7 12h10M10 18h4" stroke-linecap="round" />
              </svg>
              筛选条件
            </div>
            <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
              <UiStatChip tone="success">
                命中 {{ displayItems.length }} / {{ total }}
              </UiStatChip>
              <UiButton type="button" variant="ghost" size="sm" @click="resetFilters">重置</UiButton>
            </div>
          </div>

          <p
            v-if="intent.trim()"
            class="mb-2 text-[11px] leading-snug text-slate-500"
          >
            「意图」：在当前页结果内按 note / source 摘要过滤（服务端关键字不含 note）。
          </p>

          <div
            v-if="dateRangeInvalid"
            class="mb-3 rounded-md border border-amber-500/35 bg-amber-500/10 px-3 py-2 text-xs text-amber-200/90"
            role="alert"
          >
            日期范围无效：已忽略日期筛选
          </div>

          <div
            class="admin-runtime-execution-filter-grid grid grid-cols-12 gap-x-3.5 gap-y-2.5"
            style="align-items: start"
          >
            <div class="col-span-12 md:col-span-6">
              <UiInput
                v-model="qModel"
                label="执行 / 用户 / 场景"
                placeholder="执行 ID、UID 或场景 ID · 任一串即匹配"
              />
            </div>
            <div class="col-span-12 sm:col-span-6 md:col-span-3">
              <UiInput v-model="intentModel" label="意图" placeholder="关键词" />
            </div>
            <div class="col-span-12 sm:col-span-6 md:col-span-3">
              <UiSelect v-model="statusModel" label="运行状态" placeholder="全部" :options="STATUS_OPTIONS" />
            </div>
            <div class="col-span-12 sm:col-span-6">
              <UiInput v-model="dateFromModel" type="date" label="创建起始日" />
            </div>
            <div class="col-span-12 sm:col-span-6">
              <UiInput v-model="dateToModel" type="date" label="创建结束日" />
            </div>
          </div>
        </div>

        <p v-if="loadError" class="text-sm text-rose-400" role="alert">{{ loadError }}</p>

        <!-- 分页工具条（对齐 antd showTotal 文案） -->
        <div
          v-if="!loadError && total > 0"
          class="flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500"
        >
          <span class="tabular-nums"
            >{{ rangeStart }}-{{ rangeEnd }} / 共 {{ total }} 条</span
          >
          <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
            <UiButton
              type="button"
              variant="secondary"
              size="sm"
              :disabled="offset <= 0 || loading"
              @click="prevPage"
            >
              上一页
            </UiButton>
            <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
              <span :class="[ADMIN_TOOLBAR_META_CLASS, 'text-slate-500']">每页</span>
              <div class="w-[7.5rem] min-w-[7.5rem] shrink-0">
                <UiSelect
                  v-model="pageSizeModel"
                  size="sm"
                  :options="PAGE_SIZE_SELECT_OPTIONS"
                  placeholder="每页条数"
                  :disabled="loading"
                />
              </div>
            </div>
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

        <!-- 表格 -->
        <div
          class="admin-runtime-execution-table-host rounded-lg border border-slate-800"
          :class="adminTableHostOverflowClass(executionTableScrollX)"
        >
          <table
            class="admin-runtime-exec-grid w-full divide-y divide-slate-800 text-sm"
            :class="executionTableScrollX ? 'min-w-[1520px]' : ''"
          >
            <colgroup>
              <col class="exec-col-id" />
              <col class="exec-col-user" />
              <col class="exec-col-scenario" />
              <col class="exec-col-prompt" />
              <col class="exec-col-note" />
              <col class="exec-col-status" />
              <col class="exec-col-stage" />
              <col class="exec-col-terminal" />
              <col class="exec-col-retries" />
              <col class="exec-col-created" />
              <col class="exec-col-actions" />
            </colgroup>
            <thead class="bg-slate-900/85 text-left text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th
                  class="sticky left-0 z-[1] min-w-[12.5rem] max-w-[12.5rem] bg-slate-900/95 px-3 py-3 align-bottom backdrop-blur-sm"
                  scope="col"
                >
                  执行 ID
                </th>
                <th class="px-3 py-3 align-bottom whitespace-nowrap" scope="col">用户标识</th>
                <th class="whitespace-normal px-3 py-3 align-bottom" scope="col">场景 ID</th>
                <th class="whitespace-normal px-3 py-3 align-bottom font-normal normal-case tracking-normal" scope="col">
                  Prompt · 快照
                </th>
                <th class="whitespace-normal px-3 py-3 align-bottom" scope="col">意图摘要</th>
                <th class="align-bottom whitespace-nowrap px-3 py-3" scope="col">运行状态</th>
                <th class="align-bottom whitespace-nowrap px-3 py-3" scope="col">当前阶段</th>
                <th class="align-bottom whitespace-nowrap px-3 py-3" scope="col">业务终态</th>
                <th
                  class="align-bottom px-3 py-3 text-right text-[11px] font-medium tabular-nums whitespace-nowrap normal-case tracking-normal"
                  scope="col"
                >
                  重试次数
                </th>
                <th class="whitespace-normal px-3 py-3 align-bottom font-mono normal-case" scope="col">
                  <AdminTimeTh>创建时间</AdminTimeTh>
                </th>
                <th
                  class="sticky right-0 z-[1] min-w-[21rem] bg-slate-900/95 px-3 py-3 text-right align-bottom whitespace-nowrap backdrop-blur-sm"
                  scope="col"
                >
                  操作
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800">
              <UiTableEmptyRow v-if="loading" :colspan="11" state="loading" />
              <UiTableEmptyRow
                v-else-if="displayItems.length === 0"
                :colspan="11"
                state="filtered"
              />
              <tr
                v-for="r in displayItems"
                v-else
                :key="r.executionId"
                class="cursor-pointer transition-colors hover:bg-slate-900/55"
                @click="onRowClick($event, r)"
              >
                <td
                  class="sticky left-0 z-[1] max-w-[12.5rem] bg-slate-950/80 px-3 py-2 backdrop-blur-sm align-middle"
                >
                  <span
                    class="block truncate font-mono text-xs text-slate-200"
                    :title="r.executionId"
                  >{{ r.executionId }}</span>
                </td>
                <td class="max-w-[9rem] truncate px-3 py-2 align-middle font-mono text-xs text-slate-400" :title="r.userId">
                  {{ maskUserId(r.userId) }}
                </td>
                <td class="max-w-[11rem] truncate px-3 py-2 align-middle font-mono text-xs text-slate-400" :title="r.scenarioId ?? ''">
                  {{ r.scenarioId ?? '—' }}
                </td>
                <td class="max-w-[12rem] min-w-[8rem] px-3 py-2 align-middle text-xs leading-snug text-slate-400">
                  <div class="font-mono text-[11px] text-sky-300/90">
                    {{ formatPromptPackVersionLabel(r.promptPackVersion) }}
                  </div>
                  <div
                    class="mt-0.5 line-clamp-2 break-all font-mono text-[10px] text-slate-500"
                    :title="summarizeTradingPromptBinding(r.resolvedPromptBinding ?? null)"
                  >
                    {{ summarizeTradingPromptBinding(r.resolvedPromptBinding ?? null) }}
                  </div>
                </td>
                <td class="min-w-0 px-3 py-2 align-middle text-slate-300">
                  <span class="line-clamp-2 text-xs leading-snug" :title="r.note ?? ''">{{
                    r.note?.trim() || '—'
                  }}</span>
                </td>
                <td class="whitespace-nowrap px-3 py-2 align-middle">
                  <span
                    class="inline-flex shrink-0 items-center whitespace-nowrap rounded-md border px-2 py-0.5 text-[11px] font-medium tracking-tight"
                    :class="statusTagClass(r.state)"
                  >
                    {{ zhExecutionRuntimeStatus(r.state) }}
                  </span>
                </td>
                <td class="whitespace-nowrap px-3 py-2 align-middle text-xs text-slate-500">—</td>
                <td class="whitespace-nowrap px-3 py-2 align-middle text-xs text-slate-500">—</td>
                <td class="whitespace-nowrap px-3 py-2 text-right align-middle font-mono text-xs tabular-nums text-slate-500">
                  —
                </td>
                <td class="whitespace-nowrap px-3 py-2 align-middle font-mono text-xs tabular-nums text-slate-500">
                  {{ formatIsoTime(r.createdAt) }}
                </td>
                <td
                  class="sticky right-0 z-[1] min-w-[21rem] bg-slate-950/80 px-3 py-2 align-middle text-right backdrop-blur-sm"
                  @click.stop
                >
                  <div class="flex flex-wrap items-center justify-end gap-1.5">
                    <UiTableAction variant="sky" icon="eye" @click="previewRow = r">预览</UiTableAction>
                    <UiClipboardTipAction variant="slate" :text="r.executionId" />
                    <UiTableAction
                      variant="emerald"
                      icon="file-text"
                      :to="{
                        name: 'runtime.execution-detail',
                        params: { executionId: r.executionId },
                        query: { tab: 'timeline' },
                      }"
                    >
                      详情
                    </UiTableAction>
                    <UiTableAction variant="rose" icon="trash" @click.stop="openExecDelete(r)">删除</UiTableAction>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- SpecFooter -->
        <footer class="border-t border-slate-800/80 pt-4 text-xs text-slate-600">
          <p class="mb-2 text-slate-500">规格路径：</p>
          <ul class="list-inside list-disc space-y-1">
            <li v-for="p in SPEC_FOOTER_PATHS" :key="p">规格要求 / {{ p }}</li>
          </ul>
        </footer>
      </div>
    </section>

    <!-- 预览层：对齐原型 Drawer -->
    <Teleport to="body">
      <Transition name="admin-drawer-scrim">
        <div
          v-if="previewRow"
          class="fixed inset-0 z-40 bg-slate-950/55"
          aria-hidden="true"
          @click.self="closePreview"
        />
      </Transition>
      <Transition name="admin-drawer-panel">
        <aside
          v-if="previewRow"
          class="fixed inset-y-0 right-0 z-50 flex w-full max-w-[440px] flex-col border-l border-slate-800 bg-slate-950 shadow-2xl"
          role="dialog"
          aria-modal="true"
          aria-label="执行摘要预览"
        >
          <div class="flex items-start justify-between gap-2 border-b border-slate-800 px-4 py-3">
            <h3 class="text-sm font-medium text-white">执行摘要 · 预览</h3>
            <div class="flex shrink-0 items-center gap-2">
              <UiButton type="button" size="sm" @click="openDetailFromPreview">打开详情页</UiButton>
              <button
                type="button"
                class="rounded p-1 text-slate-500 hover:bg-slate-800 hover:text-slate-300"
                aria-label="关闭"
                @click="closePreview"
              >
                <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                  <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
                </svg>
              </button>
            </div>
          </div>
          <div class="min-h-0 flex-1 overflow-y-auto px-4 py-4 text-sm">
            <div class="rounded-lg border border-slate-800 bg-slate-900/50 p-3.5">
              <p class="text-xs text-slate-500">执行 ID</p>
              <p class="mt-1 break-all font-mono text-xs text-slate-200">{{ previewRow.executionId }}</p>
              <div class="mt-2.5 flex flex-wrap gap-2">
                <span
                  class="inline-flex shrink-0 whitespace-nowrap rounded-md border px-2 py-0.5 text-[11px] font-medium tracking-tight"
                  :class="statusTagClass(previewRow.state)"
                >
                  {{ zhExecutionRuntimeStatus(previewRow.state) }}
                </span>
              </div>
            </div>

            <dl class="mt-4 space-y-3 text-sm">
              <div>
                <dt class="text-xs text-slate-500">用户标识</dt>
                <dd class="mt-0.5 font-mono text-slate-300">{{ previewRow.userId }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">场景 ID</dt>
                <dd class="mt-0.5 break-all font-mono text-slate-300">{{ previewRow.scenarioId ?? '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">channel</dt>
                <dd class="mt-0.5 text-slate-300">{{ previewRow.channel ?? '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">source</dt>
                <dd class="mt-0.5 break-all text-xs text-slate-400">{{ previewRow.source ?? '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">意图摘要</dt>
                <dd class="mt-0.5 text-slate-300">{{ previewRow.note?.trim() || '—' }}</dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">promptPackVersion</dt>
                <dd class="mt-0.5 font-mono text-xs text-sky-300/90">
                  {{ formatPromptPackVersionLabel(previewRow.promptPackVersion) }}
                </dd>
              </div>
              <div>
                <dt class="text-xs text-slate-500">trade 绑定摘要</dt>
                <dd class="mt-0.5 break-all font-mono text-[11px] text-slate-400">
                  {{ summarizeTradingPromptBinding(previewRow.resolvedPromptBinding ?? null) }}
                </dd>
              </div>
              <details v-if="previewRow.resolvedPromptBinding != null" class="rounded-md border border-slate-800 bg-slate-900/60 p-2">
                <summary class="cursor-pointer text-xs font-medium text-slate-400">resolvedPromptBinding（JSON）</summary>
                <pre class="mt-2 max-h-48 overflow-auto font-mono text-[10px] leading-relaxed text-slate-500">{{
                  fmtPromptBindingFull(previewRow)
                }}</pre>
              </details>
              <div>
                <dt class="text-xs text-slate-500">创建时间</dt>
                <dd class="mt-0.5 font-mono text-xs text-slate-400">{{ formatIsoTime(previewRow.createdAt) }}</dd>
              </div>
            </dl>

            <div class="mt-5 space-y-2 border-t border-slate-800 pt-4">
              <RouterLink
                :to="`/ai/runtime-orchestration?tab=routing&scenario=${encodeURIComponent(previewRow.scenarioId ?? '')}`"
                class="flex h-10 w-full items-center justify-center rounded-md border border-slate-600 bg-slate-800/40 text-sm font-medium text-slate-200 transition-colors hover:bg-slate-800/70 active:scale-[0.99]"
              >
                编排
              </RouterLink>
              <RouterLink
                :to="`/runtime/executions/${previewRow.executionId}?tab=queue`"
                class="flex h-10 w-full items-center justify-center rounded-md border border-slate-600 bg-slate-800/40 text-sm font-medium text-slate-200 transition-colors hover:bg-slate-800/70 active:scale-[0.99]"
              >
                任务队列
              </RouterLink>
              <RouterLink
                :to="`/runtime/executions/${previewRow.executionId}?tab=events`"
                class="flex h-10 w-full items-center justify-center rounded-md border border-slate-600 bg-slate-800/40 text-sm font-medium text-slate-200 transition-colors hover:bg-slate-800/70 active:scale-[0.99]"
              >
                运行事件
              </RouterLink>
              <RouterLink
                :to="observabilityHref(previewRow)"
                class="flex h-10 w-full items-center justify-center rounded-md border border-emerald-500/30 bg-emerald-500/10 text-sm font-medium text-emerald-300 transition-colors hover:bg-emerald-500/15 active:scale-[0.99]"
              >
                执行链路协查
              </RouterLink>
              <UiButton variant="danger" type="button" class="w-full" @click="openDeleteFromPreview">
                删除此记录
              </UiButton>
            </div>
          </div>
        </aside>
      </Transition>
    </Teleport>

    <UiModal
      v-model:open="execDeleteOpen"
      title="确认删除执行记录"
      :show-default-close="false"
      description="硬删除数据库中的 agent_execution 行（DELETE · 204）。不可恢复，通常仅用于联调清理。"
    >
      <div v-if="execPendingDelete" class="space-y-3">
        <p class="text-sm text-slate-300">
          即将删除
          <span class="font-mono text-white">{{ execPendingDelete.executionId }}</span>
        </p>
        <p v-if="execDeleteError" class="text-sm text-rose-300">{{ execDeleteError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" @click="cancelExecDelete">取消</UiButton>
        <UiButton variant="danger" type="button" :loading="execDeleting" @click="confirmedExecDelete">
          确认删除
        </UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>

<style scoped>
/* 执行列表：colgroup 按比例分配宽度，减轻窄列短语换行（与 table-fixed 配合） */
.admin-runtime-exec-grid {
  table-layout: fixed;
}
.admin-runtime-exec-grid col.exec-col-id {
  width: 12%;
}
.admin-runtime-exec-grid col.exec-col-user {
  width: 8%;
}
.admin-runtime-exec-grid col.exec-col-scenario {
  width: 8%;
}
.admin-runtime-exec-grid col.exec-col-prompt {
  width: 11%;
}
.admin-runtime-exec-grid col.exec-col-note {
  width: 18%;
}
.admin-runtime-exec-grid col.exec-col-status {
  width: 8%;
}
.admin-runtime-exec-grid col.exec-col-stage {
  width: 6%;
}
.admin-runtime-exec-grid col.exec-col-terminal {
  width: 6%;
}
.admin-runtime-exec-grid col.exec-col-retries {
  width: 5%;
}
.admin-runtime-exec-grid col.exec-col-created {
  width: 11%;
  /* font-mono text-xs 下完整 YYYY-MM-DD HH:mm:ss；过窄时会被右侧 sticky「操作」背景盖住末位 */
  min-width: 14rem;
}
.admin-runtime-exec-grid col.exec-col-actions {
  width: 15%;
  min-width: 21rem;
}
</style>
