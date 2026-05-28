<!--
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 页面结构对齐 5176 原型（ProductPageShell 页眉 · 线型 Tab · admin-panel 分区）
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 任务队列 / 运行事件 / Retries / Recovery Tab 接 observability API（FE_HANDOFF 2026-05-27）
作者: 杨永的Agent
日期: 2026-05-18
修改功能: 总览 **治理四折叠块**（`ExecutionDetailGovernanceSection` · skill-scope / 拼装追溯 · FE_HANDOFF 2026-05-26）
-->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import ObservabilityExecutionTimelinePanel from '@/features/observability/ObservabilityExecutionTimelinePanel.vue'
import ExecutionDetailGovernanceSection from '@/features/runtime/ExecutionDetailGovernanceSection.vue'
import ExecutionDetailObservabilityTabs from '@/features/runtime/ExecutionDetailObservabilityTabs.vue'
import { EXECUTION_DETAIL_COPY } from '@/shared/copy/execution-detail-copy'
import { AppError } from '@/shared/api/errors'
import {
  deleteAdminObservabilityExecution,
  getAdminObservabilityExecution,
  getAdminObservabilityExecutionEvents,
  getAdminObservabilityExecutionQueue,
  getAdminObservabilityExecutionRetries,
  type AdminAgentExecutionItem,
} from '@/shared/api/admin-observability'
import {
  observabilityExecutionHref,
  scenarioDisplayTitle,
} from '@/shared/lib/execution-detail-display'
import { formatPromptPackVersionLabel, summarizeTradingPromptBinding } from '@/shared/lib/execution-prompt-meta'
import { adminTimeZoneParenSuffix } from '@/shared/lib/admin-datetime-display'
import { formatIsoTime, zhExecutionRuntimeStatus } from '@/shared/copy/zh-runtime'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminDetailTabs from '@/shared/ui/AdminDetailTabs.vue'
import type { AdminDetailTabItem } from '@/shared/ui/AdminDetailTabs.vue'
import AdminPageHeader from '@/shared/ui/AdminPageHeader.vue'
import { UiButton, UiModal } from '@/shared/ui'

const DETAIL_TABS = ['overview', 'timeline', 'queue', 'events', 'retries', 'recovery'] as const
type DetailTab = (typeof DETAIL_TABS)[number]

function isDetailTab(s: string): s is DetailTab {
  return (DETAIL_TABS as readonly string[]).includes(s)
}

const route = useRoute()
const router = useRouter()

const detail = ref<AdminAgentExecutionItem | null>(null)
const loading = ref(true)
const notFound = ref(false)
const loadError = ref<string | null>(null)

const deleteOpen = ref(false)
const deleteSubmitting = ref(false)
const deleteError = ref<string | null>(null)

const tabCounts = ref({ queue: 0, events: 0, retries: 0 })
const countsReady = ref(false)

const executionId = computed(() => route.params.executionId as string)
const activeTab = computed<DetailTab>(() => {
  const raw = route.query.tab
  const s = typeof raw === 'string' ? raw : 'overview'
  return isDetailTab(s) ? s : 'overview'
})

const pageTitle = computed(() => scenarioDisplayTitle(detail.value?.scenarioId))
const overviewTimeParen = computed(() => adminTimeZoneParenSuffix())
const obsHref = computed(() => observabilityExecutionHref(executionId.value))

const OBSERVABILITY_SUB_TABS = new Set<DetailTab>(['queue', 'events', 'retries', 'recovery'])
const isObservabilitySubTab = computed(() => OBSERVABILITY_SUB_TABS.has(activeTab.value))

const observabilitySubTab = computed((): 'queue' | 'events' | 'retries' | 'recovery' => {
  const t = activeTab.value
  if (t === 'queue' || t === 'events' || t === 'retries' || t === 'recovery') return t
  return 'queue'
})

