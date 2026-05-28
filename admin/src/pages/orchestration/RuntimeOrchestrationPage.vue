<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 页头改用 **`AdminPageHeader`**
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 筛选工具条命中统计改用 **`UiStatChip`**，与重置按钮行高对齐
作者: 杨永的Agent
日期: 2026-05-20
修改功能: **`flowSummary`** 列表优先 · 详情 **`GET …/scenarios/{id}`** + **executionSteps** 步骤条（FE_HANDOFF Phase2）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 场景目录表空态 **`UiTableEmptyRow`**；无数据时取消表格横向滚动
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **场景目录表 · 操作** 改用 **`UiTableAction`**；sticky **操作** 列 **`min-width`** 加宽
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **GET /api/v1/agent/scenarios** 驱动场景目录（含 orchestrationRegistryVersion / title / category / riskLevel）；筛选与详情对齐 product-doc 原型；执行策略 Tab 拆组件（FE_HANDOFF 2026-05-15）
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 运行场景页 IA（场景目录 / 执行策略 Tab、scenarioId 筛选）
-->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import {
  ORCHESTRATION_VERSION_DISPLAY,
  ROUTE_PHASE1_SCENARIOS,
  opsRuntimeStatusLabel,
  type ClosureStatus,
  type ScenarioRegistryEntry,
} from '@/entities/orchestration/scenario-registry'
import {
  getAgentScenarioDetail,
  getAgentScenarios,
  type AgentExecutionFlowStep,
  type AgentScenarioDetail,
  type AgentScenarioListItem,
  type AgentScenariosResponse,
} from '@/shared/api/agent-runtime'
import { AppError } from '@/shared/api/errors'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import AdminPage from '@/shared/ui/AdminPage.vue'
import {
  ADMIN_TOOLBAR_CLUSTER_CLASS,
  AdminPageHeader,
  UiButton,
  UiInput,
  UiModal,
  UiStatChip,
  UiTableAction,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
} from '@/shared/ui'

import OrchestrationExecutionSteps from './OrchestrationExecutionSteps.vue'
import OrchestrationPolicyTab from './OrchestrationPolicyTab.vue'

type OrchTab = 'routing' | 'policy'
/** 与 product-doc ScenarioRoutingTab Segmented 对齐的聚合类型 */
type ProtoCategoryFilter = 'all' | 'read' | 'write' | 'wealth' | 'monitoring'

const SPEC_FOOTER_PATHS: string[] = [
  'domains/agent/agent-orchestration/overview.md',
  'domains/agent/agent-orchestration/routing-engine.md',
  'domains/agent/agent-orchestration/execution-lifecycle.md',
  'domains/agent/agent-orchestration/confirmation-flow.md',
  'domains/agent/agent-orchestration/retry-policy.md',
  'domains/agent/agent-orchestration/runtime-freeze.md',
]

export interface OrchestrationRow {
  scenarioId: string
  displayTitle: string
  subtitle: string
  flowSummary: string
  riskLevel: 'low' | 'medium' | 'high'
  closureStatus: ClosureStatus
  /** 后端原始 category，用于筛选 */
  categoryApi: string
}

const route = useRoute()
const router = useRouter()

const tab = computed<OrchTab>(() => {
  const t = route.query.tab as string | undefined
  return t === 'policy' ? 'policy' : 'routing'
})

const scenarioQ = ref('')

const protoCategory = ref<ProtoCategoryFilter>('all')

const apiPayload = ref<AgentScenariosResponse | null>(null)
const apiLoading = ref(false)
const apiError = ref<string | null>(null)

const detailOpen = ref(false)
const detailRow = ref<OrchestrationRow | null>(null)
const detailApi = ref<AgentScenarioDetail | null>(null)
const detailLoading = ref(false)
const detailError = ref<string | null>(null)

const registryVersionDisplay = computed(
  () => apiPayload.value?.orchestrationRegistryVersion?.trim() || ORCHESTRATION_VERSION_DISPLAY,
)

function readinessToClosure(r: AgentScenarioListItem['readiness']): ClosureStatus {
  if (r === 'ready') return 'FROZEN'
  return 'TBD'
}

function normalizeClosureStatus(
  raw: string | null | undefined,
  readiness: AgentScenarioListItem['readiness'],
): ClosureStatus {
  const x = (raw || '').toUpperCase()
  if (x === 'FROZEN' || x === 'TBD' || x === 'PLACEHOLDER') return x
  return readinessToClosure(readiness)
}

