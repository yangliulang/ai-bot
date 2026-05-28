<!--
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **渠道列表** 最后一列操作 **`UiTableAction`**（配置/接入图标区分）
-->
<script setup lang="ts">
import { useRouter } from 'vue-router'

import { DEMO_AGENT_CHANNELS, type AgentChannelListRow } from '@/shared/demo/channels-mock'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminPageHeader from '@/shared/ui/AdminPageHeader.vue'
import UiTableAction from '@/shared/ui/UiTableAction.vue'

const router = useRouter()

function statusClass(row: AgentChannelListRow): string {
  if (row.status === 'connected' || row.status === 'enabled') {
    return 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30'
  }
  return 'bg-slate-500/15 text-slate-400 ring-slate-500/30'
}

function onOp(row: AgentChannelListRow) {
  if (row.action === 'onboard') {
    window.alert(`${row.name} 接入流程待开放（演示）`)
    return
  }
  void router.push(`/system/channels/${row.id}`)
}
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="渠道管理"
      description="Runtime Agent 对外渠道接入与状态一览。"
      dev-meta="pageId · sys.channels · 路线图 §1.2 Telegram / Webhook"
    />

    <div class="overflow-x-auto rounded-lg border border-slate-800">
      <table class="min-w-full text-sm">
        <thead class="bg-slate-900/80 text-left text-xs uppercase text-slate-500">
          <tr>
            <th class="px-4 py-3">渠道</th>
            <th class="px-4 py-3">类型</th>
            <th class="px-4 py-3">状态</th>
            <th class="px-4 py-3">规模（演示）</th>
            <th class="px-4 py-3 text-right text-xs font-medium uppercase tracking-wide text-slate-500">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-800">
          <tr v-for="row in DEMO_AGENT_CHANNELS" :key="row.id" class="hover:bg-slate-900/40">
            <td class="px-4 py-3 font-medium text-white">{{ row.name }}</td>
            <td class="px-4 py-3 text-slate-400">{{ row.kindLabel }}</td>
            <td class="px-4 py-3">
              <span
                class="inline-flex rounded-full px-2 py-0.5 text-xs ring-1 ring-inset"
                :class="statusClass(row)"
              >
                {{ row.statusLabel }}
              </span>
            </td>
            <td class="px-4 py-3 text-slate-500">{{ row.userScaleLabel }}</td>
            <td class="px-4 py-3 text-right">
              <UiTableAction
                :variant="row.action === 'onboard' ? 'sky' : 'emerald'"
                :icon="row.action === 'onboard' ? 'arrow-right-circle' : 'cog'"
                @click="onOp(row)"
              >
                {{ row.actionLabel }}
              </UiTableAction>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AdminPage>
</template>
