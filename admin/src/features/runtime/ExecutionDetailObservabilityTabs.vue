<!--
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 对齐 5176 原型 · admin-panel 卡片表 · Tab 计数回传
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 执行详情 queue / events / retries / recovery Tab（FE_HANDOFF 2026-05-27）
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

import { EXECUTION_DETAIL_COPY } from '@/shared/copy/execution-detail-copy'
import { AppError } from '@/shared/api/errors'
import {
  getAdminObservabilityExecutionEvents,
  getAdminObservabilityExecutionQueue,
  getAdminObservabilityExecutionRecovery,
  getAdminObservabilityExecutionRetries,
  type ExecutionRecoveryResponse,
  type ExecutionRetryItem,
  type ExecutionRuntimeEventItem,
  type ExecutionTaskQueueItem,
} from '@/shared/api/admin-observability'
import { observabilityExecutionHref } from '@/shared/lib/execution-detail-display'
import { adminTimeZoneParenSuffix } from '@/shared/lib/admin-datetime-display'
import { formatIsoTime, zhRuntimeEventType, zhTaskState } from '@/shared/copy/zh-runtime'

const props = defineProps<{
  executionId: string
  tab: 'queue' | 'events' | 'retries' | 'recovery'
}>()

const emit = defineEmits<{
  tabCounts: [payload: { queue: number; events: number; retries: number }]
}>()

const loading = ref(false)
const loadError = ref<string | null>(null)

const queueItems = ref<ExecutionTaskQueueItem[]>([])
const eventItems = ref<ExecutionRuntimeEventItem[]>([])
const retryItems = ref<ExecutionRetryItem[]>([])
const recovery = ref<ExecutionRecoveryResponse | null>(null)

const timeParen = computed(() => adminTimeZoneParenSuffix())

const observabilityHref = computed(() => {
  const path = recovery.value?.observabilitySearchPath?.trim()
  if (path?.startsWith('/')) return path
  return observabilityExecutionHref(props.executionId)
})

function emitCounts() {
  emit('tabCounts', {
    queue: queueItems.value.length,
    events: eventItems.value.length,
    retries: retryItems.value.length,
  })
}

function taskStateClass(state: string): string {
  const u = state.toUpperCase()
  if (u === 'RUNNING') return 'border-sky-600/45 bg-sky-950/35 text-sky-200/95'
  if (u === 'BLOCKED') return 'border-amber-600/45 bg-amber-950/35 text-amber-200/95'
  return 'border-slate-600 bg-slate-900/60 text-slate-300'
}

let loadGen = 0

async function loadTab() {
  const id = props.executionId.trim()
  if (!id) return
  const gen = ++loadGen
  loading.value = true
  loadError.value = null
  try {
    if (props.tab === 'queue') {
      const res = await getAdminObservabilityExecutionQueue(id)
      if (gen !== loadGen) return
      queueItems.value = res.items ?? []
    } else if (props.tab === 'events') {
      const res = await getAdminObservabilityExecutionEvents(id)
      if (gen !== loadGen) return
      eventItems.value = res.items ?? []
    } else if (props.tab === 'retries') {
      const res = await getAdminObservabilityExecutionRetries(id)
      if (gen !== loadGen) return
      retryItems.value = res.items ?? []
    } else {
      const res = await getAdminObservabilityExecutionRecovery(id)
      if (gen !== loadGen) return
      recovery.value = res
    }
    emitCounts()
  } catch (e) {
    if (gen !== loadGen) return
    loadError.value = e instanceof AppError ? e.message : '加载失败'
  } finally {
    if (gen === loadGen) loading.value = false
  }
}

watch(
  () => `${props.executionId}\t${props.tab}`,
  () => {
    void loadTab()
  },
  { immediate: true },
)
</script>

