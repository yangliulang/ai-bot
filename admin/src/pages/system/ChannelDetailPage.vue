<!--
作者: 杨永的Agent
日期: 2026-05-20
修改功能: Telegram 详情迁至 TelegramChannelDetailPage；本页仅承载其它渠道占位
-->
<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import AdminPage from '@/shared/ui/AdminPage.vue'

const route = useRoute()
const channelId = computed(() => route.params.channelId as string)
</script>

<template>
  <AdminPage>
    <RouterLink
      class="inline-flex items-center gap-2 text-sm text-slate-400 transition-colors duration-200 ease-ui hover:text-emerald-400/95"
      to="/system/channels"
    >
      <span aria-hidden="true" class="text-slate-600">&larr;</span>
      <span>渠道列表</span>
    </RouterLink>

    <div
      class="admin-panel border-dashed border-slate-700/70 px-6 py-14 text-center shadow-none"
    >
      <p class="text-xs font-medium uppercase tracking-wide text-slate-600">Channel</p>
      <p class="mt-2 text-lg font-semibold tracking-tight text-white">{{ channelId }}</p>
      <p class="mx-auto mt-3 max-w-md text-sm leading-relaxed text-slate-500">
        该渠道的接入向导尚未开放；请先完成 Telegram 接入或联系产品对齐路线图。
      </p>
      <RouterLink
        class="mt-6 inline-block text-sm font-medium text-emerald-400/95 hover:underline"
        to="/system/channels/telegram"
      >
        前往 Telegram · Bot 接入
      </RouterLink>
    </div>
  </AdminPage>
</template>