const detailTabItems = computed<AdminDetailTabItem[]>(() => {
  const c = tabCounts.value
  const qLabel =
    countsReady.value && c.queue > 0
      ? `${EXECUTION_DETAIL_COPY.tabQueue}（${c.queue}）`
      : EXECUTION_DETAIL_COPY.tabQueue
  const eLabel =
    countsReady.value && c.events > 0
      ? `${EXECUTION_DETAIL_COPY.tabEvents}（${c.events}）`
      : EXECUTION_DETAIL_COPY.tabEvents
  const rLabel =
    countsReady.value && c.retries > 0
      ? `${EXECUTION_DETAIL_COPY.tabRetries}（${c.retries}）`
      : EXECUTION_DETAIL_COPY.tabRetries
  return [
    { key: 'overview', label: EXECUTION_DETAIL_COPY.tabOverview },
    { key: 'timeline', label: EXECUTION_DETAIL_COPY.tabTimeline },
    { key: 'queue', label: qLabel },
    { key: 'events', label: eLabel },
    { key: 'retries', label: rLabel },
    { key: 'recovery', label: EXECUTION_DETAIL_COPY.tabRecovery },
  ]
})

const summaryRowDt = 'w-32 shrink-0 py-2.5 text-xs font-medium text-slate-500 sm:w-36'
const summaryRowDd = 'min-w-0 flex-1 py-2.5 text-sm text-slate-200'

async function prefetchTabCounts(id: string) {
  countsReady.value = false
  try {
    const [q, e, r] = await Promise.all([
      getAdminObservabilityExecutionQueue(id),
      getAdminObservabilityExecutionEvents(id),
      getAdminObservabilityExecutionRetries(id),
    ])
    tabCounts.value = {
      queue: q.items?.length ?? 0,
      events: e.items?.length ?? 0,
      retries: r.retryCount ?? r.items?.length ?? 0,
    }
  } catch {
    tabCounts.value = { queue: 0, events: 0, retries: 0 }
  } finally {
    countsReady.value = true
  }
}

