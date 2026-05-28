<!--
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 404 页
-->
<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <main class="flex min-h-[50dvh] flex-col items-center justify-center px-4 text-center">
    <p class="text-lg font-semibold text-slate-800">页面不存在</p>
    <RouterLink class="mt-4 text-sm font-medium text-emerald-700 hover:text-emerald-600" to="/">
      回首页
    </RouterLink>
  </main>
</template>
