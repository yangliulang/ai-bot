<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 控制台页头统一：标题行 + 角标、说明、开发元信息、错误提示；右侧 **actions** 插槽
-->
<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

import { showAdminPageDevMeta } from '@/shared/config/constants'
import {
  ADMIN_PAGE_HEADER_ACTIONS_CLASS,
  ADMIN_PAGE_HEADER_ROOT_CLASS,
  ADMIN_PAGE_HEADER_ROOT_COMPACT_CLASS,
  adminPageHeaderBadgeClass,
  type AdminPageHeaderBadge,
} from '@/shared/ui/admin-page-header'

export type AdminPageHeaderCrumb = {
  label: string
  to?: RouteLocationRaw
}

const props = withDefaults(
  defineProps<{
    title: string
    /** 列表/一级页 `page`；编辑/详情略小 `editor` */
    titleSize?: 'page' | 'editor'
    description?: string
    /** 标题下方等宽字体副标题（如 instanceId） */
    subline?: string
    badges?: AdminPageHeaderBadge[]
    /** 开发元信息整行（`pageId · … · GET …`） */
    devMeta?: string
    /** 页内错误（列表加载失败等） */
    error?: string | null
    density?: 'default' | 'compact'
    crumbs?: AdminPageHeaderCrumb[]
  }>(),
  { titleSize: 'page', density: 'default' },
)

const rootClass = computed(() =>
  props.density === 'compact' ? ADMIN_PAGE_HEADER_ROOT_COMPACT_CLASS : ADMIN_PAGE_HEADER_ROOT_CLASS,
)

const titleClass = computed(() =>
  props.titleSize === 'editor'
    ? 'text-xl font-semibold tracking-tight text-white sm:text-[1.5rem]'
    : 'text-2xl font-semibold tracking-tight text-white',
)

const showDevLine = computed(() => showAdminPageDevMeta && Boolean(props.devMeta?.trim()))
</script>

<template>
  <header :class="rootClass">
    <div class="min-w-0 flex-1 space-y-2">
      <p v-if="crumbs?.length" class="text-xs uppercase tracking-wide text-slate-500">
        <template v-for="(crumb, idx) in crumbs" :key="`${crumb.label}-${idx}`">
          <RouterLink
            v-if="crumb.to"
            class="font-medium text-sky-400/95 underline-offset-4 transition-colors hover:text-sky-300 hover:underline"
            :to="crumb.to"
          >
            {{ crumb.label }}
          </RouterLink>
          <span v-else class="text-slate-400">{{ crumb.label }}</span>
          <span v-if="idx < crumbs.length - 1" class="text-slate-600"> · </span>
        </template>
      </p>

      <slot name="prepend" />

      <div class="flex flex-wrap items-center gap-2">
        <h1 :class="titleClass">{{ title }}</h1>
        <slot name="badges">
          <span
            v-for="(badge, idx) in badges"
            :key="`${badge.label}-${idx}`"
            :class="adminPageHeaderBadgeClass(badge.tone)"
          >
            {{ badge.label }}
          </span>
        </slot>
      </div>

      <p v-if="subline" class="break-all font-mono text-sm text-slate-400">{{ subline }}</p>

      <p v-if="description" class="max-w-3xl text-sm leading-relaxed text-slate-400">
        {{ description }}
      </p>

      <slot name="extra" />

      <p v-if="showDevLine" class="font-mono text-[11px] leading-relaxed text-slate-600">
        <slot name="dev">{{ devMeta }}</slot>
      </p>

      <p v-if="error" class="text-sm text-rose-300/95" role="alert">{{ error }}</p>
    </div>

    <div v-if="$slots.actions" :class="ADMIN_PAGE_HEADER_ACTIONS_CLASS">
      <slot name="actions" />
    </div>
  </header>
</template>
