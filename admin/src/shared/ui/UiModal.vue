<!--
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 内容区 **`fixed inset-0` + flex 视口居中**；动画仅 **`opacity`**，避免 keyframes `transform` 顶掉居中 `translate`
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 打开/关闭缓动动画（`admin-modal-*` + `main.css` @keyframes，兼容 Reka Presence 退场等待）
-->
<script setup lang="ts">
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
  DialogTrigger,
} from 'reka-ui'
import { useSlots } from 'vue'

const open = defineModel<boolean>('open', { default: false })

const props = withDefaults(
  defineProps<{
    title?: string
    description?: string
    /** 无 footer 槽时是否显示默认「关闭」 */
    showDefaultClose?: boolean
  }>(),
  { showDefaultClose: true },
)

const slots = useSlots()
</script>

<template>
  <DialogRoot v-model:open="open">
    <DialogTrigger v-if="slots.trigger" as-child>
      <slot name="trigger" />
    </DialogTrigger>

    <DialogPortal>
      <DialogOverlay class="admin-modal-overlay fixed inset-0 z-50 bg-slate-950/70" />
      <DialogContent
        class="admin-modal-content fixed inset-0 z-50 flex items-center justify-center p-4 outline-none focus:outline-none pointer-events-none"
      >
        <div
          class="pointer-events-auto w-full max-w-lg rounded-[var(--radius-ui-lg)] border border-slate-700 bg-slate-900 p-6 text-slate-100 shadow-xl"
        >
          <DialogTitle v-if="props.title" class="text-lg font-semibold tracking-tight text-white">
            {{ props.title }}
          </DialogTitle>
          <DialogDescription v-if="props.description" class="mt-1 text-sm text-slate-400">
            {{ props.description }}
          </DialogDescription>

          <div class="mt-4">
            <slot />
          </div>

          <div v-if="slots.footer" class="mt-6 flex flex-wrap items-center justify-end gap-2">
            <slot name="footer" />
          </div>

          <div v-else-if="props.showDefaultClose" class="mt-6 flex justify-end">
            <DialogClose
              class="rounded-[var(--radius-ui)] px-3 py-1.5 text-sm font-medium text-slate-300 transition-[transform,colors] duration-200 [transition-timing-function:var(--ease-ui)] hover:bg-slate-800 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald-500 active:scale-[0.98]"
            >
              关闭
            </DialogClose>
          </div>
        </div>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