function flowSummaryFromItem(it: AgentScenarioListItem): string {
  const fs = it.flowSummary?.trim()
  if (fs) return fs
  return it.summary?.trim() || it.scenarioId
}

function normalizeRisk(raw: string | null | undefined): 'low' | 'medium' | 'high' {
  const x = (raw || '').toLowerCase()
  if (x === 'high' || x === 'medium' || x === 'low') return x
  return 'low'
}

function rowsFromApi(items: AgentScenarioListItem[]): OrchestrationRow[] {
  return items.map((it) => ({
    scenarioId: it.scenarioId,
    displayTitle: (it.title && it.title.trim()) || it.scenarioId,
    subtitle: it.scenarioId,
    flowSummary: flowSummaryFromItem(it),
    riskLevel: normalizeRisk(it.riskLevel),
    closureStatus: normalizeClosureStatus(it.closureStatus, it.readiness),
    categoryApi: (it.category || 'read').toLowerCase(),
  }))
}

function rowsFromStatic(entries: ScenarioRegistryEntry[]): OrchestrationRow[] {
  return entries.map((s) => ({
    scenarioId: s.scenarioId,
    displayTitle: s.scenarioTitle,
    subtitle: s.scenarioId,
    flowSummary: s.flowSummary,
    riskLevel: s.riskLevel,
    closureStatus: s.closureStatus,
    categoryApi: s.category,
  }))
}

const baseRows = computed((): OrchestrationRow[] => {
  if (apiPayload.value?.scenarios?.length) return rowsFromApi(apiPayload.value.scenarios)
  return rowsFromStatic(ROUTE_PHASE1_SCENARIOS)
})

function matchesProtoCategory(row: OrchestrationRow, f: ProtoCategoryFilter): boolean {
  const c = row.categoryApi
  if (f === 'all') return true
  if (f === 'read') return c === 'read'
  if (f === 'write') return c === 'trade' || c === 'margin'
  if (f === 'wealth') return c === 'wealth'
  if (f === 'monitoring') return c === 'automation' || c === 'chat'
  return true
}

const filteredRows = computed(() => {
  let rows = baseRows.value.filter((r) => matchesProtoCategory(r, protoCategory.value))
  const q = scenarioQ.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(
      (r) =>
        r.scenarioId.toLowerCase().includes(q) ||
        r.displayTitle.toLowerCase().includes(q) ||
        r.flowSummary.toLowerCase().includes(q) ||
        r.subtitle.toLowerCase().includes(q),
    )
  }
  return rows
})

const scenarioTableScrollX = computed(() => !apiLoading.value && filteredRows.value.length > 0)

const CATEGORY_SEGMENTS: { key: ProtoCategoryFilter; label: string }[] = [
  { key: 'all', label: '全部' },
  { key: 'read', label: '读侧与分析' },
  { key: 'write', label: '交易与委托' },
  { key: 'wealth', label: '理财' },
  { key: 'monitoring', label: '监控与自动化' },
]

function categoryTagLabel(cat: string): string {
  switch (cat) {
    case 'read':
      return '读侧与分析'
    case 'trade':
    case 'margin':
      return '交易与委托'
    case 'wealth':
      return '理财'
    case 'automation':
    case 'chat':
      return '监控与自动化'
    default:
      return cat || '—'
  }
}

function categoryTagClass(cat: string): string {
  if (cat === 'read') return 'border-sky-500/35 bg-sky-500/10 text-sky-200'
  if (cat === 'trade' || cat === 'margin') return 'border-rose-500/30 bg-rose-500/10 text-rose-200'
  if (cat === 'wealth') return 'border-amber-500/35 bg-amber-500/12 text-amber-200'
  return 'border-teal-500/30 bg-teal-500/10 text-teal-200'
}

function riskLabel(level: string): string {
  if (level === 'high') return '高'
  if (level === 'medium') return '中'
  return '低'
}

function riskClass(r: string): string {
  if (r === 'high') return 'border-rose-500/35 bg-rose-500/10 text-rose-200'
  if (r === 'medium') return 'border-amber-500/35 bg-amber-500/12 text-amber-200'
  return 'border-sky-500/35 bg-sky-500/10 text-sky-200'
}

