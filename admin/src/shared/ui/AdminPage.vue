<!--
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 文档：`full` 为二三级详情/编辑默认；`form`/`content` 仅用于刻意收窄的页面
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 控制台页面级统一外边距与最大宽度（与 AdminLayout 主内容区配合）
-->
<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    /**
     * full：占满主内容区（默认；列表、详情、编辑器等均应使用）；
     * content：刻意收窄的阅读页（max-w-6xl）；
     * form：刻意收窄的表单页（max-w-5xl；勿用于 `/…/:id` 类二三级路由）；
     * narrow：窄页/演示（如 UI 试跑）
     */
    width?: 'full' | 'content' | 'form' | 'narrow'
    /** 页面内区块纵向间距，默认 6（1.5rem） */
    gap?: '4' | '6' | '8'
  }>(),
  { width: 'full', gap: '6' },
)

const rootClass = computed(() => {
  const gapMap = { '4': 'gap-4', '6': 'gap-6', '8': 'gap-8' } as const
  const widthMap = {
    full: 'w-full',
    content: 'w-full max-w-6xl',
    form: 'w-full max-w-5xl',
    narrow: 'w-full max-w-2xl',
  } as const
  return ['flex w-full flex-col', gapMap[props.gap], widthMap[props.width]]
})
</script>

<template>
  <div :class="rootClass">
    <slot />
  </div>
</template>
