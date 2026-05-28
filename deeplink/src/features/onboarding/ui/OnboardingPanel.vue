<!--
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 面板样式类改为 dl-onboarding-panel（中性前缀）
日期: 2026-05-12
修改功能: closeTo=false 占位、standalone；弹层顶线（对齐 product-doc/Web OnboardingPanel）
-->
<script setup lang="ts">
import { RouterLink } from 'vue-router'

withDefaults(
  defineProps<{
    title: string
    subtitle?: string
    /** 右上角关闭；`false` 时不展示（对齐 product-doc OnboardingPanel） */
    closeTo?: string | false
    wide?: boolean
    tone?: 'default' | 'success'
    standalone?: boolean
  }>(),
  { closeTo: '/', tone: 'default', standalone: false },
)
</script>

<template>
  <div
    class="dl-onboarding-panel"
    :class="[
      wide ? 'dl-onboarding-panel--wide' : '',
      tone === 'success' ? 'dl-onboarding-panel--tone-success' : '',
      standalone ? 'dl-onboarding-panel--standalone' : '',
    ]"
  >
    <div class="dl-onboarding-panel__head">
      <div class="dl-onboarding-panel__title-wrap">
        <h2 class="dl-onboarding-panel__title">{{ title }}</h2>
        <p v-if="subtitle" class="dl-onboarding-panel__subtitle">{{ subtitle }}</p>
      </div>
      <RouterLink
        v-if="closeTo !== false"
        class="dl-onboarding-panel__close"
        :to="(closeTo as string) || '/'"
        aria-label="关闭"
      >
        ×
      </RouterLink>
      <span v-else class="dl-onboarding-panel__close-placeholder" aria-hidden="true" />
    </div>
    <slot />
  </div>
</template>