function badgeClass(s: ClosureStatus): string {
  if (s === 'FROZEN') return 'border-emerald-500/35 bg-emerald-500/10 text-emerald-200'
  if (s === 'TBD') return 'border-amber-500/35 bg-amber-500/12 text-amber-200'
  return 'border-slate-600 bg-slate-800/80 text-slate-400'
}

function setTab(next: OrchTab) {
  const query = { ...route.query } as Record<string, string | undefined>
  if (next === 'routing') delete query.tab
  else query.tab = next
  void router.replace({ path: route.path, query })
}

function clearFilters() {
  protoCategory.value = 'all'
  scenarioQ.value = ''
  const query = { ...route.query } as Record<string, string | undefined>
  delete query.scenario
  void router.replace({ path: route.path, query })
}

async function loadScenarios(toastOnSuccess = false) {
  apiLoading.value = true
  apiError.value = null
  try {
    apiPayload.value = await getAgentScenarios()
    if (toastOnSuccess) adminToastSuccess('已刷新')
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '加载场景目录失败'
    apiError.value = msg
    apiPayload.value = null
    if (toastOnSuccess) adminToastError(msg)
  } finally {
    apiLoading.value = false
  }
}

const detailExecutionSteps = computed((): AgentExecutionFlowStep[] => {
  if (detailApi.value?.executionSteps?.length) return detailApi.value.executionSteps
  const fromList = apiPayload.value?.scenarios?.find((s) => s.scenarioId === detailRow.value?.scenarioId)
  return fromList?.executionSteps ?? []
})

const detailFlowSummary = computed(() => {
  const api = detailApi.value
  if (api?.flowSummary?.trim()) return api.flowSummary.trim()
  return detailRow.value?.flowSummary ?? '—'
})

async function loadScenarioDetail(scenarioId: string) {
  detailLoading.value = true
  detailError.value = null
  detailApi.value = null
  try {
    detailApi.value = await getAgentScenarioDetail(scenarioId)
  } catch (e) {
    detailError.value = e instanceof AppError ? e.message : '加载场景详情失败'
  } finally {
    detailLoading.value = false
  }
}

function openDetail(row: OrchestrationRow) {
  detailRow.value = row
  detailOpen.value = true
  void loadScenarioDetail(row.scenarioId)
}

function goPolicyFromDetail() {
  setDetailModalOpen(false)
  setTab('policy')
}

function setDetailModalOpen(v: boolean) {
  detailOpen.value = v
  if (!v) {
    detailRow.value = null
    detailApi.value = null
    detailError.value = null
    detailLoading.value = false
  }
}

function executionsHref(scenarioId: string): string {
  return `/runtime/executions?scenario=${encodeURIComponent(scenarioId)}`
}

watch(
  () => route.query.scenario,
  (s) => {
    scenarioQ.value = typeof s === 'string' ? s : ''
  },
  { immediate: true },
)

