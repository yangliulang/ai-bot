<!--
作者: 杨永的Agent
日期: 2026-05-11
修改功能: size=sm（h-8）供工具条分页等与 UiButton sm 对齐；md 与 UiInput 表单行 h-10
-->
<script lang="ts">
/** 下拉选项（`value` 不可为 `''`，与 Reka Select 约束一致；“全部”类选项请用 `__all__` 等哨兵） */
export interface UiSelectOption {
  value: string
  label: string
  disabled?: boolean
}
</script>

<script setup lang="ts">
import { Label } from 'reka-ui'
import {
  SelectContent,
  SelectIcon,
  SelectItem,
  SelectItemText,
  SelectPortal,
  SelectRoot,
  SelectTrigger,
  SelectValue,
  SelectViewport,
} from 'reka-ui'
import { computed, useId } from 'vue'

const model = defineModel<string>({ required: true })

const props = withDefaults(
  defineProps<{
    label?: string
    placeholder?: string
    options: UiSelectOption[]
    disabled?: boolean
    id?: string
    /** sm：工具条分页等；md：表单行（默认） */
    size?: 'sm' | 'md'
  }>(),
  { placeholder: '请选择', disabled: false, size: 'md' },
)

const autoId = useId()
const controlId = computed(() => props.id ?? `ui-select-${autoId}`)

const triggerSizeClass = computed(() =>
  props.size === 'sm' ? 'h-8 min-h-8 px-2.5 text-sm leading-none' : 'h-10 min-h-10 px-3 text-sm',
)

const triggerClass = computed(
  () =>
    `flex w-full items-center justify-between gap-2 rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 py-0 text-left text-white outline-none transition-[transform,colors,border-color,box-shadow] duration-200 [transition-timing-function:var(--ease-ui)] will-change-transform hover:border-slate-600 focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600/60 active:scale-[0.98] data-[disabled]:cursor-not-allowed data-[disabled]:opacity-50 data-[disabled]:active:scale-100 data-[placeholder]:text-slate-500 ${triggerSizeClass.value}`,
)

const contentClass =
  'z-[100] max-h-64 min-w-[var(--reka-select-trigger-width)] overflow-hidden rounded-[var(--radius-ui)] border border-slate-700 bg-slate-900 py-1 text-sm shadow-lg outline-none'

const itemClass =
  'relative flex cursor-pointer select-none items-center rounded-sm py-2 pl-2 pr-8 text-slate-200 outline-none data-[disabled]:pointer-events-none data-[highlighted]:bg-slate-800 data-[highlighted]:text-white data-[state=checked]:text-emerald-400'
</script>

<template>
  <div class="w-full">
    <Label v-if="label" :for="controlId" class="mb-1 block text-xs font-medium text-slate-400">
      {{ label }}
    </Label>
    <SelectRoot v-model="model" :disabled="disabled">
      <SelectTrigger :id="controlId" :class="triggerClass">
        <SelectValue :placeholder="placeholder" />
        <SelectIcon class="text-slate-500">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
            class="h-4 w-4"
            aria-hidden="true"
          >
            <path
              fill-rule="evenodd"
              d="M5.23 7.21a.75.75 0 0 1 1.06.02L10 11.168l3.71-3.938a.75.75 0 1 1 1.08 1.04l-4.25 4.5a.75.75 0 0 1-1.08 0l-4.25-4.5a.75.75 0 0 1 .02-1.06Z"
              clip-rule="evenodd"
            />
          </svg>
        </SelectIcon>
      </SelectTrigger>
      <SelectPortal>
        <SelectContent :class="contentClass" position="popper" :side-offset="4">
          <SelectViewport class="p-1">
            <SelectItem
              v-for="opt in options"
              :key="opt.value"
              :value="opt.value"
              :disabled="opt.disabled"
              :class="itemClass"
            >
              <SelectItemText>{{ opt.label }}</SelectItemText>
            </SelectItem>
          </SelectViewport>
        </SelectContent>
      </SelectPortal>
    </SelectRoot>
  </div>
</template>
