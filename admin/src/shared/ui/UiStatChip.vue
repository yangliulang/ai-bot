<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 工具条统计标签（命中 x/y 等），行高与 UiButton size=sm 对齐
-->
<script setup lang="ts">
import { computed } from 'vue'

import { ADMIN_TOOLBAR_CONTROL_H_CLASS } from '@/shared/ui/toolbar-controls'

const props = withDefaults(
  defineProps<{
    /** 语义色调（仅边框/背景/字色，非状态机） */
    tone?: 'neutral' | 'info' | 'success' | 'violet'
  }>(),
  { tone: 'neutral' },
)

const toneClass = computed(() => {
  switch (props.tone) {
    case 'info':
      return 'border-sky-500/35 bg-sky-500/10 text-sky-200'
    case 'success':
      return 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300/95'
    case 'violet':
      return 'border-violet-500/30 bg-violet-500/10 text-violet-200'
    default:
      return 'border-slate-700 bg-slate-900/60 text-slate-400'
  }
})
</script>

<template>
  <span
    :class="[
      'inline-flex shrink-0 items-center justify-center rounded-[var(--radius-ui)] border px-2.5 text-xs font-medium leading-none tabular-nums',
      ADMIN_TOOLBAR_CONTROL_H_CLASS,
      toneClass,
    ]"
  >
    <slot />
  </span>
</template>
