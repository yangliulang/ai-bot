<!--
作者: Cursor Agent
日期: 2026-05-26
修改功能: 技能与工具 · 交互对齐原型 · 样式对齐 admin 整站
-->
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import {
  countRuntimePublishedStats,
  countSpecReadyStats,
  matrixStatusClass,
  matrixStatusLabel,
  mergeSkillRegistryWithApi,
  type SkillRegistryRowView,
} from '@/entities/tool-registry/skill-registry-catalog'
import {
  MOCK_TOOL_B_ROWS,
  MOCK_TOOL_C_ROWS,
  type ToolRegistryRow,
} from '@/entities/tool-registry/tool-registry-mock'
import {
  SKILL_REGISTRY_PAGE,
  SKILL_REGISTRY_RUNTIME,
  TOOL_REGISTRY_TABLE,
} from '@/entities/tool-registry/tool-registry-copy'
import {
  isRowEnabled,
  loadToolRegistryState,
  persistToggle,
  resetToolRegistryDemo,
  type ToolRegistryStored,
} from '@/entities/tool-registry/tool-registry-storage'
import {
  explainSkillSpecApiError,
  listSkillOperationSpecs,
  type SkillOperationSpecSummary,
} from '@/shared/api/admin-skill-specs'
import { adminToastInfo, adminToastSuccess } from '@/shared/lib/admin-toast'
import AdminPage from '@/shared/ui/AdminPage.vue'
import {
  AdminPageHeader,
  UiButton,
  UiEnableCheckbox,
  UiInput,
  UiStatChip,
  UiTableEmptyRow,
  adminTableHostOverflowClass,
} from '@/shared/ui'

import SkillOperationDrawer from '@/pages/ai/SkillOperationDrawer.vue'
import SkillRegistryTable from '@/pages/ai/SkillRegistryTable.vue'

type RegistryTab = 'skills' | 'tools-b' | 'tools-c' | 'audit'

const apiItems = ref<SkillOperationSpecSummary[]>([])
const loading = ref(false)
const listError = ref<string | null>(null)
const skillFilter = ref('')
const showPublishedOnly = ref(false)
const activeTab = ref<RegistryTab>('skills')

const detailSkillId = ref<string | null>(null)
const detailRow = ref<SkillRegistryRowView | null>(null)

const mergedRows = computed(() => mergeSkillRegistryWithApi(apiItems.value))

const skillListFiltered = computed(() => {
  if (!showPublishedOnly.value) return mergedRows.value
  return mergedRows.value.filter((r) => r.isRuntimePublished)
})

const filteredSkillRows = computed(() => {
  const kw = skillFilter.value.trim().toLowerCase()
  if (!kw) return skillListFiltered.value
  return skillListFiltered.value.filter(
    (r) =>
      r.skillId.toLowerCase().includes(kw) ||
      r.summary.toLowerCase().includes(kw) ||
      r.userFlow.toLowerCase().includes(kw) ||
      r.exchangeAction.toLowerCase().includes(kw),
  )
})

const skillTableFiltered = computed(
  () => skillFilter.value.trim().length > 0 || showPublishedOnly.value,
)

const allRegistryRows = computed(() => [
  ...mergedRows.value.map((r) => ({
    stableId: r.skillId,
    entryClass: 'A' as const,
    defaultEnabled: r.defaultEnabled,
  })),
  ...MOCK_TOOL_B_ROWS.map((r) => ({
    stableId: r.stableId,
    entryClass: r.entryClass,
    defaultEnabled: r.defaultEnabled,
  })),
  ...MOCK_TOOL_C_ROWS.map((r) => ({
    stableId: r.stableId,
    entryClass: r.entryClass,
    defaultEnabled: r.defaultEnabled,
  })),
])

const defaultEnabledMap = computed(() => {
  const m: Record<string, boolean> = {}
  for (const r of allRegistryRows.value) m[r.stableId] = r.defaultEnabled
  return m
})

const allIds = computed(() => allRegistryRows.value.map((r) => r.stableId))

const store = ref<ToolRegistryStored>({ enabled: {}, audit: [] })

function initStore() {
  store.value = loadToolRegistryState(allIds.value, defaultEnabledMap.value)
}

const specStats = computed(() => countSpecReadyStats(mergedRows.value))
const runtimeStats = computed(() => countRuntimePublishedStats(mergedRows.value))

