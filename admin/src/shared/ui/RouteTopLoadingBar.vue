<!--
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 顶部全局路由懒加载进度条（首次进入路由显示，chunk 缓存后不再显示）
-->
<script setup lang="ts">
import { computed } from 'vue'

import {
  routeTopLoadingProgress,
  routeTopLoadingVisible,
} from '@/shared/lib/route-top-loading'

const barScale = computed(() => Math.max(0, Math.min(1, routeTopLoadingProgress.value / 100)))
</script>

<template>
  <div
    v-show="routeTopLoadingVisible"
    class="route-top-loading pointer-events-none fixed inset-x-0 top-0 z-[60] h-[2px]"
    role="progressbar"
    aria-live="polite"
    aria-valuemin="0"
    aria-valuemax="100"
    :aria-valuenow="routeTopLoadingProgress"
    aria-label="页面加载中"
  >
    <div
      class="route-top-loading__track h-full origin-left bg-emerald-400/95 will-change-transform"
      :style="{ transform: `scaleX(${barScale})` }"
    />
  </div>
</template>

<style scoped>
.route-top-loading__track {
  box-shadow:
    0 0 12px rgb(52 211 153 / 0.45),
    inset 0 1px 0 rgb(255 255 255 / 0.12);
  transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1);
}
</style>
