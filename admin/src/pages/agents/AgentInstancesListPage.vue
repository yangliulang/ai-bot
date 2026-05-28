<!--
作者: 杨永的Agent
日期: 2026-05-26
修改功能: **I02**「创建实例」Modal · `createAgentInstance` 联调 · 成功后刷新列表
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 刷新/删除等操作反馈改用全局 **`adminToast`**
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 查询条命中统计改用 **`UiStatChip`**，与刷新/重置按钮行高对齐
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 实例列表操作列 **DELETE** + **UiModal** 二次确认（I06 · FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 数据列表空态 **`UiTableEmptyRow`**；无数据时取消表格横向滚动
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **TG 账号**列 **加宽**；`id:` / `name:` / **`主站:`** 各占 **单行 `truncate`**（`title` 展示全文）；去掉 **`inst-col-tg-wrap`** 多行特例
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **数据列表 · 操作** 改用 **`UiTableAction`**（图标 + outline 紧凑按钮）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **数据列表** 表头与单元格（含 TG 各行）单行展示；超长 **`truncate`** + **`title`**
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **数据列表** **左**：勾选框 + **实例 ID** `sticky`，**右**：操作列 `sticky`，与执行记录表格布局一致（`colgroup` + `overflow-x-auto`）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **预览 Drawer** **`admin-drawer-*`** backdrop + 侧栏滑入缓动（与 Execution 列表对齐）
作者: 杨永的Agent
日期: 2026-05-17
修改功能: 数据列表表格 **`align-middle`**，单元格内容相对行垂直居中
作者: 杨永的Agent
日期: 2026-05-16
修改功能: 数据列表 **`table-fixed`** + 列 **`min-w-0`** / **`truncate`**；**TG 账号** / **交易所子账号** 分列；去掉单元格内冗余「TG ID」「绑定 ID」标记（表头已区分）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: **G01** 横幅、**R06** 批量 Runtime、门禁轮询禁用 Start/Resume（接续 FE_HANDOFF · `admin_agent_control`）
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 实例列表 IA 与 product-doc InstancesPage 对齐：查询条（关键字/门禁/运行态）、命中统计、表头数据列表、行点击预览侧栏、协查深链
-->
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import GlobalAgentGateBanner from '@/features/agents/GlobalAgentGateBanner.vue'
import {
  filterInstanceListVm,
  mapAgentRowToListVm,
  type AgentInstanceListVm,
} from '@/entities/agents/agent-instance-list-vm'
import {
  getGlobalAgentGate,
  postAgentInstancesRuntimeBatch,
  type AgentBatchRuntimeResponse,
  type AgentRuntimeControlAction,
  type GlobalAgentGateResponse,
} from '@/shared/api/agent-agent-control'
import {
  createAgentInstance,
  deleteAgentInstance,
  formatAgentInstanceDeleteError,
  formatAgentInstanceWriteError,
  listAgentInstances,
  type AgentInstanceRow,
} from '@/shared/api/agent-instances'
import { AppError } from '@/shared/api/errors'
import { adminNotifyManualRefresh, adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import { zhAgentState, zhRuntimeState, zhSubAccountStatus } from '@/shared/copy/zh-agent-labels'
import {
  agentStateTagClass,
  formatInstanceAt,
  runtimeStateTagClass,
} from '@/shared/utils/agent-instance-ui'
import { buildObservabilitySearch } from '@/shared/utils/observability-deep-link'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminTimeTh from '@/shared/ui/AdminTimeTh.vue'
import {
  ADMIN_TOOLBAR_CLUSTER_CLASS,
  AdminPageHeader,
  UiButton,
  UiInput,
  UiModal,
  UiSelect,
  UiStatChip,
  UiSwitch,
  UiTableAction,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
  type UiSelectOption,
} from '@/shared/ui'

const route = useRoute()
const router = useRouter()

const allRows = ref<AgentInstanceRow[]>([])
const loading = ref(false)
const loadError = ref<string | null>(null)
const filterError = ref<string | null>(null)
const truncatedFetch = ref(false)

const keywordInput = ref('')
const gateDraft = ref('all')
const rtDraft = ref('all')

const previewVm = ref<AgentInstanceListVm | null>(null)

const instDeleteOpen = ref(false)
const instPendingDelete = ref<AgentInstanceListVm | null>(null)
const instDeleting = ref(false)
const instDeleteError = ref<string | null>(null)

const createOpen = ref(false)
const createSubmitting = ref(false)
const createError = ref<string | null>(null)
const createTelegramUserId = ref('')
const createTemplateId = ref('')
const createTemplateVersion = ref('')
const createExchangeSubAccountUserId = ref('')

function openCreateModal() {
  createError.value = null
  createTelegramUserId.value = ''
  createTemplateId.value = ''
  createTemplateVersion.value = ''
  createExchangeSubAccountUserId.value = ''
  createOpen.value = true
}

function cancelCreate() {
  if (createSubmitting.value) return
  createOpen.value = false
  createError.value = null
}

async function submitCreate() {
  const tg = createTelegramUserId.value.trim()
  if (!tg) {
    createError.value = 'telegramUserId 必填（数值串）'
    return
  }
  if (!/^\d+$/.test(tg)) {
    createError.value = 'telegramUserId 须为纯数字'
    return
  }
  createSubmitting.value = true
  createError.value = null
  try {
    const res = await createAgentInstance({
      telegramUserId: tg,
      templateId: createTemplateId.value.trim() || undefined,
      templateVersion: createTemplateVersion.value.trim() || undefined,
      exchangeSubAccountUserId: createExchangeSubAccountUserId.value.trim() || undefined,
    })
    createOpen.value = false
    adminToastSuccess(`已创建实例 ${res.instanceId}`)
    await load()
  } catch (e) {
    const msg = formatAgentInstanceWriteError(e)
    createError.value = msg
    adminToastError(msg)
  } finally {
    createSubmitting.value = false
  }
}

function keywordFromRoute(): string {
  const q = String(route.query.q ?? '').trim()
  if (q) return q
  const user = String(route.query.user ?? '').trim()
  const id = String(route.query.id ?? '').trim()
  return `${user}${user && id ? ' ' : ''}${id}`
}

function syncGateRtFromRoute() {
  const g = String(route.query.gate ?? 'all')
  gateDraft.value =
    g === 'NORMAL' ||
    g === 'BILLING_BLOCKED' ||
    g === 'GLOBAL_OFF' ||
    g === 'OPS_SUSPENDED' ||
    g === 'MEMBERSHIP_BLOCKED' ||
    g === 'AGENT_SUBACCOUNT_BLOCKED'
      ? g
      : 'all'
  const r = String(route.query.rt ?? 'all')
  rtDraft.value =
    r === 'RUNNING' || r === 'PAUSED' || r === 'STOPPED' || r === 'STARTING' || r === 'ERROR'
      ? r
      : 'all'
}

function syncFiltersFromRoute() {
  keywordInput.value = keywordFromRoute()
  syncGateRtFromRoute()
}

watch(
  () => [route.query.q, route.query.user, route.query.id],
  () => {
    keywordInput.value = keywordFromRoute()
  },
  { deep: true },
)

watch(
  () => [route.query.gate, route.query.rt],
  () => {
    syncGateRtFromRoute()
  },
  { deep: true },
)

const gateOptions = computed<UiSelectOption[]>(() => [
  { value: 'all', label: '全部' },
  { value: 'NORMAL', label: zhAgentState('NORMAL') },
  { value: 'BILLING_BLOCKED', label: zhAgentState('BILLING_BLOCKED') },
  { value: 'GLOBAL_OFF', label: zhAgentState('GLOBAL_OFF') },
  { value: 'OPS_SUSPENDED', label: zhAgentState('OPS_SUSPENDED') },
  { value: 'MEMBERSHIP_BLOCKED', label: zhAgentState('MEMBERSHIP_BLOCKED') },
  { value: 'AGENT_SUBACCOUNT_BLOCKED', label: zhAgentState('AGENT_SUBACCOUNT_BLOCKED') },
])

const rtOptions = computed<UiSelectOption[]>(() => [
  { value: 'all', label: '全部' },
  { value: 'RUNNING', label: zhRuntimeState('RUNNING') },
  { value: 'PAUSED', label: zhRuntimeState('PAUSED') },
  { value: 'STOPPED', label: zhRuntimeState('STOPPED') },
  { value: 'STARTING', label: zhRuntimeState('STARTING') },
  { value: 'ERROR', label: zhRuntimeState('ERROR') },
])

const listVms = computed(() => allRows.value.map(mapAgentRowToListVm))

const filteredVms = computed(() =>
  filterInstanceListVm(listVms.value, keywordInput.value, gateDraft.value, rtDraft.value),
)

const sortedRows = computed(() =>
  [...filteredVms.value].sort((a, b) => b.lastActiveAt.localeCompare(a.lastActiveAt)),
)

const filtersActive = computed(
  () =>
    Boolean(keywordInput.value.trim()) ||
    (gateDraft.value && gateDraft.value !== 'all') ||
    (rtDraft.value && rtDraft.value !== 'all'),
)

const instanceTableScrollX = computed(() => !loading.value && sortedRows.value.length > 0)

function replaceQuery(updates: Record<string, string | undefined>) {
  const q: Record<string, string> = {}
  for (const [k, v] of Object.entries(route.query)) {
    if (typeof v === 'string') q[k] = v
    else if (Array.isArray(v) && typeof v[0] === 'string') q[k] = v[0]
  }
  for (const [k, v] of Object.entries(updates)) {
    if (v === undefined || v === '') delete q[k]
    else q[k] = v
  }
  void router.replace({ path: route.path, query: q })
}

watch(gateDraft, (g) => {
  replaceQuery({ gate: g === 'all' ? undefined : g })
})

watch(rtDraft, (r) => {
  replaceQuery({ rt: r === 'all' ? undefined : r })
})

const MAX_ROWS_PULL = 2000
const FETCH_LIMIT = 200

async function onRefresh() {
  await load()
  const err = filterError.value || loadError.value
  adminNotifyManualRefresh(true, {
    ok: !err,
    successMessage: '已刷新',
    errorMessage: err,
  })
}

async function load() {
  const id = String(route.query.id ?? '').trim()
  const user = String(route.query.user ?? '').trim()
  if (user && !/^\d+$/.test(user)) {
    filterError.value = '地址栏 user 须为 Telegram 数值 id（纯数字）'
    return
  }
  filterError.value = null
  loading.value = true
  loadError.value = null
  truncatedFetch.value = false
  try {
    const acc: AgentInstanceRow[] = []
    let offset = 0
    let total = Infinity
    while (offset < total && acc.length < MAX_ROWS_PULL) {
      const res = await listAgentInstances({
        limit: FETCH_LIMIT,
        offset,
        instanceId: id || undefined,
        telegramUserId: user || undefined,
      })
      total = res.total
      acc.push(...res.items)
      offset += res.items.length
      if (res.items.length === 0) break
    }
    allRows.value = acc
    if (offset < total) truncatedFetch.value = true
  } catch (e) {
    loadError.value = e instanceof AppError ? e.message : e instanceof Error ? e.message : '加载失败'
    allRows.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  syncFiltersFromRoute()
  void load()
  void refreshRuntimeGate()
  gatePollTimer = setInterval(refreshRuntimeGate, 30_000)
})

onUnmounted(() => {
  if (gatePollTimer) clearInterval(gatePollTimer)
})

function resetFilters() {
  keywordInput.value = ''
  gateDraft.value = 'all'
  rtDraft.value = 'all'
  previewVm.value = null
  void router.replace({ path: '/agents/instances', query: {} })
  void load()
}

function openPreview(vm: AgentInstanceListVm) {
  previewVm.value = vm
}

function closePreview() {
  previewVm.value = null
}

function openInstDelete(vm: AgentInstanceListVm) {
  instPendingDelete.value = vm
  instDeleteError.value = null
  instDeleteOpen.value = true
}

function cancelInstDelete() {
  instDeleteOpen.value = false
  instPendingDelete.value = null
  instDeleteError.value = null
}

async function confirmedInstDelete() {
  const vm = instPendingDelete.value
  if (!vm) return
  instDeleting.value = true
  instDeleteError.value = null
  try {
    await deleteAgentInstance(vm.instanceId)
    instDeleteOpen.value = false
    instPendingDelete.value = null
    if (previewVm.value?.instanceId === vm.instanceId) previewVm.value = null
    selectedInstanceIds.value = selectedInstanceIds.value.filter((id) => id !== vm.instanceId)
    await load()
    adminToastSuccess('已删除 Agent 实例')
  } catch (e) {
    const msg = formatAgentInstanceDeleteError(e)
    instDeleteError.value = msg
    adminToastError(msg)
  } finally {
    instDeleting.value = false
  }
}

const observabilityHref = computed(() => {
  const u = previewVm.value?.userId
  if (!u) return '/observability'
  return `/observability${buildObservabilitySearch({ userId: u, tab: 'execution' })}`
})

/** G01 · 用于批量按钮禁用（与横幅数据源一致） */
const runtimeGate = ref<GlobalAgentGateResponse | null>(null)
let gatePollTimer: ReturnType<typeof setInterval> | null = null

async function refreshRuntimeGate() {
  try {
    runtimeGate.value = await getGlobalAgentGate()
  } catch {
    /* 静默：横幅仍有独立轮询 */
  }
}

const batchStartResumeBlocked = computed(() => {
  const g = runtimeGate.value
  if (!g) return false
  return !g.globalAgentSwitchOn || g.opsSuspended
})

const selectedInstanceIds = ref<string[]>([])
const batchSubmitting = ref(false)
const batchModalOpen = ref(false)
const batchOutcome = ref<AgentBatchRuntimeResponse | null>(null)

const selectedCount = computed(() => selectedInstanceIds.value.length)

const allVisibleSelected = computed(() => {
  const rows = sortedRows.value
  if (rows.length === 0) return false
  const sel = new Set(selectedInstanceIds.value)
  return rows.every((r) => sel.has(r.instanceId))
})

function toggleRowSelected(instanceId: string, checked: boolean) {
  const set = new Set(selectedInstanceIds.value)
  if (checked) set.add(instanceId)
  else set.delete(instanceId)
  selectedInstanceIds.value = [...set]
}

function onHeaderSelectChange(checked: boolean) {
  if (checked) {
    const set = new Set(selectedInstanceIds.value)
    for (const r of sortedRows.value) set.add(r.instanceId)
    selectedInstanceIds.value = [...set]
  } else {
    const visible = new Set(sortedRows.value.map((r) => r.instanceId))
    selectedInstanceIds.value = selectedInstanceIds.value.filter((id) => !visible.has(id))
  }
}

function clearBatchSelection() {
  selectedInstanceIds.value = []
}

async function runBatchRuntime(action: AgentRuntimeControlAction) {
  const ids = [...selectedInstanceIds.value]
  if (ids.length === 0) return
  if ((action === 'start' || action === 'resume') && batchStartResumeBlocked.value) {
    window.alert('当前全局门禁禁止 Start / Resume（见顶部 G01 横幅）。')
    return
  }
  const label =
    action === 'pause'
      ? '暂停'
      : action === 'stop'
        ? '停止'
        : action === 'resume'
          ? '恢复'
          : '启动'
  const ok = window.confirm(`将对已选的 ${ids.length} 个实例执行批量「${label}」？`)
  if (!ok) return
  batchSubmitting.value = true
  try {
    const res = await postAgentInstancesRuntimeBatch({ instanceIds: ids, action })
    batchOutcome.value = res
    batchModalOpen.value = true
    clearBatchSelection()
    await load()
    await refreshRuntimeGate()
  } catch (e) {
    const msg =
      e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '批量请求失败'
    window.alert(msg)
  } finally {
    batchSubmitting.value = false
  }
}

function setBatchModalOpen(v: boolean) {
  batchModalOpen.value = v
}

watch(allRows, () => {
  const allowed = new Set(allRows.value.map((r) => r.instanceId))
  selectedInstanceIds.value = selectedInstanceIds.value.filter((id) => allowed.has(id))
})
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="实例管理"
      description="查询、筛选与批量操作 Runtime Agent 实例；门禁与运行态以列表列为准。"
      dev-meta="pageId · ai.agents-instances · GET /api/v1/admin/agents/instances"
    />

    <GlobalAgentGateBanner />

    <!-- 查询条件（对齐原型 InstancesFilterPanel） -->
    <section class="admin-panel p-3 sm:p-4">
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
          <span class="inline-flex h-8 items-center text-sm font-semibold text-white">查询条件</span>
          <UiStatChip tone="info">
            命中 {{ sortedRows.length }} / {{ listVms.length }}
          </UiStatChip>
        </div>
        <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
          <UiButton type="button" variant="primary" size="sm" :disabled="loading" @click="openCreateModal">
            创建实例
          </UiButton>
          <UiButton type="button" variant="secondary" size="sm" :loading="loading" @click="onRefresh">
            刷新
          </UiButton>
          <UiButton
            type="button"
            variant="secondary"
            size="sm"
            :disabled="loading"
            @click="resetFilters"
          >
            重置
          </UiButton>
        </div>
      </div>

      <div class="mt-3 grid gap-4 lg:grid-cols-12">
        <div class="lg:col-span-5">
          <UiInput
            v-model="keywordInput"
            label="关键字"
            placeholder="实例 ID、TG ID、TG 用户名、主站 UID、交易所子账号 ID（模糊匹配）"
            type="search"
          />
          <p class="mt-1 text-[11px] text-slate-500">筛选包含实例 ID、Telegram、主站 UID、交易所子账号字段。</p>
        </div>
        <div class="lg:col-span-3">
          <UiSelect v-model="gateDraft" label="门禁" :options="gateOptions" placeholder="门禁" />
        </div>
        <div class="lg:col-span-4">
          <UiSelect v-model="rtDraft" label="运行态" :options="rtOptions" placeholder="运行态" />
        </div>
      </div>
      <p class="mt-3 text-xs text-slate-500">列表随条件<strong class="font-medium text-slate-400">即时更新</strong>。</p>
      <p v-if="filterError" class="mt-2 text-sm text-amber-300" role="alert">{{ filterError }}</p>
    </section>

    <div
      v-if="loadError"
      class="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-200"
      role="alert"
    >
      {{ loadError }}
    </div>
    <p v-if="truncatedFetch" class="text-xs text-amber-300/90">
      已最多拉取前 {{ MAX_ROWS_PULL }} 条；总量更大时请用地址栏
      <code class="rounded bg-slate-800 px-1">?id=</code> /
      <code class="rounded bg-slate-800 px-1">?user=</code>
      缩小服务端范围。
    </p>

    <div
      v-if="selectedCount > 0"
      class="flex flex-wrap items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2 text-sm text-slate-300"
    >
      <span class="font-medium text-white">已选 {{ selectedCount }} 条</span>
      <UiButton
        type="button"
        size="sm"
        variant="secondary"
        :loading="batchSubmitting"
        :disabled="batchStartResumeBlocked"
        :title="batchStartResumeBlocked ? 'G01：禁止 Start / Resume' : ''"
        @click="runBatchRuntime('start')"
      >
        批量 Start
      </UiButton>
      <UiButton
        type="button"
        size="sm"
        variant="secondary"
        :loading="batchSubmitting"
        :disabled="batchStartResumeBlocked"
        :title="batchStartResumeBlocked ? 'G01：禁止 Start / Resume' : ''"
        @click="runBatchRuntime('resume')"
      >
        批量 Resume
      </UiButton>
      <UiButton type="button" size="sm" variant="secondary" :loading="batchSubmitting" @click="runBatchRuntime('pause')">
        批量 Pause
      </UiButton>
      <UiButton type="button" size="sm" variant="danger" :loading="batchSubmitting" @click="runBatchRuntime('stop')">
        批量 Stop
      </UiButton>
      <UiButton type="button" size="sm" variant="ghost" :disabled="batchSubmitting" @click="clearBatchSelection">
        清空选择
      </UiButton>
    </div>

    <!-- 数据列表 -->
    <section class="border-t border-slate-800 pt-4">
      <div class="mb-3 flex flex-wrap items-baseline justify-between gap-2">
        <h2 class="text-[15px] font-semibold text-white">数据列表</h2>
        <span class="text-xs text-slate-500">共 {{ sortedRows.length }} 条</span>
      </div>

      <div
        class="admin-agents-instance-table-host rounded-lg border border-slate-800"
        :class="adminTableHostOverflowClass(instanceTableScrollX)"
      >
        <table
          class="admin-agent-inst-grid w-full table-fixed text-left text-sm"
          :class="instanceTableScrollX ? 'min-w-[1600px]' : ''"
        >
          <colgroup>
            <col class="inst-col-check" />
            <col class="inst-col-id" />
            <col class="inst-col-tg" />
            <col class="inst-col-exchange" />
            <col class="inst-col-gate" />
            <col class="inst-col-runtime" />
            <col class="inst-col-block" />
            <col class="inst-col-sub" />
            <col class="inst-col-last" />
            <col class="inst-col-created" />
            <col class="inst-col-ops" />
          </colgroup>
          <thead class="border-b border-slate-800 bg-slate-900/80 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th
                scope="col"
                class="sticky left-0 z-[1] w-14 min-w-[3.5rem] max-w-[3.5rem] border-r border-slate-800/80 bg-slate-900/95 px-3 py-2 align-middle font-medium whitespace-nowrap backdrop-blur-sm"
              >
                <UiSwitch
                  size="sm"
                  :model-value="sortedRows.length > 0 && allVisibleSelected"
                  aria-label="全选当前页（筛选结果）"
                  @update:model-value="onHeaderSelectChange"
                />
              </th>
              <th
                scope="col"
                class="sticky left-14 z-[1] min-w-0 whitespace-nowrap bg-slate-900/95 px-3 py-2 align-middle font-medium backdrop-blur-sm"
              >
                实例 ID
              </th>
              <th scope="col" class="min-w-0 px-3 py-2 align-middle font-medium whitespace-nowrap">TG 账号</th>
              <th scope="col" class="min-w-0 px-3 py-2 align-middle font-medium whitespace-nowrap">
                交易所子账号
              </th>
              <th scope="col" class="min-w-0 px-3 py-2 align-middle font-medium whitespace-nowrap">门禁</th>
              <th scope="col" class="min-w-0 px-3 py-2 align-middle font-medium whitespace-nowrap">运行态</th>
              <th scope="col" class="min-w-0 px-3 py-2 align-middle font-medium whitespace-nowrap">阻断原因</th>
              <th scope="col" class="min-w-0 px-3 py-2 align-middle font-medium whitespace-nowrap">子账户状态</th>
              <th
                scope="col"
                class="min-w-0 px-3 py-2 align-middle font-medium whitespace-nowrap normal-case tracking-normal"
              >
                <AdminTimeTh>最近活跃</AdminTimeTh>
              </th>
              <th
                scope="col"
                class="min-w-0 px-3 py-2 align-middle font-medium whitespace-nowrap normal-case tracking-normal"
              >
                <AdminTimeTh>创建</AdminTimeTh>
              </th>
              <th
                scope="col"
                class="sticky right-0 z-[1] border-l border-slate-800 bg-slate-900/95 px-3 py-2 text-right align-middle font-medium backdrop-blur-sm whitespace-nowrap min-w-[20rem]"
              >
                操作
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-slate-200">
            <UiTableEmptyRow v-if="loading && sortedRows.length === 0" :colspan="11" state="loading" />
            <UiTableEmptyRow
              v-else-if="!loading && sortedRows.length === 0"
              :colspan="11"
              :state="filtersActive ? 'filtered' : 'empty'"
              :title="filtersActive ? '没有符合当前筛选条件的实例' : '暂无实例数据'"
              :description="filtersActive ? '可尝试放宽或重置筛选条件。' : ''"
            >
              <UiButton v-if="filtersActive" type="button" size="sm" variant="secondary" @click="resetFilters">
                重置筛选
              </UiButton>
            </UiTableEmptyRow>
            <tr
              v-for="i in sortedRows"
              :key="i.instanceId"
              class="group cursor-pointer hover:bg-slate-900/50"
              @click="openPreview(i)"
            >
              <td
                class="sticky left-0 z-[1] w-14 min-w-[3.5rem] max-w-[3.5rem] border-r border-slate-800/80 bg-slate-950/80 px-3 py-2 align-middle backdrop-blur-sm group-hover:bg-slate-900/55"
                @click.stop
              >
                <UiSwitch
                  size="sm"
                  :model-value="selectedInstanceIds.includes(i.instanceId)"
                  :aria-label="`选择实例 ${i.instanceId}`"
                  @update:model-value="toggleRowSelected(i.instanceId, $event)"
                />
              </td>
              <td
                class="sticky left-14 z-[1] min-w-0 bg-slate-950/80 px-3 py-2 align-middle backdrop-blur-sm group-hover:bg-slate-900/55"
              >
                <code
                  class="block w-full truncate font-mono text-xs text-slate-200"
                  :title="i.instanceId"
                  >{{ i.instanceId }}</code
                >
              </td>
              <td class="min-w-0 px-3 py-2 align-middle">
                <div class="flex min-w-0 flex-col gap-0.5 text-xs leading-tight">
                  <div
                    class="truncate font-mono font-medium whitespace-nowrap text-slate-200"
                    :title="`id: ${i.userId}`"
                  >
                    id: {{ i.userId }}
                  </div>
                  <div
                    class="truncate whitespace-nowrap text-slate-500"
                    :title="`name: ${i.userEmailMasked?.trim() || '—'}`"
                  >
                    name: {{ i.userEmailMasked?.trim() || '—' }}
                  </div>
                  <div
                    v-if="i.raw.userId?.trim()"
                    class="truncate whitespace-nowrap font-mono text-[11px] text-slate-600"
                    :title="`主站: ${i.raw.userId}`"
                  >
                    主站: {{ i.raw.userId }}
                  </div>
                </div>
              </td>
              <td class="min-w-0 px-3 py-2 align-middle whitespace-nowrap">
                <div
                  class="truncate font-mono text-xs text-slate-300"
                  :class="i.exchangeSubAccountDisplay === '—' ? 'text-slate-600' : ''"
                  :title="i.exchangeSubAccountDisplay"
                >
                  {{ i.exchangeSubAccountDisplay }}
                </div>
              </td>
              <td class="min-w-0 px-3 py-2 align-middle">
                <span
                  class="inline-flex max-w-full truncate rounded border px-2 py-0.5 text-xs font-medium"
                  :class="agentStateTagClass(i.agentState)"
                  :title="zhAgentState(i.agentState)"
                >
                  {{ zhAgentState(i.agentState) }}
                </span>
              </td>
              <td class="min-w-0 px-3 py-2 align-middle">
                <span
                  class="inline-flex max-w-full truncate rounded border px-2 py-0.5 text-xs font-medium"
                  :class="runtimeStateTagClass(i.runtimeState)"
                  :title="zhRuntimeState(i.runtimeState)"
                >
                  {{ zhRuntimeState(i.runtimeState) }}
                </span>
              </td>
              <td class="min-w-0 px-3 py-2 align-middle whitespace-nowrap">
                <div class="truncate text-xs text-slate-500" :title="i.lastProductBlockReason || undefined">
                  {{ i.lastProductBlockReason || '—' }}
                </div>
              </td>
              <td
                class="min-w-0 truncate px-3 py-2 align-middle text-xs whitespace-nowrap text-slate-400"
                :title="zhSubAccountStatus(i.subAccountStatus)"
              >
                {{ zhSubAccountStatus(i.subAccountStatus) }}
              </td>
              <td class="whitespace-nowrap px-3 py-2 align-middle font-mono text-xs tabular-nums text-slate-500">
                {{ formatInstanceAt(i.lastActiveAt) }}
              </td>
              <td class="whitespace-nowrap px-3 py-2 align-middle font-mono text-xs tabular-nums text-slate-500">
                {{ formatInstanceAt(i.createdAt) }}
              </td>
              <td
                class="sticky right-0 z-[1] min-w-[20rem] whitespace-nowrap border-l border-slate-800 bg-slate-950/80 px-3 py-2 text-right align-middle backdrop-blur-sm group-hover:bg-slate-900/60"
                @click.stop
              >
                <div class="flex flex-nowrap items-center justify-end gap-1.5">
                  <UiTableAction variant="sky" icon="eye" @click="openPreview(i)">预览</UiTableAction>
                  <UiTableAction
                    variant="sky"
                    icon="file-text"
                    :to="{ name: 'agents.instance-detail', params: { instanceId: i.instanceId } }"
                  >
                    详情
                  </UiTableAction>
                  <UiTableAction
                    variant="emerald"
                    icon="search"
                    :to="`/observability${buildObservabilitySearch({ userId: i.userId, tab: 'execution' })}`"
                  >
                    协查
                  </UiTableAction>
                  <UiTableAction variant="rose" icon="trash" @click="openInstDelete(i)">删除</UiTableAction>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- 实例预览侧栏（对齐原型 Drawer） -->
    <Teleport to="body">
      <Transition name="admin-drawer-scrim">
        <button
          v-if="previewVm"
          type="button"
          class="fixed inset-0 z-[80] bg-slate-950/60"
          aria-label="关闭预览"
          @click="closePreview"
        />
      </Transition>
      <Transition name="admin-drawer-panel">
        <aside
          v-if="previewVm"
          class="fixed inset-y-0 right-0 z-[90] flex w-full max-w-md flex-col border-l border-slate-700 bg-slate-900 shadow-xl"
          role="dialog"
          aria-modal="true"
          aria-labelledby="instance-preview-title"
        >
          <div class="flex items-start justify-between gap-2 border-b border-slate-800 p-4">
            <h2 id="instance-preview-title" class="text-base font-semibold text-white">实例预览</h2>
            <RouterLink
              class="shrink-0 rounded-md bg-emerald-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-emerald-500"
              :to="{ name: 'agents.instance-detail', params: { instanceId: previewVm.instanceId } }"
              @click="closePreview"
            >
              进入详情 →
            </RouterLink>
          </div>
          <div class="flex-1 overflow-y-auto p-4 text-sm">
            <div class="rounded-lg border border-slate-700 bg-slate-950/60 p-3">
              <p class="mb-1 text-xs text-slate-500">实例 · 模板</p>
              <code class="break-all text-xs text-slate-200">{{ previewVm.instanceId }}</code>
              <div class="mt-2">
                <span class="font-medium text-white">{{ previewVm.templateDisplayName }}</span>
                <span class="text-slate-500"> v{{ previewVm.templateVersion }}</span>
              </div>
              <div class="mt-2 flex flex-wrap gap-2">
                <span
                  class="inline-flex rounded border px-2 py-0.5 text-xs font-medium"
                  :class="agentStateTagClass(previewVm.agentState)"
                >
                  {{ zhAgentState(previewVm.agentState) }}
                </span>
                <span
                  class="inline-flex rounded border px-2 py-0.5 text-xs font-medium"
                  :class="runtimeStateTagClass(previewVm.runtimeState)"
                >
                  {{ zhRuntimeState(previewVm.runtimeState) }}
                </span>
              </div>
            </div>

            <div class="mt-4 space-y-4">
              <div>
                <p class="text-xs font-medium text-slate-400">TG 账号</p>
                <p class="mt-1 font-mono font-medium text-white">{{ previewVm.userId }}</p>
                <p class="text-xs text-slate-500">{{ previewVm.userEmailMasked }}</p>
                <p v-if="previewVm.raw.userId?.trim()" class="mt-1 text-[11px] text-slate-600">
                  主站 UID · {{ previewVm.raw.userId }}
                </p>
              </div>
              <div>
                <p class="text-xs font-medium text-slate-400">交易所子账号</p>
                <p class="font-mono text-sm text-slate-300">{{ previewVm.exchangeSubAccountDisplay }}</p>
              </div>
              <div>
                <p class="text-xs text-slate-500">子账户状态</p>
                <p class="text-slate-300">{{ zhSubAccountStatus(previewVm.subAccountStatus) }}</p>
              </div>
              <div>
                <p class="text-xs text-slate-500">阻断原因</p>
                <p class="text-slate-300">{{ previewVm.lastProductBlockReason || '—' }}</p>
              </div>
              <div>
                <p class="text-xs text-slate-500">最近活跃 · 创建</p>
                <p class="text-slate-400">
                  {{ formatInstanceAt(previewVm.lastActiveAt) }} ·
                  {{ formatInstanceAt(previewVm.createdAt) }}
                </p>
              </div>
              <RouterLink
                class="flex w-full justify-center rounded-md bg-emerald-600 px-3 py-2 text-center text-sm font-medium text-white hover:bg-emerald-500"
                :to="observabilityHref"
                @click="closePreview"
              >
                执行链路协查
              </RouterLink>
              <RouterLink
                class="flex w-full justify-center rounded-md border border-slate-600 bg-slate-800 px-3 py-2 text-center text-sm font-medium text-slate-200 hover:bg-slate-700"
                to="/runtime/executions"
                @click="closePreview"
              >
                执行记录
              </RouterLink>
            </div>
          </div>
        </aside>
      </Transition>
    </Teleport>

    <UiModal
      v-model:open="createOpen"
      title="创建 Agent 实例"
      :show-default-close="false"
      description="I02 · telegramUserId 必填；API 密钥仍由 Deeplink 绑定。"
    >
      <div class="space-y-3">
        <UiInput
          v-model="createTelegramUserId"
          label="telegramUserId"
          placeholder="Telegram 用户 id（数值串）"
          autocomplete="off"
        />
        <UiInput
          v-model="createTemplateId"
          label="templateId（可选）"
          placeholder="如 tmpl_test"
          autocomplete="off"
        />
        <UiInput
          v-model="createTemplateVersion"
          label="templateVersion（可选）"
          placeholder="如 1"
          autocomplete="off"
        />
        <UiInput
          v-model="createExchangeSubAccountUserId"
          label="exchangeSubAccountUserId（可选）"
          placeholder="子账户标识"
          autocomplete="off"
        />
        <p v-if="createError" class="text-sm text-rose-300" role="alert">{{ createError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="createSubmitting" @click="cancelCreate">
          取消
        </UiButton>
        <UiButton variant="primary" type="button" :loading="createSubmitting" @click="submitCreate">
          创建
        </UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="instDeleteOpen"
      title="确认删除 Agent 实例"
      :show-default-close="false"
      description="硬删除 agent_instance（DELETE · 204）。不删除 Telegram 交易 API 绑定行；绑定 Tab 仍可能显示 BOUND。"
    >
      <div v-if="instPendingDelete" class="space-y-3">
        <p class="text-sm text-slate-300">
          即将删除
          <span class="font-mono text-white">{{ instPendingDelete.instanceId }}</span>
          <span v-if="instPendingDelete.userId" class="text-slate-500">
            · TG {{ instPendingDelete.userId }}
          </span>
        </p>
        <p v-if="instDeleteError" class="text-sm text-rose-300">{{ instDeleteError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="instDeleting" @click="cancelInstDelete">
          取消
        </UiButton>
        <UiButton variant="danger" type="button" :loading="instDeleting" @click="confirmedInstDelete">
          确认删除
        </UiButton>
      </template>
    </UiModal>

    <UiModal :open="batchModalOpen" title="批量 Runtime 结果" @update:open="setBatchModalOpen">
      <div v-if="batchOutcome" class="space-y-3 text-sm text-slate-300">
        <p>
          成功 <span class="font-semibold text-emerald-400">{{ batchOutcome.succeeded?.length ?? 0 }}</span>
          · 失败
          <span class="font-semibold text-rose-400">{{ batchOutcome.failures?.length ?? 0 }}</span>
        </p>
        <pre
          class="max-h-[min(50vh,420px)] overflow-auto rounded border border-slate-700 bg-slate-950 p-3 text-xs text-slate-200"
          >{{ JSON.stringify(batchOutcome, null, 2) }}</pre
        >
      </div>
    </UiModal>
  </AdminPage>
</template>

<style scoped>
/* 与执行记录列表一致：colgroup + table-fixed，横滑时左侧勾选/实例 ID、右侧操作 sticky */
.admin-agent-inst-grid {
  table-layout: fixed;
}

/* 有可横向滚动容器时默认单行不换行（loading/占位行用 whitespace-normal） */
.admin-agent-inst-grid thead th {
  vertical-align: bottom;
  white-space: nowrap;
}

.admin-agent-inst-grid tbody td {
  vertical-align: middle;
  white-space: nowrap;
}

.admin-agent-inst-grid col.inst-col-check {
  width: 3.5rem;
}

.admin-agent-inst-grid col.inst-col-id {
  width: 15%;
}

.admin-agent-inst-grid col.inst-col-tg {
  width: 19%;
  min-width: 17.5rem;
}

.admin-agent-inst-grid col.inst-col-exchange {
  width: 12%;
}

.admin-agent-inst-grid col.inst-col-gate {
  width: 8%;
}

.admin-agent-inst-grid col.inst-col-runtime {
  width: 8%;
}

.admin-agent-inst-grid col.inst-col-block {
  width: 11%;
}

.admin-agent-inst-grid col.inst-col-sub {
  width: 8%;
  min-width: 6.75rem;
}

.admin-agent-inst-grid col.inst-col-last {
  width: 13rem;
  min-width: 13rem;
}

.admin-agent-inst-grid col.inst-col-created {
  width: 13rem;
  min-width: 13rem;
}

.admin-agent-inst-grid col.inst-col-ops {
  width: 20rem;
  min-width: 20rem;
}
</style>
