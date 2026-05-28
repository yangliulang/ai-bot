<!--
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 兼容导出 · 内部改为 UiSwitch
作者: Cursor Agent
日期: 2026-05-26
修改功能: 表格行内启用开关 · 与 ConfirmationRules 等页 checkbox 样式一致
-->
<script setup lang="ts">
import UiSwitch from '@/shared/ui/UiSwitch.vue'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    disabled?: boolean
    ariaLabel?: string
  }>(),
  { disabled: false },
)

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>

<template>
  <UiSwitch
    :model-value="props.modelValue"
    :disabled="props.disabled"
    :aria-label="props.ariaLabel"
    size="sm"
    @update:model-value="emit('update:modelValue', $event)"
  />
</template>
