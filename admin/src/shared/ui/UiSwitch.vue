<!--
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 运营台统一 Switch 开关（替代 checkbox 视觉 · 对齐 product-doc antd Switch）
-->
<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    modelValue: boolean
    disabled?: boolean
    ariaLabel?: string
    size?: 'sm' | 'md'
  }>(),
  { disabled: false, size: 'md' },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

function onChange(event: Event) {
  emit('update:modelValue', (event.target as HTMLInputElement).checked)
}

const trackSizeClass =
  props.size === 'sm' ? 'h-5 w-9' : 'h-6 w-11'

const thumbSizeClass = props.size === 'sm' ? 'h-4 w-4' : 'h-5 w-5'

const thumbOnClass =
  props.size === 'sm' ? 'group-has-[:checked]:translate-x-4' : 'group-has-[:checked]:translate-x-5'
</script>

<template>
  <label
    class="group relative inline-flex shrink-0 cursor-pointer items-center"
    :class="disabled ? 'cursor-not-allowed opacity-50' : ''"
    @click.stop
  >
    <input
      type="checkbox"
      role="switch"
      class="peer sr-only"
      :checked="modelValue"
      :disabled="disabled"
      :aria-label="ariaLabel"
      @change="onChange"
    />
    <span
      class="relative inline-flex shrink-0 items-center rounded-full border border-slate-600 bg-slate-800 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] transition-[background-color,border-color] duration-200 ease-out group-has-[:checked]:border-emerald-500/55 group-has-[:checked]:bg-emerald-600/90 peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-emerald-500/45"
      :class="trackSizeClass"
      aria-hidden="true"
    >
      <span
        class="pointer-events-none inline-block translate-x-0.5 rounded-full bg-slate-100 shadow-sm transition-transform duration-200 ease-out will-change-transform"
        :class="[thumbSizeClass, thumbOnClass]"
      />
    </span>
  </label>
</template>