onMounted(() => {
  void loadScenarios()
})
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="运行场景"
      :badges="[{ label: 'AI 治理', tone: 'sky' }]"
      description="按业务类型浏览智能体运行场景；执行边界在「执行策略」。内部标识与规格路径见场景详情。"
    >
      <template #dev>
        <code class="text-slate-500">ai.runtime-orchestration</code>
        · 寄存器
        <span class="font-mono text-slate-500">{{ registryVersionDisplay }}</span>
      </template>
      <template #actions>
        <UiButton type="button" variant="secondary" size="sm" :loading="apiLoading" @click="loadScenarios(true)">
          刷新
        </UiButton>
      </template>
    </AdminPageHeader>

    <div class="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
      <button
        type="button"
        class="admin-seg"
        :class="
          tab === 'routing'
            ? 'admin-seg-active'
            : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
        "
        @click="setTab('routing')"
      >
        场景目录
      </button>
      <button
        type="button"
        class="admin-seg"
        :class="
          tab === 'policy'
            ? 'admin-seg-active'
            : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
        "
        @click="setTab('policy')"
      >
        执行策略
      </button>
    </div>

    <section v-show="tab === 'routing'" class="space-y-4">
      <div class="admin-panel p-4 sm:p-5">
        <div class="flex flex-wrap items-start justify-between gap-3 border-b border-slate-800 pb-3">
          <div>
            <p class="text-[13px] font-semibold text-white">筛选条件</p>
            <p class="mt-0.5 text-xs text-slate-500">类型与关键词；重置将清空地址栏 scenario 参数。</p>
          </div>
          <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
            <UiStatChip tone="success">
              命中 {{ filteredRows.length }} / {{ baseRows.length }}
            </UiStatChip>
            <UiButton type="button" variant="secondary" size="sm" @click="clearFilters">重置</UiButton>
          </div>
        </div>

        <div class="mt-4 flex flex-wrap gap-2">
          <button
            v-for="seg in CATEGORY_SEGMENTS"
            :key="seg.key"
            type="button"
            class="admin-seg text-xs sm:text-sm"
            :class="
              protoCategory === seg.key
                ? 'admin-seg-active'
                : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
            "
            @click="protoCategory = seg.key"
          >
            {{ seg.label }}
          </button>
        </div>

        <div class="mt-4 max-w-2xl">
          <UiInput
            v-model="scenarioQ"
            type="search"
            label="关键字"
            placeholder="场景名称、流程摘要、scenarioId…"
          />
        </div>
      </div>

      <p v-if="apiError" class="text-sm text-amber-300" role="alert">{{ apiError }}（已回退静态寄存器快照）</p>

      <div
        class="rounded-lg border border-slate-800"
        :class="adminTableHostOverflowClass(scenarioTableScrollX)"
      >
        <table
          class="w-full text-left text-sm"
          :class="scenarioTableScrollX ? 'min-w-[1040px]' : ''"
        >
          <thead class="border-b border-slate-800 bg-slate-900/80 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="sticky left-0 z-10 min-w-[200px] bg-slate-900/95 px-4 py-2 font-medium backdrop-blur-sm">
                场景名称
              </th>
              <th class="px-4 py-2 font-medium">类型</th>
              <th class="min-w-[280px] px-4 py-2 font-medium">执行流程</th>
              <th class="px-4 py-2 font-medium">风险等级</th>
              <th class="px-4 py-2 font-medium">状态</th>
              <th class="sticky right-0 z-10 min-w-[208px] bg-slate-900/95 px-4 py-2 text-right font-medium backdrop-blur-sm">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800 text-slate-200">
            <UiTableEmptyRow
              v-if="apiLoading && baseRows.length === 0"
              :colspan="6"
              state="loading"
            />
            <UiTableEmptyRow
              v-else-if="filteredRows.length === 0"
              :colspan="6"
              state="filtered"
              title="无匹配场景"
              description="请调整筛选或关键字。"
            />
            <tr v-for="row in filteredRows" :key="row.scenarioId" class="hover:bg-slate-900/40">
              <td class="sticky left-0 z-[1] bg-slate-950/90 px-4 py-3 backdrop-blur-sm">
                <div class="font-medium text-white">{{ row.displayTitle }}</div>
                <div class="mt-0.5 font-mono text-[11px] text-slate-500">{{ row.subtitle }}</div>
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                  :class="categoryTagClass(row.categoryApi)"
                >
                  {{ categoryTagLabel(row.categoryApi) }}
                </span>
              </td>
              <td class="max-w-md px-4 py-3 text-slate-400">{{ row.flowSummary }}</td>
              <td class="px-4 py-3">
                <span
                  class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                  :class="riskClass(row.riskLevel)"
                >
                  {{ riskLabel(row.riskLevel) }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span class="rounded border px-2 py-0.5 text-[11px] font-medium" :class="badgeClass(row.closureStatus)">
                  {{ opsRuntimeStatusLabel(row.closureStatus) }}
                </span>
              </td>
              <td class="sticky right-0 z-[1] min-w-[208px] whitespace-nowrap bg-slate-950/90 px-4 py-3 text-right backdrop-blur-sm">
                <div class="flex flex-wrap items-center justify-end gap-1.5">
                  <UiTableAction variant="sky" icon="list" :to="executionsHref(row.scenarioId)">
                    最近执行
                  </UiTableAction>
                  <UiTableAction variant="emerald" icon="file-text" @click="openDetail(row)">
                    详情
                  </UiTableAction>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <footer class="rounded-lg border border-slate-800/80 bg-slate-950/30 px-4 py-3">
        <p class="text-[11px] font-medium uppercase tracking-wide text-slate-500">规格互引（product-doc）</p>
        <ul class="mt-2 space-y-1 font-mono text-[11px] text-slate-500">
          <li v-for="p in SPEC_FOOTER_PATHS" :key="p">{{ p }}</li>
        </ul>
      </footer>
    </section>

    <section v-show="tab === 'policy'">
      <OrchestrationPolicyTab />
    </section>

    <UiModal :open="detailOpen" :title="detailRow?.displayTitle ?? '场景详情'" @update:open="setDetailModalOpen">
      <div v-if="detailRow" class="space-y-4 text-sm text-slate-300">
        <div>
          <p class="text-xs font-medium text-slate-500">类型</p>
          <span
            class="mt-1 inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
            :class="categoryTagClass(detailRow.categoryApi)"
          >
            {{ categoryTagLabel(detailRow.categoryApi) }}
          </span>
        </div>
        <div>
          <p class="text-xs font-medium text-slate-500">执行流程</p>
          <p class="mt-1 leading-relaxed">{{ detailFlowSummary }}</p>
        </div>
        <div>
          <p class="text-xs font-medium text-slate-500">编排步骤</p>
          <p v-if="detailError" class="mt-1 text-xs text-amber-300" role="alert">{{ detailError }}</p>
          <OrchestrationExecutionSteps
            class="mt-1"
            :steps="detailExecutionSteps"
            :loading="detailLoading"
          />
        </div>
        <div v-if="detailApi?.flowAnchor?.trim()">
          <p class="text-xs font-medium text-slate-500">流程锚点</p>
          <p class="mt-1 break-words font-mono text-xs text-slate-400">{{ detailApi.flowAnchor }}</p>
        </div>
        <div v-if="detailApi?.promptBindingHint?.trim()">
          <p class="text-xs font-medium text-slate-500">Prompt 绑定</p>
          <p class="mt-1 text-xs leading-relaxed text-slate-400">{{ detailApi.promptBindingHint }}</p>
        </div>
        <div v-if="detailApi?.specRefs?.length">
          <p class="text-xs font-medium text-slate-500">规格互引</p>
          <ul class="mt-2 list-inside list-disc space-y-1 text-xs text-slate-400">
            <li v-for="p in detailApi.specRefs" :key="p">
              <code class="rounded bg-slate-900 px-1 py-0.5 font-mono text-[11px] text-slate-300">{{ p }}</code>
            </li>
          </ul>
        </div>
        <div>
          <p class="text-xs font-medium text-slate-500">风险等级</p>
          <span
            class="mt-1 inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
            :class="riskClass(normalizeRisk(detailApi?.riskLevel ?? detailRow.riskLevel))"
          >
            {{ riskLabel(normalizeRisk(detailApi?.riskLevel ?? detailRow.riskLevel)) }}
          </span>
        </div>
        <div>
          <p class="text-xs font-medium text-slate-500">运行状态</p>
          <span
            class="mt-1 inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
            :class="
              badgeClass(
                detailApi
                  ? normalizeClosureStatus(detailApi.closureStatus, detailApi.readiness)
                  : detailRow.closureStatus,
              )
            "
          >
            {{
              opsRuntimeStatusLabel(
                detailApi
                  ? normalizeClosureStatus(detailApi.closureStatus, detailApi.readiness)
                  : detailRow.closureStatus,
              )
            }}
          </span>
        </div>
        <div>
          <p class="text-xs font-medium text-slate-500">scenarioId</p>
          <code class="mt-1 block break-all rounded bg-slate-900 px-2 py-1.5 font-mono text-xs text-emerald-300/90">
            {{ detailRow.scenarioId }}
          </code>
        </div>
        <div>
          <p class="text-xs font-medium text-slate-500">orchestrationRegistryVersion</p>
          <code class="mt-1 block font-mono text-xs text-slate-400">{{ registryVersionDisplay }}</code>
        </div>
        <div class="flex flex-wrap gap-3 pt-2">
          <RouterLink
            class="text-xs font-medium text-sky-400 hover:text-sky-300"
            :to="executionsHref(detailRow.scenarioId)"
          >
            最近执行
          </RouterLink>
          <button
            type="button"
            class="text-xs font-medium text-emerald-400 hover:text-emerald-300"
            @click="goPolicyFromDetail"
          >
            执行策略
          </button>
        </div>
      </div>
    </UiModal>
  </AdminPage>
</template>
