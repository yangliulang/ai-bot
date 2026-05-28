<!--
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 执行详情线型 Tab（对齐 product-doc Ant Tabs 信息架构）
-->
<script setup lang="ts">
export type AdminDetailTabItem = {
  key: string
  label: string
}

defineProps<{
  tabs: AdminDetailTabItem[]
  activeKey: string
}>()

const emit = defineEmits<{
  'update:activeKey': [key: string]
}>()
</script>

<template>
  <nav
    class="admin-detail-tabs -mb-px flex flex-wrap gap-0 border-b border-slate-800"
    role="tablist"
    aria-label="执行详情"
  >
    <button
      v-for="t in tabs"
      :key="t.key"
      type="button"
      role="tab"
      :aria-selected="activeKey === t.key"
      class="admin-detail-tab -mb-px border-b-2 px-4 py-2.5 text-sm font-medium transition-colors duration-200 ease-ui"
      :class="
        activeKey === t.key
          ? 'border-emerald-500 text-white'
          : 'border-transparent text-slate-500 hover:border-slate-600 hover:text-slate-300'
      "
      @click="emit('update:activeKey', t.key)"
    >
      {{ t.label }}
    </button>
  </nav>
</template>