async function load() {
  loading.value = true
  notFound.value = false
  loadError.value = null
  detail.value = null
  countsReady.value = false
  try {
    const row = await getAdminObservabilityExecution(executionId.value)
    detail.value = row
    void prefetchTabCounts(row.executionId)
  } catch (e) {
    if (e instanceof AppError && e.status === 404) {
      notFound.value = true
    } else {
      loadError.value = e instanceof AppError ? e.message : '加载失败'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void load()
})

watch(executionId, () => {
  void load()
})

function setTab(key: string) {
  if (!isDetailTab(key)) return
  const q = { ...route.query }
  if (key === 'overview') delete q.tab
  else q.tab = key
  void router.replace({ query: q })
}

function onTabCounts(payload: { queue: number; events: number; retries: number }) {
  tabCounts.value = payload
  countsReady.value = true
}

function statusTagClass(status: string): string {
  if (status === 'SUCCEEDED') return 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30'
  if (status === 'ACCEPTED') return 'bg-sky-500/15 text-sky-300 ring-sky-500/30'
  if (status === 'CANCELLED') return 'bg-slate-500/15 text-slate-300 ring-slate-500/30'
  if (status === 'FAILED') return 'bg-rose-500/15 text-rose-300 ring-rose-500/30'
  return 'bg-slate-500/15 text-slate-300 ring-slate-500/30'
}

function outcomeHintClass(state: string): string {
  if (state === 'FAILED') return 'bg-rose-500/12 text-rose-200/90 ring-rose-500/25'
  if (state === 'SUCCEEDED') return 'bg-emerald-500/12 text-emerald-200/90 ring-emerald-500/25'
  if (state === 'ACCEPTED') return 'bg-sky-500/12 text-sky-200/90 ring-sky-500/25'
  return 'bg-slate-500/12 text-slate-300 ring-slate-600/40'
}

function outcomeHintLabel(state: string): string {
  if (state === 'FAILED') return '失败'
  if (state === 'SUCCEEDED') return '已落地'
  if (state === 'ACCEPTED') return '进行中'
  if (state === 'CANCELLED') return '已取消'
  return zhExecutionRuntimeStatus(state)
}

function openDeleteConfirm() {
  deleteError.value = null
  deleteOpen.value = true
}

function cancelDelete() {
  deleteOpen.value = false
  deleteError.value = null
}

async function confirmedDelete() {
  const id = executionId.value.trim()
  if (!id) return
  deleteSubmitting.value = true
  deleteError.value = null
  try {
    await deleteAdminObservabilityExecution(id)
    deleteOpen.value = false
    await router.replace({ path: '/runtime/executions' })
  } catch (e) {
    deleteError.value = e instanceof AppError ? e.message : '删除失败'
  } finally {
    deleteSubmitting.value = false
  }
}

function fmtResolvedBindingJson(d: AdminAgentExecutionItem): string {
  const b = d.resolvedPromptBinding
  if (b == null || typeof b !== 'object') return '{}'
  return JSON.stringify(b, null, 2)
}
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      :title="detail ? pageTitle : EXECUTION_DETAIL_COPY.pageTitle"
      title-size="editor"
      dev-meta="pageId · runtime.execution-detail"
      :crumbs="[
        { label: '执行记录', to: '/runtime/executions' },
        { label: '详情' },
      ]"
    >
      <template v-if="detail" #badges>
        <span
          class="inline-flex rounded-full px-2 py-0.5 text-xs ring-1"
          :class="statusTagClass(detail.state)"
        >
          {{ zhExecutionRuntimeStatus(detail.state) }}
        </span>
        <span
          class="inline-flex rounded-full px-2 py-0.5 text-xs ring-1"
          :class="outcomeHintClass(detail.state)"
        >
          {{ outcomeHintLabel(detail.state) }}
        </span>
      </template>
      <template v-if="detail" #actions>
        <div class="flex flex-wrap items-center gap-2">
          <UiButton type="button" variant="secondary" size="sm" disabled>
            {{ EXECUTION_DETAIL_COPY.retryAction }}
          </UiButton>
          <RouterLink
            :to="obsHref"
            class="inline-flex items-center justify-center rounded-md border border-slate-600 bg-slate-900 px-3 py-1.5 text-sm font-medium text-slate-200 transition-colors hover:border-slate-500 hover:bg-slate-800"
          >
            {{ EXECUTION_DETAIL_COPY.obsLink }}
          </RouterLink>
          <RouterLink
            to="/runtime/executions"
            class="inline-flex items-center justify-center px-2 py-1.5 text-sm font-medium text-sky-400/90 hover:text-sky-300 hover:underline"
          >
            {{ EXECUTION_DETAIL_COPY.backToList }}
          </RouterLink>
          <UiButton type="button" variant="danger" size="sm" @click="openDeleteConfirm">
            删除记录
          </UiButton>
        </div>
      </template>
    </AdminPageHeader>

    <p v-if="loading" class="text-slate-500">加载中…</p>
    <p v-else-if="loadError" class="text-rose-400">{{ loadError }}</p>
    <p v-else-if="notFound" class="text-rose-400">未找到该 execution（404 · AGENT_ADMIN_EXECUTION_NOT_FOUND）。</p>

    <template v-else-if="detail">
      <p class="text-sm text-slate-400">
        <span class="font-mono text-slate-300">{{ detail.executionId }}</span>
        <span class="text-slate-600"> · </span>
        用户 <span class="font-mono text-slate-400">{{ detail.userId }}</span>
        <span class="text-slate-600"> · </span>
        场景 <span class="font-mono text-slate-400">{{ detail.scenarioId ?? '—' }}</span>
      </p>

      <AdminDetailTabs
        class="mt-4"
        :tabs="detailTabItems"
        :active-key="activeTab"
        @update:active-key="setTab"
      />

      <div class="mt-4 space-y-4">
        <section v-show="activeTab === 'overview'" class="space-y-4">
          <section class="admin-panel overflow-hidden p-4 sm:p-5">
            <h2 class="mb-3 text-[15px] font-semibold text-white">
              {{ EXECUTION_DETAIL_COPY.summaryCardTitle }}
            </h2>
            <dl class="divide-y divide-slate-800/80">
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelExecutionId }}</dt>
                <dd :class="`${summaryRowDd} font-mono text-xs break-all`">{{ detail.executionId }}</dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelUserId }}</dt>
                <dd :class="`${summaryRowDd} font-mono`">{{ detail.userId }}</dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelScenarioId }}</dt>
                <dd :class="`${summaryRowDd} font-mono`">{{ detail.scenarioId ?? '—' }}</dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelRuntimeStatus }}</dt>
                <dd :class="summaryRowDd">{{ zhExecutionRuntimeStatus(detail.state) }}</dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelChannel }}</dt>
                <dd :class="`${summaryRowDd} font-mono text-slate-400`">{{ detail.channel ?? '—' }}</dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelSource }}</dt>
                <dd :class="`${summaryRowDd} font-mono text-xs text-slate-400`">{{ detail.source ?? '—' }}</dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelNote }}</dt>
                <dd :class="summaryRowDd">{{ detail.note ?? '—' }}</dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelPromptPackVersion }}</dt>
                <dd :class="`${summaryRowDd} font-mono text-sky-300/90`">
                  {{ formatPromptPackVersionLabel(detail.promptPackVersion) }}
                </dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">{{ EXECUTION_DETAIL_COPY.labelPromptBinding }}</dt>
                <dd :class="summaryRowDd">
                  <p class="break-all font-mono text-xs text-slate-400">
                    {{ summarizeTradingPromptBinding(detail.resolvedPromptBinding ?? null) }}
                  </p>
                  <details
                    v-if="detail.resolvedPromptBinding != null"
                    class="mt-2 rounded-md border border-slate-800 bg-slate-950/55 p-2"
                  >
                    <summary class="cursor-pointer text-xs text-slate-500">
                      resolvedPromptBinding（完整 JSON）
                    </summary>
                    <pre class="mt-2 max-h-64 overflow-auto font-mono text-[11px] text-slate-500">{{
                      fmtResolvedBindingJson(detail)
                    }}</pre>
                  </details>
                </dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">
                  {{ EXECUTION_DETAIL_COPY.labelCreatedAt
                  }}<span class="font-normal text-slate-600">{{ overviewTimeParen }}</span>
                </dt>
                <dd :class="`${summaryRowDd} font-mono text-xs text-slate-400`">
                  {{ formatIsoTime(detail.createdAt) }}
                </dd>
              </div>
              <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
                <dt :class="summaryRowDt">
                  {{ EXECUTION_DETAIL_COPY.labelUpdatedAt
                  }}<span class="font-normal text-slate-600">{{ overviewTimeParen }}</span>
                </dt>
                <dd :class="`${summaryRowDd} font-mono text-xs text-slate-400`">
                  {{ detail.updatedAt ? formatIsoTime(detail.updatedAt) : '—' }}
                </dd>
              </div>
            </dl>
          </section>

          <ExecutionDetailGovernanceSection :detail="detail" />
        </section>

        <section v-show="activeTab === 'timeline'" class="admin-panel overflow-hidden p-4 sm:p-5">
          <ObservabilityExecutionTimelinePanel
            :execution-id="executionId"
            :scenario-id="detail.scenarioId"
          />
        </section>

        <ExecutionDetailObservabilityTabs
          v-if="isObservabilitySubTab"
          :execution-id="executionId"
          :tab="observabilitySubTab"
          @tab-counts="onTabCounts"
        />
      </div>
    </template>

    <UiModal
      v-model:open="deleteOpen"
      title="确认删除执行记录"
      :show-default-close="false"
      description="硬删除 agent_execution（DELETE · 204）。删除后将返回执行列表。"
    >
      <div class="space-y-3 text-sm text-slate-300">
        <p>
          即将删除
          <span class="font-mono text-white">{{ executionId }}</span>
        </p>
        <p v-if="deleteError" class="text-rose-300">{{ deleteError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" @click="cancelDelete">取消</UiButton>
        <UiButton variant="danger" type="button" :loading="deleteSubmitting" @click="confirmedDelete">
          确认删除
        </UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>
