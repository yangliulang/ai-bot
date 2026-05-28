<!--
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 表头 **`创建时间(UTC+8)`** 单行（随顶栏切换为 `(UTC)`）
-->
<script setup lang="ts">
import { computed } from 'vue'

import { adminTimeZoneParenSuffix } from '@/shared/lib/admin-datetime-display'

const suffix = computed(() => adminTimeZoneParenSuffix())
</script>

<template>
  <span class="inline-block whitespace-nowrap normal-case tracking-normal">
    <slot />{{ suffix }}
  </span>
</template>
