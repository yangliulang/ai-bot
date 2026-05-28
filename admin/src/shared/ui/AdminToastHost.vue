<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: Toast 固定 **顶部水平居中** 堆叠（全断点 `items-center`）
作者: 杨永的Agent
日期: 2026-05-22
修改功能: Toast 排版优化：状态图标 + 文案区 + 图标关闭
-->
<script setup lang="ts">
import { adminToastItems, dismissAdminToast } from '@/shared/lib/admin-toast'
import {
  ADMIN_TOAST_TONE_ICON,
  ADMIN_TOAST_TONE_VISUAL,
  adminToastToneLabel,
} from '@/shared/ui/admin-toast-icons'

const iconStroke = {
  fill: 'none',
  stroke: 'currentColor',
  'stroke-width': '1.5',
  'stroke-linecap': 'round',
  'stroke-linejoin': 'round',
} as const
</script>

<template>
  <div
    class="pointer-events-none fixed inset-x-0 top-4 z-[200] flex flex-col items-center gap-2 px-3"
    aria-live="polite"
    aria-relevant="additions"
  >
    <TransitionGroup
      enter-active-class="transition duration-200 [transition-timing-function:var(--ease-ui)]"
      enter-from-class="opacity-0 translate-y-1 scale-[0.98]"
      enter-to-class="opacity-100 translate-y-0 scale-100"
      leave-active-class="transition duration-150 [transition-timing-function:var(--ease-ui)]"
      leave-from-class="opacity-100 translate-y-0 scale-100"
      leave-to-class="opacity-0 -translate-y-1 scale-[0.98]"
      move-class="transition duration-200 [transition-timing-function:var(--ease-ui)]"
    >
      <article
        v-for="t in adminToastItems"
        :key="t.id"
        class="pointer-events-auto flex w-full min-h-11 max-w-[min(100%,22rem)] items-center gap-3 rounded-[var(--radius-ui)] border px-3 py-2.5 backdrop-blur-md"
        :class="ADMIN_TOAST_TONE_VISUAL[t.tone].surface"
        :role="t.tone === 'error' ? 'alert' : 'status'"
        :aria-label="`${adminToastToneLabel(t.tone)}：${t.message}`"
      >
        <span
          class="flex size-8 shrink-0 items-center justify-center rounded-lg"
          :class="[
            ADMIN_TOAST_TONE_VISUAL[t.tone].iconWrap,
            ADMIN_TOAST_TONE_VISUAL[t.tone].iconColor,
          ]"
          aria-hidden="true"
        >
          <svg class="size-[1.125rem]" viewBox="0 0 24 24" v-bind="iconStroke">
            <path
              v-if="ADMIN_TOAST_TONE_ICON[t.tone] === 'check-circle'"
              d="M9 12.75 11.25 14.25 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
            <template v-else-if="ADMIN_TOAST_TONE_ICON[t.tone] === 'x-circle'">
              <path d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5" />
              <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </template>
            <template v-else>
              <path
                d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
              <path d="M12 17.25h.008v.008H12v-.008z" />
            </template>
          </svg>
        </span>

        <p
          class="min-w-0 flex-1 text-sm leading-snug"
          :class="ADMIN_TOAST_TONE_VISUAL[t.tone].message"
        >
          {{ t.message }}
        </p>

        <button
          type="button"
          class="inline-flex size-8 shrink-0 items-center justify-center rounded-md text-slate-500 transition-[transform,colors] duration-200 [transition-timing-function:var(--ease-ui)] hover:bg-slate-800/80 hover:text-slate-200 active:scale-[0.96] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-emerald-500/50"
          aria-label="关闭提示"
          @click="dismissAdminToast(t.id)"
        >
          <svg class="size-4" viewBox="0 0 24 24" v-bind="iconStroke" aria-hidden="true">
            <path d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </article>
    </TransitionGroup>
  </div>
</template>