<template>
  <section class="admin-panel overflow-hidden text-sm">
    <div v-if="loading" class="px-4 py-10 text-center text-slate-500 sm:px-5">加载中…</div>
    <p v-else-if="loadError" class="px-4 py-6 text-rose-400/90 sm:px-5">{{ loadError }}</p>

    <template v-else-if="tab === 'queue'">
      <div
        v-if="queueItems.length === 0"
        class="px-4 py-10 text-center text-slate-500 sm:px-5"
      >
        {{ EXECUTION_DETAIL_COPY.queueEmpty }}
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-[560px] w-full border-collapse text-left text-sm">
          <thead>
            <tr class="border-b border-slate-800/90 text-xs font-medium uppercase tracking-wide text-slate-500">
              <th class="px-4 py-3 sm:px-5">任务 ID</th>
              <th class="px-4 py-3">状态</th>
              <th class="px-4 py-3">
                计划时间<span class="font-normal normal-case text-slate-600">{{ timeParen }}</span>
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/80">
            <tr v-for="row in queueItems" :key="row.taskId" class="text-slate-300">
              <td class="px-4 py-3 font-mono text-xs text-slate-300 sm:px-5">
                {{ row.taskId }}
                <span
                  v-if="row.stepLabelZh || row.stepKey"
                  class="mt-0.5 block text-[11px] font-sans text-slate-500"
                >
                  {{ row.stepLabelZh ?? row.stepKey }}
                </span>
              </td>
              <td class="px-4 py-3">
                <span
                  class="inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium"
                  :class="taskStateClass(row.state)"
                >
                  {{ zhTaskState(String(row.state)) }}
                </span>
              </td>
              <td class="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-400">
                {{ formatIsoTime(row.scheduledAt) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template v-else-if="tab === 'events'">
      <div
        v-if="eventItems.length === 0"
        class="px-4 py-10 text-center text-slate-500 sm:px-5"
      >
        {{ EXECUTION_DETAIL_COPY.eventsEmpty }}
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-[640px] w-full border-collapse text-left text-sm">
          <thead>
            <tr class="border-b border-slate-800/90 text-xs font-medium uppercase tracking-wide text-slate-500">
              <th class="whitespace-nowrap px-4 py-3 sm:px-5">
                时间<span class="font-normal normal-case text-slate-600">{{ timeParen }}</span>
              </th>
              <th class="w-[12rem] px-4 py-3">类型</th>
              <th class="px-4 py-3">摘要</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/80">
            <tr
              v-for="(row, idx) in eventItems"
              :key="`${row.at}-${row.eventType}-${idx}`"
              class="text-slate-300"
            >
              <td class="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-500 sm:px-5">
                {{ formatIsoTime(row.at) }}
              </td>
              <td class="px-4 py-3">
                <p class="text-xs text-slate-200">{{ zhRuntimeEventType(row.eventType) }}</p>
                <p
                  v-if="zhRuntimeEventType(row.eventType) !== row.eventType"
                  class="mt-0.5 font-mono text-[10px] text-slate-600"
                >
                  {{ row.eventType }}
                </p>
              </td>
              <td class="px-4 py-3 text-slate-400">{{ row.summary }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template v-else-if="tab === 'retries'">
      <div
        v-if="retryItems.length === 0"
        class="px-4 py-10 text-center text-slate-500 sm:px-5"
      >
        {{ EXECUTION_DETAIL_COPY.retryEmpty }}
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-[480px] w-full border-collapse text-left text-sm">
          <thead>
            <tr class="border-b border-slate-800/90 text-xs font-medium uppercase tracking-wide text-slate-500">
              <th class="w-16 px-4 py-3 sm:px-5">次序</th>
              <th class="whitespace-nowrap px-4 py-3">
                时间<span class="font-normal normal-case text-slate-600">{{ timeParen }}</span>
              </th>
              <th class="px-4 py-3">原因</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/80">
            <tr v-for="row in retryItems" :key="`${row.attempt}-${row.at}`" class="text-slate-300">
              <td class="px-4 py-3 tabular-nums text-slate-300 sm:px-5">{{ row.attempt }}</td>
              <td class="whitespace-nowrap px-4 py-3 font-mono text-xs text-slate-500">
                {{ formatIsoTime(row.at) }}
              </td>
              <td class="px-4 py-3 text-slate-400">{{ row.reason }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <template v-else-if="tab === 'recovery'">
      <div class="space-y-4 p-4 sm:p-5">
        <div>
          <h2 class="text-[15px] font-semibold text-white">
            {{ recovery?.recoveryTitle ?? EXECUTION_DETAIL_COPY.recoveryTitle }}
          </h2>
          <p class="mt-2 text-sm leading-relaxed text-slate-400">
            {{ recovery?.recoveryBody ?? EXECUTION_DETAIL_COPY.recoveryBody }}
            <RouterLink
              class="ml-1 text-sky-400/90 hover:text-sky-300 hover:underline"
              :to="observabilityHref"
            >
              {{ EXECUTION_DETAIL_COPY.obsLink }}
            </RouterLink>
          </p>
        </div>
        <dl
          v-if="recovery"
          class="grid gap-3 rounded-md border border-slate-800/80 bg-slate-950/35 p-3 text-xs sm:grid-cols-2"
        >
          <div>
            <dt class="text-slate-500">caseKind</dt>
            <dd class="font-mono text-slate-300">{{ recovery.caseKind }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">resolutionStatus</dt>
            <dd class="font-mono text-slate-300">{{ recovery.resolutionStatus }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">stillUnknown</dt>
            <dd>{{ recovery.stillUnknown ? '是' : '否' }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">executionState</dt>
            <dd class="font-mono text-slate-300">{{ recovery.executionState }}</dd>
          </div>
        </dl>
      </div>
    </template>
  </section>
</template>
