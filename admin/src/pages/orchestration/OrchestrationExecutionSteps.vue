<!--
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 场景详情 **executionSteps[]** 步骤条（FE_HANDOFF · Phase2 运行编排）
-->
<script setup lang="ts">
import { computed } from 'vue'

import type { AgentExecutionFlowStep } from '@/shared/api/agent-runtime'
import { showAdminPageDevMeta } from '@/shared/config/constants'

const props = defineProps<{
  steps: AgentExecutionFlowStep[]
  loading?: boolean
}>()

const sortedSteps = computed(() =>
  [...props.steps].sort((a, b) => (a.order ?? 0) - (b.order ?? 0)),
)
</script>

<template>
  <div v-if="loading" class="text-xs text-slate-500">加载步骤…</div>
  <p v-else-if="sortedSteps.length === 0" class="text-xs text-slate-500">暂无登记步骤</p>
  <ol v-else class="mt-2 flex flex-col gap-3 sm:flex-row sm:flex-wrap sm:items-start">
    <li
      v-for="(step, index) in sortedSteps"
      :key="step.stepKey"
      class="flex min-w-0 flex-col gap-1 sm:max-w-[11rem]"
    >
      <div class="flex items-center gap-2">
        <span
          class="inline-flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-sky-500/40 bg-sky-500/15 text-[11px] font-semibold text-sky-200"
          aria-hidden="true"
        >
          {{ step.order }}
        </span>
        <span class="text-sm font-medium text-slate-200">{{ step.labelZh }}</span>
        <span
          v-if="index < sortedSteps.length - 1"
          class="hidden shrink-0 text-slate-600 sm:inline"
          aria-hidden="true"
        >
          →
        </span>
      </div>
      <code
        v-if="showAdminPageDevMeta"
        class="ml-8 block truncate font-mono text-[10px] text-slate-500"
      >
        {{ step.stepKey }}
      </code>
    </li>
  </ol>
</template>
