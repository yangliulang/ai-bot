<!--
作者: 杨永的Agent
日期: 2026-05-11
修改功能: size=sm 固定 h-8 与工具条 UiSelect/UiStatChip 对齐；md 为表单行 h-10
-->
<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 视觉变体 */
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'
    /** 原生 button type */
    type?: 'button' | 'submit' | 'reset'
    disabled?: boolean
    /** 请求中：禁用点击并显示加载指示（与 API 类操作配合） */
    loading?: boolean
    /**
     * sm：较矮密排（顶栏次要操作）；md：与 UiInput / UiSelect trigger 对齐的表单行高度
     */
    size?: 'sm' | 'md'
  }>(),
  { variant: 'primary', type: 'button', disabled: false, loading: false, size: 'md' },
)

const emit = defineEmits<{
  click: [e: MouseEvent]
}>()

const variantClass = computed(() => {
  const sizing =
    props.size === 'sm'
      ? 'h-8 min-h-8 shrink-0 px-3 py-0 text-sm leading-none'
      : 'h-10 min-h-10 shrink-0 px-3 py-0 text-sm'
  const base = `inline-flex items-center justify-center gap-2 rounded-[var(--radius-ui)] ${sizing} font-medium transition-[transform,colors,opacity] duration-200 [transition-timing-function:var(--ease-ui)] will-change-transform focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500 active:scale-[0.98] disabled:pointer-events-none disabled:opacity-50 disabled:active:scale-100`
  switch (props.variant) {
    case 'secondary':
      return `${base} border border-slate-600 bg-slate-800 text-slate-100 hover:border-slate-500 hover:bg-slate-700`
    case 'ghost':
      return `${base} text-slate-300 hover:bg-slate-800 hover:text-white`
    case 'danger':
      return `${base} bg-rose-600 text-white hover:bg-rose-500`
    default:
      return `${base} bg-emerald-600 text-white hover:bg-emerald-500`
  }
})

function onClick(e: MouseEvent) {
  emit('click', e)
}
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="variantClass"
    :aria-busy="loading ? true : undefined"
    @click="onClick"
  >
    <span
      v-if="loading"
      class="inline-block size-4 shrink-0 animate-spin rounded-full border-2 border-current border-t-transparent opacity-90"
      aria-hidden="true"
    />
    <slot />
  </button>
</template>