const stats = computed(() => {
  const countOn = (rows: { stableId: string; defaultEnabled: boolean }[]) =>
    rows.filter((r) => isRowEnabled(r.stableId, r.defaultEnabled, store.value)).length
  return {
    aOn: countOn(
      mergedRows.value.map((r) => ({ stableId: r.skillId, defaultEnabled: r.defaultEnabled })),
    ),
    aTotal: mergedRows.value.length,
    bOn: countOn(MOCK_TOOL_B_ROWS),
    bTotal: MOCK_TOOL_B_ROWS.length,
    cOn: countOn(MOCK_TOOL_C_ROWS),
    cTotal: MOCK_TOOL_C_ROWS.length,
    audit: store.value.audit.length,
  }
})

async function loadList() {
  loading.value = true
  listError.value = null
  try {
    const res = await listSkillOperationSpecs()
    apiItems.value = res.items
    initStore()
  } catch (e) {
    listError.value = explainSkillSpecApiError(e, '加载技能列表失败')
    apiItems.value = []
    initStore()
  } finally {
    loading.value = false
  }
}

function resetDemo() {
  store.value = resetToolRegistryDemo(allIds.value, defaultEnabledMap.value)
  adminToastSuccess(SKILL_REGISTRY_PAGE.resetSuccess)
}

function onSkillToggle(row: SkillRegistryRowView, enabled: boolean) {
  if (row.matrixStatus === 'tbd' && enabled) {
    adminToastInfo(SKILL_REGISTRY_PAGE.enableWarning)
  }
  store.value = persistToggle({
    stableId: row.skillId,
    entryClass: 'A',
    enabled,
    prev: store.value,
  })
}

function onToolToggle(row: ToolRegistryRow, enabled: boolean) {
  if (row.matrixStatus === 'tbd' && enabled) {
    adminToastInfo(SKILL_REGISTRY_PAGE.enableWarning)
  }
  store.value = persistToggle({
    stableId: row.stableId,
    entryClass: row.entryClass,
    enabled,
    prev: store.value,
  })
}

function openSkillDetail(skillId: string) {
  detailSkillId.value = skillId
  detailRow.value = mergedRows.value.find((r) => r.skillId === skillId) ?? null
}

function closeDrawer() {
  detailSkillId.value = null
  detailRow.value = null
}

async function onPublished() {
  await loadList()
  const id = detailSkillId.value
  if (!id) return
  detailRow.value = mergedRows.value.find((r) => r.skillId === id) ?? null
}

function toolRowEnabled(row: ToolRegistryRow): boolean {
  return isRowEnabled(row.stableId, row.defaultEnabled, store.value)
}

function toolRowClass(row: ToolRegistryRow): string {
  const parts: string[] = []
  if (row.matrixStatus === 'tbd') parts.push('admin-tool-registry-row--tbd')
  if (!toolRowEnabled(row)) parts.push('admin-tool-registry-row--disabled')
  return parts.join(' ')
}

const auditRows = computed(() => [...store.value.audit].reverse())

onMounted(() => {
  void loadList()
})
</script>

