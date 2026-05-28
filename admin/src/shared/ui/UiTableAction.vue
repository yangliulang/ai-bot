<!--
作者: 杨永的Agent
日期: 2026-05-15
修改功能: **button** 模式 **click** 先于 **emit** 调 **`stopPropagation`**，避免表格行 **click** 抢走手势/焦点
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 列表行内操作：图标 + 文案的紧凑 outline 控件；button / RouterLink 单模板渲染避免重复
-->
<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { RouteLocationRaw } from 'vue-router'

const props = withDefaults(
  defineProps<{
    variant?: 'sky' | 'slate' | 'emerald' | 'rose'
    /** 传入时渲染为 RouterLink */
    to?: RouteLocationRaw
    type?: 'button' | 'submit'
    disabled?: boolean
    /** 仅 button 模式：请求中展示加载指示并禁用 */
    loading?: boolean
    /**
     * 预设线性图标（currentColor，1.5px 描边）
     * trending-up：健康 / 探针类操作
     */
    icon?:
      | 'eye'
      | 'clipboard'
      | 'file-text'
      | 'trash'
      | 'clock'
      | 'list'
      | 'search'
      | 'cog'
      | 'arrow-right-circle'
      | 'check'
      | 'arrow-path'
      | 'trending-up'
  }>(),
  { variant: 'slate', type: 'button', disabled: false, loading: false },
)

const emit = defineEmits<{ click: [e: MouseEvent] }>()

const variantClass = computed(() => {
  switch (props.variant) {
    case 'sky':
      return 'border-slate-600/70 bg-slate-900/55 text-sky-400 hover:border-slate-500 hover:bg-slate-800 hover:text-sky-300'
    case 'emerald':
      return 'border-slate-600/70 bg-slate-900/55 text-emerald-400 hover:border-slate-500 hover:bg-slate-800 hover:text-emerald-300'
    case 'rose':
      return 'border-rose-500/35 bg-rose-950/25 text-rose-400 hover:border-rose-400/45 hover:bg-rose-950/45 hover:text-rose-300'
    default:
      return 'border-slate-600/70 bg-slate-900/40 text-slate-400 hover:border-slate-500 hover:bg-slate-800 hover:text-slate-200'
  }
})

const baseClass =
  'inline-flex max-w-full items-center justify-center gap-1 rounded-md border px-2 py-0.5 text-[11px] font-medium leading-tight transition-[transform,colors,border-color] duration-200 [transition-timing-function:var(--ease-ui)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-emerald-500/60 active:scale-[0.98] disabled:pointer-events-none disabled:opacity-45'

const mergedClass = computed(() => [baseClass, variantClass.value])

const isLink = computed(() => props.to !== undefined)

const rootIs = computed(() => (isLink.value ? RouterLink : 'button'))

const rootBind = computed(() => {
  if (isLink.value) return { to: props.to! }
  return { type: props.type, disabled: props.disabled || props.loading }
})

function onRootClick(e: MouseEvent) {
  if (!isLink.value) {
    e.stopPropagation()
    emit('click', e)
  }
}
</script>

<template>
  <component :is="rootIs" v-bind="rootBind" :class="mergedClass" @click="onRootClick">
    <span
      v-if="loading && !isLink"
      class="inline-block size-3.5 shrink-0 animate-spin rounded-full border-2 border-current border-t-transparent opacity-90"
      aria-hidden="true"
    />
    <span
      v-else-if="icon"
      class="size-3.5 shrink-0 text-current [&>svg]:h-3.5 [&>svg]:w-3.5"
      aria-hidden="true"
    >
      <svg
        v-if="icon === 'eye'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z"
        />
        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <svg
        v-else-if="icon === 'clipboard'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"
        />
      </svg>
      <svg
        v-else-if="icon === 'file-text'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <svg
        v-else-if="icon === 'trash'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0"
        />
      </svg>
      <svg
        v-else-if="icon === 'clock'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <svg
        v-else-if="icon === 'list'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75zm0 5.25h.007v.008H3.75v-.008zm0 5.25h.007v.008H3.75v-.008z" />
      </svg>
      <svg
        v-else-if="icon === 'search'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
      </svg>
      <svg
        v-else-if="icon === 'cog'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M9.594 3.94c.09-.542.56-.94 1.11-.94h2.593c.55 0 1.02.398 1.11.94l.213 1.281c.063.374.313.686.645.87.074.04.147.083.22.127.324.196.72.257 1.075.124l1.217-.456a1.125 1.125 0 011.37.49l1.296 2.247a1.125 1.125 0 01-.26 1.431l-1.003.827c-.293.24-.438.613-.391.992a12.082 12.082 0 010 .255c-.047.378.098.75.392.991l1.004.827c.424.35.534.954.26 1.43l-1.298 2.247a1.125 1.125 0 01-1.369.491l-1.217-.456c-.355-.133-.75-.072-1.076.124a6.576 6.576 0 01-.218.138c-.33.178-.579.489-.642.855l-.213 1.28c-.09.544-.563.943-1.11.943h-2.594c-.549 0-1.019-.398-1.11-.943l-.212-1.281c-.062-.376-.314-.689-.642-.867a8.088 8.088 0 01-.217-.147c-.34-.207-.743-.274-1.085-.169l-1.25.466a1.125 1.125 0 01-1.369-.49l-1.297-2.247a1.125 1.125 0 01.261-1.431l1.004-.827c.292-.249.442-.627.389-1.006a13.734 13.734 0 010-.255c.053-.374-.096-.75-.388-.992l-1.004-.827a1.125 1.125 0 01-.263-1.432l1.299-2.246a1.125 1.125 0 011.37-.491l1.217.456c.356.133.751.072 1.076-.124.072-.044.146-.087.22-.128.332-.183.582-.495.644-.869l.214-1.281z"
        />
        <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
      <svg
        v-else-if="icon === 'arrow-right-circle'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M12 21a9 9 0 100-18 9 9 0 000 18z" />
        <path d="M13.5 8.25L19.5 12l-6 3.75m6-3.75H4.5" />
      </svg>
      <svg
        v-else-if="icon === 'check'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <svg
        v-else-if="icon === 'arrow-path'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.993m0 0 3.181 3.183a8.25 8.25 0 002.637.463 8.259 8.259 0 007.956-8.957V9.348M4.031 9.865a8.259 8.259 0 0013.803 3.7l4.993-5.943" />
      </svg>
      <svg
        v-else-if="icon === 'trending-up'"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M3 13l5-5 4 4L21 8M21 8v6M21 8h-6" />
      </svg>
    </span>
    <span class="truncate"><slot /></span>
  </component>
</template>
