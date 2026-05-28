<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 页头改用 **`AdminPageHeader`**
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 列表数据行除「规则」列外 **`align-middle`**，与多行规则列垂直居中对齐
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 操作反馈改用全局 **`adminToast`**；刷新成功 Toast
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 筛选工具条统计标签改用 **`UiStatChip`**，与操作按钮行高对齐
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 人工确认规则列表（GET/PATCH/DELETE/reset · 对齐原型 ConfirmationRulesPanel）
修改功能: 列表 table-fixed + colgroup 固定「规则」列宽，其余列 nowrap / truncate 防挤换行
-->
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import {
  formatTriggerSummary,
  riskLevelBadgeClass,
  riskLevelLabel,
  RULE_ACTION_META,
  RISK_LEVEL_OPTIONS,
  ruleActionNeedsStrongDisableGuard,
  scenarioLabels,
  type RiskLevel,
} from '@/entities/confirmation-rules/confirmation-rules-catalog'
import {
  deleteConfirmationRule,
  explainConfirmationRuleError,
  listConfirmationRules,
  patchConfirmationRuleEnabled,
  resetConfirmationRules,
  type ConfirmationRuleItem,
} from '@/shared/api/admin-confirmation-rules'
import { adminNotifyManualRefresh, adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import AdminPage from '@/shared/ui/AdminPage.vue'
import {
  ADMIN_TOOLBAR_CLUSTER_CLASS,
  AdminPageHeader,
  UiButton,
  UiInput,
  UiModal,
  UiStatChip,
  UiSwitch,
  UiTableAction,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
} from '@/shared/ui'

const router = useRouter()

const items = ref<ConfirmationRuleItem[]>([])
const enabledCount = ref(0)
const loading = ref(false)
const listError = ref<string | null>(null)

const riskFilter = ref<RiskLevel | 'all'>('all')
const keyword = ref('')

const detailRow = ref<ConfirmationRuleItem | null>(null)

const disableGuardOpen = ref(false)
const pendingDisableRow = ref<ConfirmationRuleItem | null>(null)

const deleteOpen = ref(false)
const pendingDeleteRow = ref<ConfirmationRuleItem | null>(null)
const deleteSubmitting = ref(false)

const resetOpen = ref(false)
const resetSubmitting = ref(false)

const SPEC_FOOTER_PATHS = [
  'risk/hitl-and-automation-matrix.md',
  'risk/user-confirmation.md',
  'domains/agent/agent-orchestration/confirmation-flow.md',
  'prompts/confirmation/high-risk-confirmation.md',
]

const filteredRows = computed(() => {
  let rows = items.value
  if (riskFilter.value !== 'all') {
    rows = rows.filter((r) => r.riskLevel === riskFilter.value)
  }
  const q = keyword.value.trim().toLowerCase()
  if (q) {
    rows = rows.filter(
      (r) =>
        r.title.toLowerCase().includes(q) ||
        r.summary.toLowerCase().includes(q) ||
        r.id.toLowerCase().includes(q) ||
        formatTriggerSummary(r.triggerConditions).toLowerCase().includes(q) ||
        scenarioLabels(r.scenarios).toLowerCase().includes(q) ||
        RULE_ACTION_META[r.action].label.toLowerCase().includes(q),
    )
  }
  return rows
})

const tableScrollX = computed(() => !loading.value && filteredRows.value.length > 0)
const hasActiveFilter = computed(
  () => riskFilter.value !== 'all' || keyword.value.trim().length > 0,
)

async function load() {
  loading.value = true
  listError.value = null
  try {
    const res = await listConfirmationRules()
    items.value = res.items
    enabledCount.value = res.enabledCount
  } catch (e) {
    listError.value = explainConfirmationRuleError(e)
    items.value = []
    enabledCount.value = 0
  } finally {
    loading.value = false
  }
}

async function onRefresh() {
  await load()
  adminNotifyManualRefresh(true, {
    ok: !listError.value,
    successMessage: '已刷新',
    errorMessage: listError.value,
  })
}

async function applyEnabled(row: ConfirmationRuleItem, next: boolean) {
  try {
    const updated = await patchConfirmationRuleEnabled(row.id, next)
    items.value = items.value.map((r) => (r.id === updated.id ? updated : r))
    enabledCount.value = items.value.filter((r) => r.enabled).length
    if (detailRow.value?.id === updated.id) detailRow.value = updated
    adminToastSuccess(next ? '已启用规则' : '已关闭规则')
  } catch (e) {
    const msg = explainConfirmationRuleError(e)
    listError.value = msg
    adminToastError(msg)
  }
}

function requestToggle(row: ConfirmationRuleItem, next: boolean) {
  if (!next && ruleActionNeedsStrongDisableGuard(row.action)) {
    pendingDisableRow.value = row
    disableGuardOpen.value = true
    return
  }
  void applyEnabled(row, next)
}

function confirmDisableGuard() {
  const row = pendingDisableRow.value
  disableGuardOpen.value = false
  pendingDisableRow.value = null
  if (row) void applyEnabled(row, false)
}

function cancelDisableGuard() {
  disableGuardOpen.value = false
  pendingDisableRow.value = null
}

function openDelete(row: ConfirmationRuleItem) {
  if (row.isBuiltin) return
  pendingDeleteRow.value = row
  deleteOpen.value = true
}

async function confirmDelete() {
  const row = pendingDeleteRow.value
  if (!row) return
  deleteSubmitting.value = true
  try {
    await deleteConfirmationRule(row.id)
    if (detailRow.value?.id === row.id) detailRow.value = null
    deleteOpen.value = false
    pendingDeleteRow.value = null
    adminToastSuccess('已删除规则')
    await load()
  } catch (e) {
    const msg = explainConfirmationRuleError(e)
    listError.value = msg
    adminToastError(msg)
  } finally {
    deleteSubmitting.value = false
  }
}

function requestReset() {
  resetOpen.value = true
}

async function confirmReset() {
  resetSubmitting.value = true
  try {
    const res = await resetConfirmationRules()
    items.value = res.items
    enabledCount.value = res.enabledCount
    riskFilter.value = 'all'
    keyword.value = ''
    detailRow.value = null
    resetOpen.value = false
    adminToastSuccess('已恢复默认规则与启用态')
  } catch (e) {
    const msg = explainConfirmationRuleError(e)
    listError.value = msg
    adminToastError(msg)
  } finally {
    resetSubmitting.value = false
  }
}

function goEdit(row: ConfirmationRuleItem) {
  router.push({ name: 'ai.confirmation-rules.edit', params: { ruleId: row.id } })
}

onMounted(() => {
  void load()
})
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="人工确认规则"
      :badges="[{ label: '风控治理', tone: 'violet' }]"
      description="风控规则中心：集中管理高风险交易与资金动作的确认门槛（何时须用户点头、何时加码二次确认）。可与风险限制、工具授权一起核对。"
      dev-meta="pageId · ai.confirmation-rules · GET /api/v1/admin/confirmation-rules"
      :error="listError"
    >
      <template #actions>
        <UiButton type="button" variant="secondary" size="sm" :loading="loading" @click="onRefresh">
          刷新
        </UiButton>
      </template>
    </AdminPageHeader>

    <div
      class="mb-4 rounded-lg border border-sky-500/25 bg-sky-500/10 px-4 py-3 text-sm leading-relaxed text-sky-100/95"
      role="note"
    >
      部分高风险交易需用户确认后才能执行，用于降低误操作与资金风险。名义金额、杠杆等阈值可在
      <RouterLink
        class="font-medium text-sky-200 underline-offset-4 hover:text-white hover:underline"
        to="/ai/runtime-orchestration?tab=policy"
      >
        风险限制
      </RouterLink>
      统一配置。
    </div>

    <section class="admin-panel mb-4 p-4 sm:p-5">
      <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h2 class="text-[15px] font-semibold text-white">筛选条件</h2>
        <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
          <UiButton type="button" size="sm" @click="router.push({ name: 'ai.confirmation-rules.new' })">
            新建规则
          </UiButton>
          <UiStatChip tone="neutral">
            命中 {{ filteredRows.length }} / {{ items.length }}
          </UiStatChip>
          <UiStatChip tone="neutral">
            已启用 {{ enabledCount }} / {{ items.length }}
          </UiStatChip>
          <UiButton type="button" variant="secondary" size="sm" @click="requestReset">恢复默认</UiButton>
        </div>
      </div>

      <div class="mb-4 flex flex-wrap gap-2">
        <button
          type="button"
          class="admin-seg text-xs sm:text-sm"
          :class="
            riskFilter === 'all'
              ? 'admin-seg-active'
              : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
          "
          @click="riskFilter = 'all'"
        >
          全部风险
        </button>
        <button
          v-for="opt in RISK_LEVEL_OPTIONS"
          :key="opt.value"
          type="button"
          class="admin-seg text-xs sm:text-sm"
          :class="
            riskFilter === opt.value
              ? 'admin-seg-active'
              : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
          "
          @click="riskFilter = opt.value"
        >
          {{ opt.label }}
        </button>
      </div>

      <UiInput
        v-model="keyword"
        type="search"
        label="关键字"
        placeholder="规则名称、说明、触发条件、场景、处理动作…"
      />
    </section>

    <section class="admin-panel overflow-hidden p-0">
      <div
        class="rounded-lg border-0"
        :class="adminTableHostOverflowClass(tableScrollX)"
      >
        <table
          class="admin-cr-rules-grid w-full table-fixed text-left text-sm"
          :class="tableScrollX ? 'min-w-[1280px]' : ''"
        >
          <colgroup>
            <col class="cr-col-rule" />
            <col class="cr-col-trigger" />
            <col class="cr-col-risk" />
            <col class="cr-col-scenarios" />
            <col class="cr-col-action" />
            <col class="cr-col-enabled" />
            <col class="cr-col-ops" />
          </colgroup>
          <thead class="border-b border-slate-800 bg-slate-900/85 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th class="cr-col-rule px-4 py-3 align-bottom" scope="col">规则</th>
              <th class="min-w-0 px-4 py-3 align-bottom whitespace-nowrap" scope="col">触发条件</th>
              <th class="min-w-0 px-4 py-3 align-bottom whitespace-nowrap" scope="col">风险等级</th>
              <th class="min-w-0 px-4 py-3 align-bottom whitespace-nowrap" scope="col">适用场景</th>
              <th class="min-w-0 px-4 py-3 align-bottom whitespace-nowrap" scope="col">处理动作</th>
              <th class="min-w-0 px-4 py-3 text-center align-bottom whitespace-nowrap" scope="col">
                启用
              </th>
              <th class="cr-col-ops px-4 py-3 text-right align-bottom whitespace-nowrap" scope="col">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/90">
            <UiTableEmptyRow v-if="loading" :colspan="7" state="loading" />
            <UiTableEmptyRow
              v-else-if="filteredRows.length === 0"
              :colspan="7"
              :state="hasActiveFilter ? 'filtered' : 'empty'"
              :title="hasActiveFilter ? undefined : '暂无规则'"
              :description="
                hasActiveFilter
                  ? '可尝试放宽或重置筛选条件。'
                  : '可通过「新建规则」添加自定义条目。'
              "
            />
            <tr
              v-for="row in filteredRows"
              v-else
              :key="row.id"
              class="transition-colors hover:bg-slate-900/40"
            >
              <td class="cr-col-rule px-4 py-3 align-top">
                <div class="min-w-0 space-y-1">
                  <div class="flex min-w-0 flex-wrap items-center gap-1.5">
                    <span
                      class="min-w-0 truncate text-[13px] font-medium text-slate-100"
                      :title="row.title"
                    >{{ row.title }}</span>
                    <span
                      v-if="row.isBuiltin"
                      class="rounded border border-slate-600 bg-slate-800/80 px-1.5 py-0.5 text-[10px] text-slate-400"
                    >
                      内置
                    </span>
                    <span
                      v-else
                      class="rounded border border-sky-500/30 bg-sky-500/10 px-1.5 py-0.5 text-[10px] text-sky-200"
                    >
                      自定义
                    </span>
                    <span
                      v-if="ruleActionNeedsStrongDisableGuard(row.action)"
                      class="rounded border border-rose-500/35 bg-rose-500/10 px-1.5 py-0.5 text-[10px] text-rose-200"
                    >
                      强管控
                    </span>
                  </div>
                  <p
                    class="line-clamp-2 text-xs leading-relaxed text-slate-500"
                    :title="row.summary"
                  >
                    {{ row.summary }}
                  </p>
                </div>
              </td>
              <td class="min-w-0 px-4 py-3 align-middle text-xs text-slate-400">
                <span
                  class="block truncate"
                  :title="formatTriggerSummary(row.triggerConditions)"
                >
                  {{ formatTriggerSummary(row.triggerConditions) }}
                </span>
              </td>
              <td class="min-w-0 whitespace-nowrap px-4 py-3 align-middle">
                <span
                  class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                  :class="riskLevelBadgeClass(row.riskLevel)"
                >
                  {{ riskLevelLabel(row.riskLevel) }}
                </span>
              </td>
              <td class="min-w-0 px-4 py-3 align-middle text-xs text-slate-400">
                <span class="block truncate" :title="scenarioLabels(row.scenarios)">
                  {{ scenarioLabels(row.scenarios) }}
                </span>
              </td>
              <td class="min-w-0 whitespace-nowrap px-4 py-3 align-middle">
                <span
                  class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                  :class="RULE_ACTION_META[row.action].badgeClass"
                  :title="RULE_ACTION_META[row.action].hint"
                >
                  {{ RULE_ACTION_META[row.action].label }}
                </span>
              </td>
              <td class="min-w-0 whitespace-nowrap px-4 py-3 text-center align-middle">
                <UiSwitch
                  :model-value="row.enabled"
                  size="sm"
                  :aria-label="`${row.title} 启用`"
                  @update:model-value="requestToggle(row, $event)"
                />
              </td>
              <td class="cr-col-ops px-4 py-3 text-right align-middle">
                <div class="flex flex-nowrap items-center justify-end gap-1">
                  <UiTableAction variant="sky" icon="eye" @click="detailRow = row">详情</UiTableAction>
                  <UiTableAction
                    v-if="!row.isBuiltin"
                    variant="slate"
                    icon="file-text"
                    @click="goEdit(row)"
                  >
                    编辑
                  </UiTableAction>
                  <UiTableAction
                    v-if="!row.isBuiltin"
                    variant="rose"
                    icon="trash"
                    @click="openDelete(row)"
                  >
                    删除
                  </UiTableAction>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <footer class="mt-6 border-t border-slate-800/80 pt-4 text-xs text-slate-600">
      <p class="mb-2 text-slate-500">规格路径：</p>
      <ul class="list-inside list-disc space-y-1">
        <li v-for="p in SPEC_FOOTER_PATHS" :key="p">规格要求 / {{ p }}</li>
      </ul>
    </footer>

    <Teleport to="body">
      <Transition name="admin-drawer-scrim">
        <div
          v-if="detailRow"
          class="fixed inset-0 z-40 bg-slate-950/55"
          aria-hidden="true"
          @click.self="detailRow = null"
        />
      </Transition>
      <Transition name="admin-drawer-panel">
        <aside
          v-if="detailRow"
          class="fixed inset-y-0 right-0 z-50 flex w-full max-w-md flex-col border-l border-slate-800 bg-slate-950 shadow-2xl"
          role="dialog"
          aria-modal="true"
          aria-label="规则详情"
        >
          <div class="flex items-start justify-between gap-2 border-b border-slate-800 px-4 py-3">
            <h3 class="text-sm font-medium text-white">{{ detailRow.title }}</h3>
            <button
              type="button"
              class="rounded p-1 text-slate-500 hover:bg-slate-800 hover:text-slate-300"
              aria-label="关闭"
              @click="detailRow = null"
            >
              <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
              </svg>
            </button>
          </div>
          <div class="flex-1 overflow-y-auto px-4 py-4 text-sm">
            <div class="mb-4 flex flex-wrap gap-2">
              <span
                v-if="detailRow.isBuiltin"
                class="rounded border border-slate-600 px-2 py-0.5 text-[11px] text-slate-400"
              >
                内置
              </span>
              <span
                v-else
                class="rounded border border-sky-500/30 bg-sky-500/10 px-2 py-0.5 text-[11px] text-sky-200"
              >
                自定义
              </span>
              <span
                class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                :class="riskLevelBadgeClass(detailRow.riskLevel)"
              >
                {{ riskLevelLabel(detailRow.riskLevel) }}
              </span>
              <span
                class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                :class="RULE_ACTION_META[detailRow.action].badgeClass"
              >
                {{ RULE_ACTION_META[detailRow.action].label }}
              </span>
            </div>
            <p class="mb-4 text-xs leading-relaxed text-slate-400">{{ detailRow.summary }}</p>
            <p class="mb-1 text-xs font-medium text-slate-500">触发条件</p>
            <ul class="mb-4 list-inside list-disc text-xs text-slate-400">
              <li v-for="(line, idx) in detailRow.triggerConditions" :key="idx">
                {{ formatTriggerSummary([line]) }}
              </li>
            </ul>
            <p class="mb-1 text-xs font-medium text-slate-500">适用场景</p>
            <p class="mb-4 text-xs text-slate-300">{{ scenarioLabels(detailRow.scenarios) }}</p>
            <p class="mb-1 text-xs font-medium text-slate-500">启用</p>
            <div class="mb-4 inline-flex items-center gap-2">
              <UiSwitch
                :model-value="detailRow.enabled"
                size="sm"
                :aria-label="`${detailRow.title} 启用`"
                @update:model-value="requestToggle(detailRow, $event)"
              />
              <span class="text-xs text-slate-400">{{ detailRow.enabled ? '已启用' : '已关闭' }}</span>
            </div>
            <p class="break-all font-mono text-[10px] text-slate-600">{{ detailRow.id }}</p>
            <div v-if="!detailRow.isBuiltin" class="mt-6 flex gap-2">
              <UiButton type="button" size="sm" @click="goEdit(detailRow)">编辑</UiButton>
            </div>
          </div>
        </aside>
      </Transition>
    </Teleport>

    <UiModal
      v-model:open="disableGuardOpen"
      title="确认关闭该规则？"
      description="该规则涉及强制确认或禁止自动执行类管控，关闭可能增加误操作与资金风险。仅建议在演练环境评估。"
      :show-default-close="false"
    >
      <template #footer>
        <UiButton variant="ghost" type="button" @click="cancelDisableGuard">保持启用</UiButton>
        <UiButton variant="danger" type="button" @click="confirmDisableGuard">仍要关闭</UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="deleteOpen"
      title="删除该自定义规则？"
      description="删除后不可恢复。"
      :show-default-close="false"
    >
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="deleteSubmitting" @click="deleteOpen = false">
          取消
        </UiButton>
        <UiButton variant="danger" type="button" :loading="deleteSubmitting" @click="confirmDelete">
          删除
        </UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="resetOpen"
      title="恢复默认？"
      description="将自定义规则恢复为三条演示样例，并把内置规则的启用状态恢复为初始默认。"
      :show-default-close="false"
    >
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="resetSubmitting" @click="resetOpen = false">
          取消
        </UiButton>
        <UiButton variant="danger" type="button" :loading="resetSubmitting" @click="confirmReset">
          恢复
        </UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>

<style scoped>
/* 规则列固定宽度，其余列单行展示；窄屏依赖表格外层横向滚动 */
.admin-cr-rules-grid {
  table-layout: fixed;
}
.admin-cr-rules-grid col.cr-col-rule {
  width: 17.5rem;
}
.admin-cr-rules-grid col.cr-col-trigger {
  width: 16%;
}
.admin-cr-rules-grid col.cr-col-risk {
  width: 5.5rem;
}
.admin-cr-rules-grid col.cr-col-scenarios {
  width: 12%;
}
.admin-cr-rules-grid col.cr-col-action {
  width: 6.5rem;
}
.admin-cr-rules-grid col.cr-col-enabled {
  width: 3.5rem;
}
.admin-cr-rules-grid col.cr-col-ops {
  width: 10.5rem;
  min-width: 10.5rem;
}
.admin-cr-rules-grid th.cr-col-rule,
.admin-cr-rules-grid td.cr-col-rule {
  width: 17.5rem;
  min-width: 17.5rem;
  max-width: 17.5rem;
}
.admin-cr-rules-grid th.cr-col-ops,
.admin-cr-rules-grid td.cr-col-ops {
  min-width: 10.5rem;
}
.admin-cr-rules-grid tbody td:not(.cr-col-rule) {
  vertical-align: middle;
}
</style>
