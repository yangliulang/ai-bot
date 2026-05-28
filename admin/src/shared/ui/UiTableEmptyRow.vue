<!--
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 列表表格统一空态/加载态行（表内居中、可配筛选说明与操作 slot）
-->
<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    colspan: number
    state?: 'loading' | 'empty' | 'filtered'
    title?: string
    description?: string
  }>(),
  { state: 'empty' },
)

const displayTitle = computed(() => {
  if (props.title) return props.title
  if (props.state === 'loading') return '加载中…'
  if (props.state === 'filtered') return '暂无匹配数据'
  return '暂无数据'
})

const displayDescription = computed(() => {
  if (props.description !== undefined) return props.description
  if (props.state === 'filtered') return '可尝试放宽或重置筛选条件。'
  return ''
})
</script>

<template>
  <tr class="bg-slate-950/40">
    <td :colspan="colspan" class="p-0 align-middle">
      <div
        class="flex min-h-[10rem] w-full flex-col items-center justify-center gap-3 px-6 py-10 text-center"
        :aria-busy="state === 'loading' ? true : undefined"
      >
        <div v-if="state === 'loading'" class="w-full max-w-xs space-y-2">
          <div class="h-2.5 animate-pulse rounded-md bg-slate-800/90" />
          <div class="h-2.5 w-4/5 animate-pulse rounded-md bg-slate-800/70" />
          <p class="pt-1 text-xs text-slate-500">{{ displayTitle }}</p>
        </div>
        <template v-else>
          <p class="text-sm font-medium text-slate-400">{{ displayTitle }}</p>
          <p
            v-if="displayDescription"
            class="max-w-md text-xs leading-relaxed text-slate-500"
          >
            {{ displayDescription }}
          </p>
          <div v-if="$slots.default" class="flex flex-wrap items-center justify-center gap-2">
            <slot />
          </div>
        </template>
      </div>
    </td>
  </tr>
</template>