<template>
  <AdminPage width="full" class="admin-tool-registry-page">
    <AdminPageHeader
      :title="SKILL_REGISTRY_PAGE.title"
      :description="SKILL_REGISTRY_PAGE.description"
      :badges="[
        { label: SKILL_REGISTRY_PAGE.tagTrading, tone: 'violet' },
        { label: SKILL_REGISTRY_PAGE.tagPreview, tone: 'sky' },
      ]"
      dev-meta="pageId · ai.tool-registry · GET/POST v1/admin/skill-specs/*"
      :error="listError"
    >
      <template #actions>
        <UiButton type="button" variant="secondary" size="sm" @click="resetDemo">
          {{ SKILL_REGISTRY_PAGE.resetButton }}
        </UiButton>
      </template>
    </AdminPageHeader>

    <div class="admin-tool-registry-stats mb-4 grid grid-cols-2 gap-3 lg:grid-cols-5">
      <div class="admin-panel admin-tool-registry-stat-card rounded-lg px-4 py-3">
        <p class="text-xs text-slate-500">{{ SKILL_REGISTRY_PAGE.statTradingEnabled }}</p>
        <p class="mt-1 text-2xl font-semibold tabular-nums text-white">
          {{ stats.aOn }}
          <span class="text-base font-normal text-slate-500">/ {{ stats.aTotal }}</span>
        </p>
      </div>
      <div class="admin-panel admin-tool-registry-stat-card rounded-lg px-4 py-3">
        <p class="text-xs text-slate-500">{{ SKILL_REGISTRY_PAGE.statSpecReady }}</p>
        <p
          class="mt-1 text-2xl font-semibold tabular-nums"
          :class="specStats.complete === specStats.publishRequired ? 'text-emerald-300' : 'text-white'"
        >
          {{ specStats.complete }}
          <span class="text-base font-normal text-slate-500">/ {{ specStats.publishRequired }}</span>
        </p>
      </div>
      <div class="admin-panel admin-tool-registry-stat-card rounded-lg px-4 py-3">
        <p class="text-xs text-slate-500">{{ SKILL_REGISTRY_RUNTIME.statPublished }}</p>
        <p
          class="mt-1 text-2xl font-semibold tabular-nums"
          :class="
            runtimeStats.published === runtimeStats.total ? 'text-emerald-300' : 'text-white'
          "
        >
          {{ runtimeStats.published }}
          <span class="text-base font-normal text-slate-500">/ {{ runtimeStats.total }}</span>
        </p>
      </div>
      <div class="admin-panel admin-tool-registry-stat-card rounded-lg px-4 py-3">
        <p class="text-xs text-slate-500">{{ SKILL_REGISTRY_PAGE.statToolsEnabled }}</p>
        <p class="mt-1 text-2xl font-semibold tabular-nums text-white">
          {{ stats.bOn + stats.cOn }}
          <span class="text-base font-normal text-slate-500">
            / {{ stats.bTotal + stats.cTotal }}
          </span>
        </p>
      </div>
      <div class="admin-panel admin-tool-registry-stat-card rounded-lg px-4 py-3">
        <p class="text-xs text-slate-500">{{ SKILL_REGISTRY_PAGE.statAudit }}</p>
        <p class="mt-1 text-2xl font-semibold tabular-nums text-white">{{ stats.audit }}</p>
      </div>
    </div>

    <div
      class="mb-4 rounded-lg border border-sky-500/25 bg-sky-500/10 px-4 py-3 text-sm leading-relaxed text-sky-100/95"
      role="note"
    >
      <p class="font-medium text-sky-100">{{ SKILL_REGISTRY_PAGE.alertTitle }}</p>
      <p class="mt-1 text-sky-100/90">{{ SKILL_REGISTRY_PAGE.alertDescription }}</p>
    </div>

    <section class="admin-panel overflow-hidden">
      <div class="border-b border-slate-800/90 px-4 py-3 sm:px-5">
        <h2 class="text-[15px] font-semibold text-white">{{ SKILL_REGISTRY_PAGE.cardTitle }}</h2>
      </div>
      <div class="space-y-4 p-4 sm:p-5">
        <div class="flex flex-wrap gap-2 border-b border-slate-800 pb-2">
          <button
            v-for="tab in [
              {
                key: 'skills' as const,
                label: SKILL_REGISTRY_PAGE.tabTrading,
                count: filteredSkillRows.length,
                total: skillListFiltered.length,
              },
              { key: 'tools-b' as const, label: SKILL_REGISTRY_PAGE.tabReadonly, count: MOCK_TOOL_B_ROWS.length },
              { key: 'tools-c' as const, label: SKILL_REGISTRY_PAGE.tabExternal, count: MOCK_TOOL_C_ROWS.length },
              { key: 'audit' as const, label: SKILL_REGISTRY_PAGE.tabAudit, count: store.audit.length },
            ]"
            :key="tab.key"
            type="button"
            class="admin-seg inline-flex items-center gap-2 text-xs sm:text-sm"
            :class="
              activeTab === tab.key
                ? 'admin-seg-active'
                : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
            "
            @click="activeTab = tab.key"
          >
            <span>{{ tab.label }}</span>
            <UiStatChip v-if="tab.key !== 'audit' || tab.count > 0" tone="neutral">
              <template v-if="tab.key === 'skills' && skillTableFiltered">
                {{ tab.count }} / {{ tab.total }}
              </template>
              <template v-else>{{ tab.count }}</template>
            </UiStatChip>
          </button>
        </div>

        <div v-if="activeTab === 'skills'" class="space-y-3">
          <div class="flex flex-wrap items-center gap-2">
            <UiInput
              v-model="skillFilter"
              size="sm"
              class="max-w-md flex-1"
              :placeholder="SKILL_REGISTRY_PAGE.searchPlaceholder"
              aria-label="搜索技能"
            />
            <button
              type="button"
              class="admin-seg inline-flex items-center text-xs sm:text-sm"
              :class="
                showPublishedOnly
                  ? 'admin-seg-active'
                  : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
              "
              :aria-pressed="showPublishedOnly"
              @click="showPublishedOnly = !showPublishedOnly"
            >
              {{ SKILL_REGISTRY_PAGE.filterPublishedOnly }}
            </button>
          </div>
          <SkillRegistryTable
            :rows="filteredSkillRows"
            :store="store"
            :active-skill-id="detailSkillId"
            :loading="loading"
            :filtered="skillTableFiltered && mergedRows.length > 0"
            @toggle="onSkillToggle"
            @open-drawer="openSkillDetail"
          />
        </div>

        <div
          v-else-if="activeTab === 'tools-b' || activeTab === 'tools-c'"
          class="overflow-hidden rounded-lg border-0"
          :class="adminTableHostOverflowClass(true)"
        >
          <table class="w-full min-w-[40rem] table-fixed text-left text-sm">
            <thead class="border-b border-slate-800 bg-slate-900/85 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th class="w-[240px] px-4 py-3 align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.colTool }}</th>
                <th class="min-w-0 px-4 py-3 align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.colDesc }}</th>
                <th class="w-24 px-4 py-3 text-center align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.colStatus }}</th>
                <th class="w-20 px-4 py-3 text-center align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.colEnabled }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/90">
              <tr
                v-for="row in activeTab === 'tools-b' ? MOCK_TOOL_B_ROWS : MOCK_TOOL_C_ROWS"
                :key="row.stableId"
                class="align-middle"
                :class="toolRowClass(row)"
              >
                <td class="px-4 py-3 align-top">
                  <p class="text-sm font-medium text-slate-100">{{ row.summary }}</p>
                  <p class="mt-0.5 font-mono text-[11px] text-slate-500">{{ row.stableId }}</p>
                </td>
                <td class="min-w-0 px-4 py-3 align-top text-xs leading-relaxed text-slate-400">
                  {{ row.anchor }}
                </td>
                <td class="px-4 py-3 text-center align-middle">
                  <span
                    class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                    :class="matrixStatusClass(row.matrixStatus)"
                  >
                    {{ matrixStatusLabel(row.matrixStatus) }}
                  </span>
                </td>
                <td class="px-4 py-3 text-center align-middle">
                  <UiEnableCheckbox
                    :model-value="toolRowEnabled(row)"
                    :aria-label="`${row.summary} 启用`"
                    @update:model-value="onToolToggle(row, $event)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div
          v-else
          class="overflow-hidden rounded-lg border-0"
          :class="adminTableHostOverflowClass(auditRows.length > 0)"
        >
          <table class="w-full min-w-[40rem] table-fixed text-left text-sm">
            <thead class="border-b border-slate-800 bg-slate-900/85 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th class="w-[200px] px-4 py-3 align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.auditTime }}</th>
                <th class="w-16 px-4 py-3 text-center align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.auditType }}</th>
                <th class="min-w-0 px-4 py-3 align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.auditId }}</th>
                <th class="w-20 px-4 py-3 text-center align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.auditAction }}</th>
                <th class="w-24 px-4 py-3 align-bottom font-medium" scope="col">{{ TOOL_REGISTRY_TABLE.auditActor }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/90">
              <UiTableEmptyRow
                v-if="auditRows.length === 0"
                :colspan="5"
                :empty-text="TOOL_REGISTRY_TABLE.auditEmpty"
              />
              <tr v-for="(entry, idx) in auditRows" :key="`${entry.at}-${entry.stableId}-${idx}`" class="align-middle">
                <td class="px-4 py-3">
                  <code class="font-mono text-[11px] text-slate-400">{{ entry.at }}</code>
                </td>
                <td class="px-4 py-3 text-center">
                  <UiStatChip
                    :tone="entry.entryClass === 'A' ? 'violet' : entry.entryClass === 'B' ? 'info' : 'neutral'"
                  >
                    {{ entry.entryClass }}
                  </UiStatChip>
                </td>
                <td class="min-w-0 px-4 py-3">
                  <code class="block truncate font-mono text-[11px] text-slate-400">{{ entry.stableId }}</code>
                </td>
                <td class="px-4 py-3 text-center">
                  <UiStatChip :tone="entry.enabled ? 'success' : 'neutral'">
                    {{ entry.enabled ? '启用' : '停用' }}
                  </UiStatChip>
                </td>
                <td class="px-4 py-3 text-xs text-slate-400">{{ entry.actor }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <SkillOperationDrawer
      :skill-id="detailSkillId"
      :row="detailRow"
      @close="closeDrawer"
      @published="onPublished"
    />
  </AdminPage>
</template>
