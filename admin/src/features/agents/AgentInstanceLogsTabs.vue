<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 分页按钮簇 **`items-center`** 与 **`ADMIN_TOOLBAR_CLUSTER_CLASS`** 对齐
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 日志三张表空态 **`UiTableEmptyRow`**；加载态表内展示；无数据时取消横向滚动
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 日志三张表「时间线」列 **`UiTableAction`**（时钟图标）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: **FR-AM-L01–L03** 实例日志 Tab（**`GET …/logs/conversations|tools|errors`** · 深链 **`observability*Path`**）
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

import {
  getAgentInstanceLogsConversations,
  getAgentInstanceLogsErrors,
  getAgentInstanceLogsTools,
  type InstanceConversationLogItem,
  type InstanceErrorLogItem,
  type InstanceToolLogItem,
} from '@/shared/api/agent-agent-control'
import { AppError } from '@/shared/api/errors'
import { formatIsoTime, zhExecutionRuntimeStatus } from '@/shared/copy/zh-runtime'
import AdminTimeTh from '@/shared/ui/AdminTimeTh.vue'
import {
  ADMIN_TOOLBAR_CLUSTER_CLASS,
  UiButton,
  UiTableAction,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
} from '@/shared/ui'
import { buildObservabilitySearch } from '@/shared/utils/observability-deep-link'
import { observabilityAdminApiPathToRouteHref } from '@/shared/utils/observability-admin-path'

const props = defineProps<{
  instanceId: string
  telegramUserId: string
}>()

type LogTab = 'conversations' | 'tools' | 'errors'

const activeTab = ref<LogTab>('conversations')
const limit = 20
const offset = ref(0)
const loading = ref(false)
const errorText = ref<string | null>(null)
const convItems = ref<InstanceConversationLogItem[]>([])
const toolItems = ref<InstanceToolLogItem[]>([])
const errItems = ref<InstanceErrorLogItem[]>([])

const convTableScrollX = computed(() => !loading.value && convItems.value.length > 0)
const toolTableScrollX = computed(() => !loading.value && toolItems.value.length > 0)
const errTableScrollX = computed(() => !loading.value && errItems.value.length > 0)
const total = ref(0)

const observabilityExecutionHref = computed(() => {
  const u = props.telegramUserId?.trim()
  if (!u) return '/observability'
  return `/observability${buildObservabilitySearch({ userId: u, tab: 'execution' })}`
})

const executionsKeywordHref = computed(() => {
  const u = props.telegramUserId?.trim()
  if (!u) return '/runtime/executions'
  return `/runtime/executions?q=${encodeURIComponent(u)}`
})

