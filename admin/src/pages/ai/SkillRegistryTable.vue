<!--
作者: Cursor Agent
日期: 2026-05-26
修改功能: A 类技能登记表格 · 交互对齐原型 · 样式对齐 admin 列表页
-->
<script setup lang="ts">
import {
  matrixStatusClass,
  matrixStatusLabel,
  skillDomainLabel,
  type SkillRegistryRowView,
} from '@/entities/tool-registry/skill-registry-catalog'
import { SKILL_DRAWER, SKILL_TABLE } from '@/entities/tool-registry/tool-registry-copy'
import {
  isRowEnabled,
  type ToolRegistryStored,
} from '@/entities/tool-registry/tool-registry-storage'
import { UiEnableCheckbox, UiStatChip, UiTableEmptyRow, adminTableHostOverflowClass } from '@/shared/ui'

const props = defineProps<{
  rows: SkillRegistryRowView[]
  store: ToolRegistryStored
  activeSkillId?: string | null
  loading?: boolean
  filtered?: boolean
}>()

const emit = defineEmits<{
  toggle: [row: SkillRegistryRowView, enabled: boolean]
  openDrawer: [skillId: string]
}>()

function rowEnabled(row: SkillRegistryRowView): boolean {
  return isRowEnabled(row.skillId, row.defaultEnabled, props.store)
}

function rowClass(row: SkillRegistryRowView): string {
  const parts: string[] = []
  if (row.matrixStatus === 'tbd') parts.push('admin-tool-registry-row--tbd')
  if (!rowEnabled(row)) parts.push('admin-tool-registry-row--disabled')
  if (props.activeSkillId === row.skillId) parts.push('admin-tool-registry-row--active')
  return parts.join(' ')
}
</script>

<template>
  <div
    class="overflow-hidden rounded-lg border-0"
    :class="adminTableHostOverflowClass(!loading && rows.length > 0)"
  >
    <table class="w-full min-w-[52rem] table-fixed text-left text-sm">
      <thead class="border-b border-slate-800 bg-slate-900/85 text-xs uppercase tracking-wide text-slate-500">
        <tr>
          <th class="w-[260px] px-4 py-3 align-bottom font-medium" scope="col">{{ SKILL_TABLE.colSkill }}</th>
          <th class="min-w-0 px-4 py-3 align-bottom font-medium" scope="col">{{ SKILL_TABLE.colUserFlow }}</th>
          <th class="min-w-0 px-4 py-3 align-bottom font-medium" scope="col">{{ SKILL_TABLE.colExchange }}</th>
          <th class="w-20 px-4 py-3 text-center align-bottom font-medium" scope="col">
            {{ SKILL_TABLE.colEnabled }}
          </th>
        </tr>
      </thead>
      <tbody class="divide-y divide-slate-800/90">
        <UiTableEmptyRow
          v-if="loading || rows.length === 0"
          :colspan="4"
          :loading="loading"
          :filtered="filtered"
          :empty-text="SKILL_TABLE.empty"
        />
        <tr
          v-for="row in rows"
          :key="row.skillId"
          class="cursor-pointer align-middle transition-colors hover:bg-slate-800/35"
          :class="rowClass(row)"
          @click="emit('openDrawer', row.skillId)"
        >
          <td class="px-4 py-3 align-top">
            <div class="mb-1 flex flex-wrap items-center gap-1.5">
              <UiStatChip v-if="skillDomainLabel(row.skillId)" tone="violet">
                {{ skillDomainLabel(row.skillId) }}
              </UiStatChip>
              <span
                class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
                :class="matrixStatusClass(row.matrixStatus)"
              >
                {{ matrixStatusLabel(row.matrixStatus) }}
              </span>
              <span v-if="row.skillSpecVersion" class="text-[11px] text-slate-500">
                {{ SKILL_DRAWER.version(row.skillSpecVersion) }}
              </span>
            </div>
            <p class="text-sm font-medium text-slate-100">{{ row.summary }}</p>
            <p class="mt-0.5 font-mono text-[11px] text-slate-500">{{ row.skillId }}</p>
          </td>
          <td class="min-w-0 px-4 py-3 align-top">
            <p class="line-clamp-3 text-xs leading-relaxed text-slate-400">{{ row.userFlow }}</p>
          </td>
          <td class="min-w-0 px-4 py-3 align-top">
            <p class="line-clamp-3 text-xs leading-relaxed text-slate-400">{{ row.exchangeAction }}</p>
          </td>
          <td class="whitespace-nowrap px-4 py-3 text-center align-middle">
            <UiEnableCheckbox
              :model-value="rowEnabled(row)"
              :aria-label="`${row.summary} 启用`"
              @update:model-value="emit('toggle', row, $event)"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
