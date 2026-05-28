<script setup lang="ts">
import { ref } from 'vue'

import AdminPage from '@/shared/ui/AdminPage.vue'
import { AdminPageHeader, UiButton, UiInput, UiModal } from '@/shared/ui'

const name = ref('')
const modalOpen = ref(false)
const controlledOpen = ref(false)
</script>

<template>
  <AdminPage width="narrow" gap="8">
    <AdminPageHeader title="UI 组件试跑" dev-meta="pageId · sys.ui-playground">
      <template #dev>
        Reka UI 原语 +
        <code class="text-slate-500">shared/ui</code>
        封装 · Tailwind v4
      </template>
    </AdminPageHeader>

    <section class="admin-panel space-y-3 p-6">
      <h2 class="text-sm font-medium text-slate-300">UiButton</h2>
      <div class="flex flex-wrap gap-2">
        <UiButton>Primary</UiButton>
        <UiButton variant="secondary">Secondary</UiButton>
        <UiButton variant="ghost">Ghost</UiButton>
        <UiButton variant="danger">Danger</UiButton>
        <UiButton disabled>Disabled</UiButton>
      </div>
    </section>

    <section class="admin-panel space-y-3 p-6">
      <h2 class="text-sm font-medium text-slate-300">UiInput + Reka Label</h2>
      <UiInput v-model="name" label="展示名称" placeholder="输入文案…" />
      <p class="text-xs text-slate-600">v-model: {{ name || '（空）' }}</p>
    </section>

    <section class="admin-panel space-y-4 p-6">
      <h2 class="text-sm font-medium text-slate-300">UiModal（Dialog）</h2>
      <div class="flex flex-wrap gap-2">
        <UiButton @click="modalOpen = true">程序化打开</UiButton>
      </div>

      <UiModal
        v-model:open="modalOpen"
        title="示例对话框"
        description="基于 Reka UI Dialog，焦点陷阱与 Esc 关闭由库处理。"
      >
        <p class="text-sm text-slate-300">正文槽位：可放表单或说明文案。</p>
        <template #footer>
          <UiButton variant="ghost" @click="modalOpen = false">取消</UiButton>
          <UiButton @click="modalOpen = false">确定</UiButton>
        </template>
      </UiModal>

      <UiModal
        v-model:open="controlledOpen"
        title="带触发器"
        description="Trigger 槽内请放置单个根节点（as-child）。"
      >
        <template #trigger>
          <UiButton variant="secondary">从 Trigger 打开</UiButton>
        </template>
        <p class="text-sm text-slate-300">内容区</p>
      </UiModal>
    </section>
  </AdminPage>
</template>
