<!--
作者: 杨永的Agent
日期: 2026-05-28
修改功能: 卡片式字段单元 · 适配多列网格布局
作者: 杨永的Agent
日期: 2026-05-28
修改功能: GlobalConfigBundle 单键编辑行（STM/SESSION/READ）
-->
<script setup lang="ts">
import {
  formatMemoryConfigDefault,
  type MemoryRuntimeConfigFieldMeta,
} from '@/features/ai-settings/memory-runtime-config-constants'
import type { TradingAgentConfigValue } from '@/shared/api/admin-trading-agent-config'
import UiSelect from '@/shared/ui/UiSelect.vue'
import UiSwitch from '@/shared/ui/UiSwitch.vue'
import type { UiSelectOption } from '@/shared/ui'

const props = defineProps<{
  field: MemoryRuntimeConfigFieldMeta
  modelValue: TradingAgentConfigValue
  envDefault?: TradingAgentConfigValue
  bundleOverride?: boolean
  dirty?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: TradingAgentConfigValue]
}>()

const numInputClass =
  'box-border h-10 min-h-10 w-full rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 text-sm text-white [color-scheme:dark] outline-none transition-[border-color,box-shadow] duration-200 focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600/60'

function enumOptions(meta: MemoryRuntimeConfigFieldMeta): UiSelectOption[] {
  return (meta.enumOptions ?? []).map((v) => ({ value: v, label: v }))
}

function onNumberInput(ev: Event) {
  const el = ev.target as HTMLInputElement
  if (props.field.kind === 'float') {
    emit('update:modelValue', parseFloat(el.value))
    return
  }
  emit('update:modelValue', parseInt(el.value, 10))
}
</script>

<template>
  <div
    class="flex h-full flex-col space-y-2 rounded-lg border border-slate-800/80 bg-slate-950/35 p-3 transition-[border-color,box-shadow] duration-200 hover:border-slate-700/90"
  >
    <div class="flex flex-wrap items-start justify-between gap-2">
      <span class="min-w-0">
        <span class="block text-sm text-slate-200">{{ field.label }}</span>
        <span class="block font-mono text-[11px] text-slate-500">{{ field.configKey }}</span>
      </span>
      <span class="flex shrink-0 flex-wrap gap-1">
        <span
          v-if="bundleOverride"
          class="rounded border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 font-mono text-[10px] text-emerald-200/90"
        >
          Bundle 覆盖
        </span>
        <span
          v-if="dirty"
          class="rounded border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 font-mono text-[10px] text-amber-100/90"
        >
          未保存
        </span>
      </span>
    </div>
    <p class="text-[11px] leading-relaxed text-slate-500">{{ field.description }}</p>
    <UiSwitch
      v-if="field.kind === 'bool'"
      :model-value="Boolean(modelValue)"
      size="sm"
      :aria-label="field.label"
      @update:model-value="emit('update:modelValue', $event)"
    />
    <UiSelect
      v-else-if="field.kind === 'enum'"
      :model-value="String(modelValue)"
      :options="enumOptions(field)"
      @update:model-value="emit('update:modelValue', $event)"
    />
    <input
      v-else
      :value="modelValue"
      type="number"
      :class="numInputClass"
      :min="field.min"
      :max="field.max"
      :step="field.step ?? (field.kind === 'float' ? 0.01 : 1)"
      @input="onNumberInput"
    />
    <dl class="mt-auto grid gap-2 text-[11px] sm:grid-cols-2">
      <div v-if="envDefault !== undefined">
        <dt class="text-slate-600">Env 默认</dt>
        <dd class="mt-0.5 font-mono text-slate-400">{{ envDefault }}</dd>
      </div>
      <div>
        <dt class="text-slate-600">产品默认</dt>
        <dd class="mt-0.5 font-mono text-slate-500">{{ formatMemoryConfigDefault(field) }}</dd>
      </div>
      <div class="sm:col-span-2">
        <dt class="text-slate-600">环境变量</dt>
        <dd class="mt-0.5 break-all font-mono text-[10px] leading-snug text-emerald-400/85">
          {{ field.envVar }}
        </dd>
      </div>
    </dl>
  </div>
</template>
