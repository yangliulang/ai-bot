<!--
作者: 杨永的Agent
日期: 2026-05-11
修改功能: 支持可选 errorMessage；standaloneField 与侧向按钮并排时由外行提供 Label；控件高 h-10
-->
<script setup lang="ts">
import { Label } from 'reka-ui'
import { computed, useId } from 'vue'

const model = defineModel<string>({ default: '' })

const props = withDefaults(
  defineProps<{
    /** 关联 Label 文案；无则仅渲染 input */
    label?: string
    type?: string
    placeholder?: string
    autocomplete?: string
    disabled?: boolean
    id?: string
    /** 校验错误；有值时展示辅助文案并高亮边框 */
    errorMessage?: string
    /**
     * 为 true 时不渲染内置 Label — 适用于与相邻按钮同一行并排；须由外行提供可通过 id 关联的文案
     */
    standaloneField?: boolean
  }>(),
  { type: 'text', disabled: false, standaloneField: false },
)

const autoId = useId()
const inputId = computed(() => props.id ?? `ui-input-${autoId}`)
const errorId = computed(() => `${inputId.value}-error`)

const hasError = computed(() => Boolean(props.errorMessage?.trim()))
</script>

<template>
  <div class="w-full">
    <Label
      v-if="label && !standaloneField"
      :for="inputId"
      class="mb-1 block text-xs font-medium"
      :class="hasError ? 'text-rose-300/90' : 'text-slate-400'"
    >
      {{ label }}
    </Label>
    <input
      :id="inputId"
      v-model="model"
      :type="type"
      :placeholder="placeholder"
      :autocomplete="autocomplete"
      :disabled="disabled"
      :aria-invalid="hasError ? true : undefined"
      :aria-describedby="hasError ? errorId : undefined"
      class="box-border h-10 min-h-10 w-full rounded-[var(--radius-ui)] border bg-slate-950 px-3 py-0 text-sm leading-snug text-white [color-scheme:dark] placeholder:text-slate-600 transition-[border-color,box-shadow] duration-200 [transition-timing-function:var(--ease-ui)] focus:outline-none focus:ring-1 disabled:cursor-not-allowed disabled:opacity-50"
      :class="
        hasError
          ? 'border-rose-600 focus:border-rose-500 focus:ring-rose-500/55'
          : 'border-slate-700 focus:border-emerald-600 focus:ring-emerald-600/60'
      "
    />
    <p v-if="hasError" :id="errorId" class="mt-1.5 text-xs text-rose-200/90" role="alert">
      {{ errorMessage }}
    </p>
  </div>
</template>
