<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 挂载全局 `AdminToastHost`（操作成功/失败统一提示）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 挂载全局路由顶部 loading 条（懒加载 chunk 首次进入）
-->
<script setup lang="ts">
import { RouterView } from 'vue-router'

import RouteTopLoadingBar from '@/shared/ui/RouteTopLoadingBar.vue'
import AdminToastHost from '@/shared/ui/AdminToastHost.vue'
</script>

<template>
  <RouteTopLoadingBar />
  <AdminToastHost />
  <RouterView />
</template>