async function fetchTab() {
  const id = props.instanceId.trim()
  if (!id) return
  loading.value = true
  errorText.value = null
  try {
    if (activeTab.value === 'conversations') {
      const res = await getAgentInstanceLogsConversations(id, {
        limit,
        offset: offset.value,
      })
      convItems.value = res.items
      total.value = res.total
    } else if (activeTab.value === 'tools') {
      const res = await getAgentInstanceLogsTools(id, { limit, offset: offset.value })
      toolItems.value = res.items
      total.value = res.total
    } else {
      const res = await getAgentInstanceLogsErrors(id, { limit, offset: offset.value })
      errItems.value = res.items
      total.value = res.total
    }
  } catch (e) {
    errorText.value = e instanceof AppError ? e.message : '加载失败'
    convItems.value = []
    toolItems.value = []
    errItems.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

watch(
  [() => props.instanceId, activeTab, offset],
  () => {
    void fetchTab()
  },
  { immediate: true },
)

function setTab(t: LogTab) {
  activeTab.value = t
  offset.value = 0
}

function nextPage() {
  if (offset.value + limit < total.value) offset.value += limit
}

function prevPage() {
  offset.value = Math.max(0, offset.value - limit)
}

function rowHrefConv(row: InstanceConversationLogItem): string {
  return observabilityAdminApiPathToRouteHref(row.observabilityExecutionPath)
}

function rowHrefTool(row: InstanceToolLogItem): string {
  return observabilityAdminApiPathToRouteHref(row.observabilityTimelinePath)
}

function rowHrefErr(row: InstanceErrorLogItem): string {
  return observabilityAdminApiPathToRouteHref(row.observabilityTimelinePath)
}

const tabBtn =
  'rounded-md border px-3 py-1.5 text-xs font-medium transition-colors sm:text-sm border-slate-700 bg-slate-900 text-slate-300 hover:border-slate-600 hover:text-white'
const tabBtnActive = 'border-emerald-500/50 bg-emerald-500/15 text-emerald-100'
</script>

<template>
  <section class="admin-panel overflow-hidden p-4 sm:p-5">
    <h2 class="mb-1 text-[15px] font-semibold text-white">实例日志（L01–L03）</h2>
    <p class="mb-4 max-w-3xl text-xs leading-relaxed text-slate-500">
      Phase1 投影自 agent_execution / agent_execution_event；行内链接跳转执行详情时间线（Observability 同源）。
    </p>

    <div class="mb-4 flex flex-wrap gap-2">
      <RouterLink
        class="inline-flex items-center rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-emerald-500 sm:text-sm"
        :to="observabilityExecutionHref"
      >
        执行协查
      </RouterLink>
      <RouterLink
        class="inline-flex items-center rounded-md border border-slate-600 bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-800 sm:text-sm"
        :to="executionsKeywordHref"
      >
        执行记录
      </RouterLink>
    </div>

    <div class="mb-4 flex flex-wrap gap-2 border-b border-slate-800 pb-3">
      <button
        type="button"
        :class="[tabBtn, activeTab === 'conversations' ? tabBtnActive : '']"
        @click="setTab('conversations')"
      >
        对话（执行）
      </button>
      <button type="button" :class="[tabBtn, activeTab === 'tools' ? tabBtnActive : '']" @click="setTab('tools')">
        Tool 调用
      </button>
      <button type="button" :class="[tabBtn, activeTab === 'errors' ? tabBtnActive : '']" @click="setTab('errors')">
        错误
      </button>
    </div>

    <p v-if="errorText" class="mb-3 text-sm text-rose-400" role="alert">{{ errorText }}</p>

    <div v-if="!loading" class="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500">
        <span>共 {{ total }} 条 · 每页 {{ limit }}</span>
        <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
          <UiButton type="button" size="sm" variant="secondary" :disabled="offset <= 0" @click="prevPage">
            上一页
          </UiButton>
          <UiButton
            type="button"
            size="sm"
            variant="secondary"
            :disabled="offset + limit >= total"
            @click="nextPage"
          >
            下一页
          </UiButton>
        </div>
      </div>

      <!-- conversations -->
      <div
        v-if="activeTab === 'conversations'"
        class="rounded-lg border border-slate-800"
        :class="adminTableHostOverflowClass(convTableScrollX)"
      >
        <table
          class="w-full text-left text-sm"
          :class="convTableScrollX ? 'min-w-[720px]' : ''"
        >
          <thead class="border-b border-slate-800 bg-slate-900/80 text-xs text-slate-500">
            <tr>
              <th class="px-3 py-2 font-medium">executionId</th>
              <th class="px-3 py-2 font-medium">状态</th>
              <th class="px-3 py-2 font-medium normal-case"><AdminTimeTh>创建</AdminTimeTh></th>
              <th class="px-3 py-2 font-medium">摘要</th>
              <th class="px-3 py-2 font-medium text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <UiTableEmptyRow v-if="loading" :colspan="5" state="loading" />
            <UiTableEmptyRow v-else-if="convItems.length === 0" :colspan="5" state="empty" title="暂无记录" />
            <tr v-for="r in convItems" v-else :key="r.executionId + r.createdAt" class="hover:bg-slate-900/40">
              <td class="max-w-[220px] px-3 py-2 font-mono text-xs text-slate-300">{{ r.executionId }}</td>
              <td class="whitespace-nowrap px-3 py-2 text-xs">{{ zhExecutionRuntimeStatus(r.state) }}</td>
              <td class="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-500">
                {{ formatIsoTime(r.createdAt) }}
              </td>
              <td class="max-w-md truncate px-3 py-2 text-xs text-slate-400" :title="r.notePreview ?? ''">
                {{ r.notePreview ?? '—' }}
              </td>
              <td class="px-3 py-2 text-right">
                <UiTableAction variant="sky" icon="clock" :to="rowHrefConv(r)">时间线</UiTableAction>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- tools -->
      <div
        v-else-if="activeTab === 'tools'"
        class="rounded-lg border border-slate-800"
        :class="adminTableHostOverflowClass(toolTableScrollX)"
      >
        <table
          class="w-full text-left text-sm"
          :class="toolTableScrollX ? 'min-w-[880px]' : ''"
        >
          <thead class="border-b border-slate-800 bg-slate-900/80 text-xs text-slate-500">
            <tr>
              <th class="px-3 py-2 font-medium">event</th>
              <th class="px-3 py-2 font-medium">executionId</th>
              <th class="px-3 py-2 font-medium">stepKind</th>
              <th class="px-3 py-2 font-medium normal-case"><AdminTimeTh>创建</AdminTimeTh></th>
              <th class="px-3 py-2 font-medium text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <UiTableEmptyRow v-if="loading" :colspan="5" state="loading" />
            <UiTableEmptyRow v-else-if="toolItems.length === 0" :colspan="5" state="empty" title="暂无记录" />
            <tr v-for="r in toolItems" v-else :key="r.eventId" class="hover:bg-slate-900/40">
              <td class="px-3 py-2 font-mono text-xs text-slate-300">{{ r.eventName }}</td>
              <td class="max-w-[200px] px-3 py-2 font-mono text-xs text-slate-400">{{ r.executionId }}</td>
              <td class="px-3 py-2 font-mono text-xs text-slate-500">{{ r.stepKind ?? '—' }}</td>
              <td class="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-500">
                {{ formatIsoTime(r.createdAt) }}
              </td>
              <td class="px-3 py-2 text-right">
                <UiTableAction variant="sky" icon="clock" :to="rowHrefTool(r)">时间线</UiTableAction>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- errors -->
      <div
        v-else
        class="rounded-lg border border-slate-800"
        :class="adminTableHostOverflowClass(errTableScrollX)"
      >
        <table
          class="w-full text-left text-sm"
          :class="errTableScrollX ? 'min-w-[800px]' : ''"
        >
          <thead class="border-b border-slate-800 bg-slate-900/80 text-xs text-slate-500">
            <tr>
              <th class="px-3 py-2 font-medium">kind</th>
              <th class="px-3 py-2 font-medium">executionId</th>
              <th class="px-3 py-2 font-medium">状态/结果</th>
              <th class="px-3 py-2 font-medium normal-case"><AdminTimeTh>创建</AdminTimeTh></th>
              <th class="px-3 py-2 font-medium text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <UiTableEmptyRow v-if="loading" :colspan="5" state="loading" />
            <UiTableEmptyRow v-else-if="errItems.length === 0" :colspan="5" state="empty" title="暂无记录" />
            <tr v-for="(r, idx) in errItems" v-else :key="r.executionId + r.createdAt + idx" class="hover:bg-slate-900/40">
              <td class="px-3 py-2 font-mono text-xs text-rose-200/90">{{ r.kind }}</td>
              <td class="max-w-[200px] px-3 py-2 font-mono text-xs text-slate-400">{{ r.executionId }}</td>
              <td class="max-w-[240px] truncate px-3 py-2 text-xs text-slate-300" :title="r.message ?? ''">
                {{ r.stateOrOutcome }}
              </td>
              <td class="whitespace-nowrap px-3 py-2 font-mono text-xs text-slate-500">
                {{ formatIsoTime(r.createdAt) }}
              </td>
              <td class="px-3 py-2 text-right">
                <UiTableAction variant="sky" icon="clock" :to="rowHrefErr(r)">时间线</UiTableAction>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
  </section>
</template>
