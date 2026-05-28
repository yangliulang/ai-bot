<!--
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 列表「复制」类操作：**copy-to-clipboard 回退** + 成功后 **Teleport 浮动提示**（类 tooltip，不占表头告警位）
-->
<script setup lang="ts">
import { ref } from 'vue'

import { copyTextToClipboard } from '@/shared/utils/copy-to-clipboard'
import UiTableAction from '@/shared/ui/UiTableAction.vue'

const props = withDefaults(
  defineProps<{
    /** 复制到剪贴板的完整文本 */
    text: string
    /** 按钮文案 */
    label?: string
    variant?: 'sky' | 'slate' | 'emerald' | 'rose'
    /** 传给 `UiTableAction` 的额外 class（如 `shrink-0`） */
    buttonClass?: string
  }>(),
  { label: '复制 ID', variant: 'slate' },
)

const popup = ref<{ left: number; top: number; msg: string } | null>(null)
let popupTimer: ReturnType<typeof window.setTimeout> | undefined

async function handleCopy(e: MouseEvent) {
  e.stopPropagation()
  e.preventDefault()

  const ok = await copyTextToClipboard(props.text)
  const msg = ok ? '已复制' : '复制失败'
  const btn = (e.target as Element | null)?.closest?.('button') as HTMLButtonElement | null
  const rect = btn?.getBoundingClientRect()
  if (rect && typeof window !== 'undefined') {
    popup.value = {
      left: rect.left + rect.width / 2,
      /** `fixed`：使用视口坐标 */
      top: rect.top,
      msg,
    }
  } else if (typeof window !== 'undefined') {
    popup.value = { left: window.innerWidth / 2, top: 80, msg }
  } else {
    popup.value = { left: 0, top: 0, msg }
  }

  if (popupTimer) window.clearTimeout(popupTimer)
  popupTimer = window.setTimeout(() => {
    popup.value = null
  }, 2200)
}
</script>

<template>
  <span class="relative inline-flex">
    <UiTableAction
      :variant="variant"
      icon="clipboard"
      type="button"
      :class="buttonClass"
      @click="handleCopy"
    >
      {{ label }}
    </UiTableAction>

    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-150 ease-out"
        enter-from-class="opacity-0"
        leave-active-class="transition-opacity duration-150 ease-out"
        leave-to-class="opacity-0"
      >
        <div
          v-if="popup"
          role="status"
          aria-live="polite"
          class="pointer-events-none fixed z-[9999] rounded-md border border-slate-600/90 bg-slate-900/98 px-2.5 py-1 text-[11px] font-medium whitespace-nowrap text-slate-100 shadow-lg backdrop-blur-[2px]"
          :style="{
            left: `${popup.left}px`,
            top: `${popup.top - 10}px`,
            transform: 'translate(-50%, -100%)',
          }"
        >
          {{ popup.msg }}
        </div>
      </Transition>
    </Teleport>
  </span>
</template>
