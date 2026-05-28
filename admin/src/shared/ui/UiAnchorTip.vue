<!--
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 锚定控件上方的浮动提示（Teleport tooltip），供保存等操作成功反馈
-->
<script setup lang="ts">
import { ref } from 'vue'

const props = withDefaults(
  defineProps<{
    /** 提示视觉：success 用于保存成功等正向反馈 */
    tone?: 'neutral' | 'success'
    /** 自动消失毫秒 */
    durationMs?: number
  }>(),
  { tone: 'neutral', durationMs: 2200 },
)

const wrapperRef = ref<HTMLElement | null>(null)
const popup = ref<{ left: number; top: number; msg: string } | null>(null)
let popupTimer: ReturnType<typeof window.setTimeout> | undefined

function resolveAnchor(): HTMLElement | null {
  const root = wrapperRef.value
  if (!root) return null
  const btn = root.querySelector('button')
  return (btn as HTMLElement | null) ?? root
}

function show(msg: string, anchor?: HTMLElement | null) {
  const el = anchor ?? resolveAnchor()
  const rect = el?.getBoundingClientRect()
  if (rect && typeof window !== 'undefined') {
    popup.value = {
      left: rect.left + rect.width / 2,
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
  }, props.durationMs)
}

defineExpose({ show })
</script>

<template>
  <span ref="wrapperRef" class="relative inline-flex">
    <slot />

    <Teleport to="body">
      <Transition
        enter-active-class="transition-[opacity,transform] duration-150 ease-out"
        enter-from-class="opacity-0 translate-y-1"
        leave-active-class="transition-opacity duration-150 ease-out"
        leave-to-class="opacity-0"
      >
        <div
          v-if="popup"
          role="status"
          aria-live="polite"
          class="pointer-events-none fixed z-[9999] rounded-md px-2.5 py-1 text-[11px] font-medium whitespace-nowrap shadow-lg backdrop-blur-[2px]"
          :class="
            tone === 'success'
              ? 'border border-emerald-500/50 bg-slate-900/98 text-emerald-100'
              : 'border border-slate-600/90 bg-slate-900/98 text-slate-100'
          "
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
