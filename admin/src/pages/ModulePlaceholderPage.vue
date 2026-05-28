<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { showAdminPageDevMeta } from '@/shared/config/constants'
import AdminPage from '@/shared/ui/AdminPage.vue'

const route = useRoute()
const title = computed(() => String(route.meta.title ?? '页面'))
const pageId = computed(() => (route.meta.pageId as string | undefined) ?? '—')
const hint = computed(() => (route.meta.hint as string | undefined) ?? '')
</script>

<template>
  <AdminPage>
  <div class="admin-panel border-dashed border-slate-700/70 px-6 py-12 text-center">
    <h1 class="text-2xl font-semibold tracking-tight text-white">{{ title }}</h1>
    <p v-if="showAdminPageDevMeta" class="mt-2 text-sm text-slate-500">pageId · {{ pageId }}</p>
    <p v-if="hint" class="mx-auto mt-4 max-w-lg text-sm text-slate-400">{{ hint }}</p>
    <p v-else-if="showAdminPageDevMeta" class="mt-4 text-sm text-slate-500">
      该模块将在后续迭代接入契约与联调（参见 admin-console 交付计划）。
    </p>
    <p v-else class="mt-4 text-sm text-slate-500">敬请期待。</p>
  </div>
  </AdminPage>
</template>
