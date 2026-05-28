<!--
作者: Cursor Agent
日期: 2026-05-26
修改功能: 技能规范分段内容 · 对齐 product-doc SkillSpecSectionContent
-->
<script setup lang="ts">
import { computed } from 'vue'

import {
  formatConfirmRuleLines,
  formatConfirmRuleTitle,
  type SkillOperationView,
} from '@/entities/tool-registry/parse-skill-operation-view'
import {
  SKILL_SPEC_EMPTY,
  SKILL_SPEC_NOTE,
  SKILL_SPEC_SECTION,
  type SkillSpecSectionKey,
} from '@/entities/tool-registry/tool-registry-copy'

const props = defineProps<{
  section: SkillSpecSectionKey
  view: SkillOperationView
}>()

const title = computed(() => SKILL_SPEC_SECTION[props.section].title)

const table = computed(() => {
  switch (props.section) {
    case 'params':
      return props.view.requiredParams
    case 'validation':
      return props.view.validations
    case 'confirm':
      return props.view.confirmation
    case 'unknown':
      return props.view.unknown
    case 'refusal':
      return props.view.refusals
    default:
      return { headers: [], rows: [] as string[][] }
  }
})

const emptyText = computed(() => SKILL_SPEC_EMPTY[props.section])
</script>

<template>
  <div v-if="section === 'api'" class="admin-skill-op-card admin-panel rounded-lg p-3">
    <h4 class="mb-2 text-sm font-medium text-slate-200">{{ SKILL_SPEC_SECTION.api.title }}</h4>
    <p v-if="!view.apiText?.trim()" class="text-xs text-slate-500">{{ SKILL_SPEC_EMPTY.api }}</p>
    <ul v-else-if="view.apiText.split('\n').filter((l) => /^[-*•]/.test(l.trim())).length >= 2" class="admin-skill-op-api-list space-y-1 text-xs text-slate-300">
      <li v-for="(line, i) in view.apiText.split('\n').filter(Boolean)" :key="i">
        {{ line.replace(/^[-*•]\s*/, '') }}
      </li>
    </ul>
    <pre v-else class="admin-skill-op-api-pre whitespace-pre-wrap text-xs text-slate-300">{{ view.apiText }}</pre>
  </div>

  <div v-else class="admin-skill-op-card admin-panel rounded-lg p-3">
    <div class="mb-2 flex items-center gap-2">
      <h4 class="text-sm font-medium text-slate-200">{{ title }}</h4>
      <span v-if="table.rows.length" class="text-[11px] text-slate-500">{{ table.rows.length }} 条</span>
    </div>

    <template v-if="section === 'confirm'">
      <div v-if="view.confirmRules.length" class="mb-3">
        <p class="mb-1 text-[11px] text-slate-500">{{ SKILL_SPEC_NOTE.orchestration }}</p>
        <ul class="admin-skill-op-rules-list space-y-2 text-xs text-slate-300">
          <li v-for="(rule, i) in view.confirmRules" :key="i">
            <p class="font-medium text-slate-200">{{ formatConfirmRuleTitle(rule.title) }}</p>
            <ul class="mt-1 list-disc space-y-0.5 pl-4 text-slate-400">
              <li v-for="(line, j) in formatConfirmRuleLines(rule.body)" :key="j">{{ line }}</li>
            </ul>
          </li>
        </ul>
      </div>
      <div v-if="table.rows.length" class="overflow-x-auto">
        <table class="admin-skill-op-table w-full min-w-[20rem] border-collapse text-left text-xs">
          <thead>
            <tr class="border-b border-slate-800 text-slate-500">
              <th
                v-for="(h, hi) in table.headers.length ? table.headers : ['项']"
                :key="hi"
                class="px-2 py-1.5 font-medium"
              >
                {{ h || `列${hi + 1}` }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, ri) in table.rows" :key="ri" class="border-b border-slate-800/60">
              <td v-for="(cell, ci) in row" :key="ci" class="px-2 py-1.5 text-slate-300">
                {{ cell ?? '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-xs text-slate-500">{{ SKILL_SPEC_EMPTY.noConfirmFields }}</p>
    </template>

    <template v-else>
      <div v-if="table.rows.length" class="overflow-x-auto">
        <table class="admin-skill-op-table w-full min-w-[20rem] border-collapse text-left text-xs">
          <thead>
            <tr class="border-b border-slate-800 text-slate-500">
              <th
                v-for="(h, hi) in table.headers.length ? table.headers : ['项']"
                :key="hi"
                class="px-2 py-1.5 font-medium"
              >
                {{ h || `列${hi + 1}` }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, ri) in table.rows" :key="ri" class="border-b border-slate-800/60">
              <td v-for="(cell, ci) in row" :key="ci" class="px-2 py-1.5 text-slate-300">
                {{ cell ?? '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <p v-else class="text-xs text-slate-500">{{ emptyText }}</p>
    </template>
  </div>
</template>
