<!--
作者: 杨永的Agent
日期: 2026-05-14
修改功能: **FR-AM-G01** 只读横幅（**`GET …/global-agent-gate`** · ≤30s 轮询 · UTC 当日收纳）
-->
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

import { getGlobalAgentGate, type GlobalAgentGateResponse } from '@/shared/api/agent-agent-control'

const STORAGE_KEY = 'chainup-admin-g01-banner-dismiss-utc'

function utcCalendarDay(): string {
  return new Date().toISOString().slice(0, 10)
}

function loadDismissedFlag(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === utcCalendarDay()
  } catch {
    return false
  }
}

function persistDismissToday() {
  try {
    localStorage.setItem(STORAGE_KEY, utcCalendarDay())
  } catch {
    /* ignore */
  }
}

const gate = ref<GlobalAgentGateResponse | null>(null)
const pollErr = ref(false)
const dismissedToday = ref(false)

let timer: ReturnType<typeof setInterval> | null = null

async function refresh() {
  try {
    gate.value = await getGlobalAgentGate()
    pollErr.value = false
  } catch {
    pollErr.value = true
  }
}

const visible = computed(() => {
  if (dismissedToday.value) return false
  const g = gate.value
  if (!g) return false
  return !g.globalAgentSwitchOn || g.opsSuspended
})

const bannerText = computed(() => {
  const g = gate.value
  if (!g) return ''
  const hint = g.bannerMessage?.trim()
  if (hint) return hint
  if (!g.globalAgentSwitchOn) return 'GLOBAL_AGENT_SWITCH 关闭（G01）：Start / Resume 不可用。'
  if (g.opsSuspended) return '运维全局暂停（OPS_SUSPENDED）。'
  return '全局门禁需要关注。'
})

function onDismissToday() {
  persistDismissToday()
  dismissedToday.value = true
}

onMounted(() => {
  dismissedToday.value = loadDismissedFlag()
  void refresh()
  timer = setInterval(refresh, 30_000)
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div
    v-if="visible"
    class="rounded-lg border border-rose-500/35 bg-rose-950/40 px-4 py-3 text-sm text-rose-100"
    role="status"
  >
    <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
      <div class="min-w-0">
        <p class="font-semibold text-rose-50">全局门禁（G01）</p>
        <p class="mt-1 leading-relaxed text-rose-100/95">{{ bannerText }}</p>
        <p v-if="gate?.reasonCodes?.length" class="mt-2 font-mono text-xs text-rose-200/80">
          {{ gate.reasonCodes.join(', ') }}
        </p>
        <p v-if="pollErr" class="mt-2 text-xs text-rose-300/90">
          横幅状态轮询失败，仍以最近一次成功结果为准。
        </p>
      </div>
      <button
        type="button"
        class="shrink-0 rounded-md border border-rose-400/40 px-3 py-1.5 text-xs font-medium text-rose-100 transition-colors hover:bg-rose-500/15"
        @click="onDismissToday"
      >
        今日不再显示
      </button>
    </div>
  </div>
</template>
