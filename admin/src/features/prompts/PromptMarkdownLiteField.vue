<!--
作者: 杨永的Agent
日期: 2026-05-19
修改功能: Markdown Lite 源码/预览编辑器（对齐 product-doc PromptMarkdownLiteField）
-->
<script setup lang="ts">
import { computed, nextTick, ref, useId } from 'vue'

import {
  markdownLiteInsertPrefixAtLogicalLineHead,
  markdownLiteWrapSelection,
} from '@/shared/lib/markdown-lite-edit'
import { markdownLiteToPreviewHtml } from '@/shared/lib/markdown-lite-preview-html'

const props = withDefaults(
  defineProps<{
    modelValue: string
    disabled?: boolean
    minEditorHeightPx?: number
  }>(),
  { disabled: false, minEditorHeightPx: 380 },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const mode = ref<'edit' | 'preview'>('edit')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const textareaId = useId()

const previewHtml = computed(() => markdownLiteToPreviewHtml(props.modelValue))

function applyEdit(next: string, start: number, end: number) {
  emit('update:modelValue', next)
  void nextTick(() => {
    const el = textareaRef.value
    if (!el) return
    el.focus()
    el.setSelectionRange(start, end)
  })
}

function withSelection(fn: (value: string, start: number, end: number) => { next: string; focusStart: number; focusEnd: number }) {
  const el = textareaRef.value
  if (!el || props.disabled) return
  const { selectionStart: s, selectionEnd: e } = el
  const { next, focusStart, focusEnd } = fn(props.modelValue, s, e)
  applyEdit(next, focusStart, focusEnd)
}

function onBold() {
  withSelection((v, s, e) => markdownLiteWrapSelection(v, s, e, '**', '**', '加粗文案'))
}

function onItalic() {
  withSelection((v, s, e) => markdownLiteWrapSelection(v, s, e, '*', '*', '倾斜文案'))
}

function onH2() {
  const el = textareaRef.value
  if (!el || props.disabled) return
  const { next, focus } = markdownLiteInsertPrefixAtLogicalLineHead(props.modelValue, el.selectionStart, '## ')
  applyEdit(next, focus, focus)
}

function onBullet() {
  const el = textareaRef.value
  if (!el || props.disabled) return
  const { next, focus } = markdownLiteInsertPrefixAtLogicalLineHead(props.modelValue, el.selectionStart, '- ')
  applyEdit(next, focus, focus)
}

function onOrdered() {
  const el = textareaRef.value
  if (!el || props.disabled) return
  const { next, focus } = markdownLiteInsertPrefixAtLogicalLineHead(props.modelValue, el.selectionStart, '1. ')
  applyEdit(next, focus, focus)
}

function onFence() {
  withSelection((v, s, e) => markdownLiteWrapSelection(v, s, e, '```\n', '\n```\n', '// 占位说明'))
}
</script>

<template>
  <div class="space-y-2.5">
    <div class="flex flex-wrap items-center justify-between gap-2">
      <div class="flex flex-wrap gap-1">
        <button
          type="button"
          class="rounded-md border border-slate-700/80 bg-slate-900/60 px-2 py-1 text-xs font-semibold text-slate-300 transition-colors hover:border-slate-600 hover:text-white disabled:opacity-40"
          title="加粗"
          :disabled="disabled"
          @click="onBold"
        >
          B
        </button>
        <button
          type="button"
          class="rounded-md border border-slate-700/80 bg-slate-900/60 px-2 py-1 text-xs italic text-slate-300 transition-colors hover:border-slate-600 hover:text-white disabled:opacity-40"
          title="倾斜"
          :disabled="disabled"
          @click="onItalic"
        >
          I
        </button>
        <button
          type="button"
          class="rounded-md border border-slate-700/80 bg-slate-900/60 px-2 py-1 text-xs text-slate-300 transition-colors hover:border-slate-600 hover:text-white disabled:opacity-40"
          title="二级标题"
          :disabled="disabled"
          @click="onH2"
        >
          H2
        </button>
        <button
          type="button"
          class="rounded-md border border-slate-700/80 bg-slate-900/60 px-2 py-1 text-xs text-slate-300 transition-colors hover:border-slate-600 hover:text-white disabled:opacity-40"
          title="无序列表"
          :disabled="disabled"
          @click="onBullet"
        >
          UL
        </button>
        <button
          type="button"
          class="rounded-md border border-slate-700/80 bg-slate-900/60 px-2 py-1 text-xs text-slate-300 transition-colors hover:border-slate-600 hover:text-white disabled:opacity-40"
          title="有序列表"
          :disabled="disabled"
          @click="onOrdered"
        >
          OL
        </button>
        <button
          type="button"
          class="rounded-md border border-slate-700/80 bg-slate-900/60 px-2 py-1 font-mono text-xs text-slate-300 transition-colors hover:border-slate-600 hover:text-white disabled:opacity-40"
          title="围栏代码块"
          :disabled="disabled"
          @click="onFence"
        >
          {}
        </button>
      </div>
      <div
        class="inline-flex rounded-md border border-slate-700/80 bg-slate-900/50 p-0.5 text-xs"
        role="tablist"
        aria-label="编辑模式"
      >
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'edit'"
          class="rounded px-2.5 py-1 transition-colors"
          :class="mode === 'edit' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'"
          :disabled="disabled"
          @click="mode = 'edit'"
        >
          源码
        </button>
        <button
          type="button"
          role="tab"
          :aria-selected="mode === 'preview'"
          class="rounded px-2.5 py-1 transition-colors"
          :class="mode === 'preview' ? 'bg-slate-700 text-white' : 'text-slate-400 hover:text-slate-200'"
          @click="mode = 'preview'"
        >
          预览
        </button>
      </div>
    </div>

    <textarea
      v-show="mode === 'edit'"
      :id="textareaId"
      ref="textareaRef"
      :value="modelValue"
      :disabled="disabled"
      spellcheck="false"
      aria-label="Prompt Markdown 源码"
      placeholder="# Spot trading system prompt&#10;&#10;## 规则&#10;- 条目一"
      class="box-border w-full resize-y rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2.5 font-mono text-[13px] leading-relaxed text-slate-200 [color-scheme:dark] transition-[border-color] duration-200 ease-ui focus:border-emerald-600 focus:outline-none focus:ring-1 focus:ring-emerald-600/45 disabled:cursor-not-allowed disabled:opacity-60"
      :style="{ minHeight: `${minEditorHeightPx}px` }"
      @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
    />

    <div
      v-show="mode === 'preview'"
      class="prompt-markdown-lite-preview min-h-[20rem] max-h-[32rem] overflow-auto rounded-[var(--radius-ui)] border border-slate-800/90 bg-slate-950/50 px-3.5 py-3 text-[13px] leading-relaxed text-slate-200"
      aria-live="polite"
    >
      <div v-if="previewHtml" class="prompt-markdown-lite-preview__body" v-html="previewHtml" />
      <p v-else class="text-sm text-slate-500">暂无内容 · 切换到「源码」开始编写</p>
    </div>
  </div>
</template>

<style scoped>
.prompt-markdown-lite-preview__body :deep(h1),
.prompt-markdown-lite-preview__body :deep(h2),
.prompt-markdown-lite-preview__body :deep(h3) {
  margin: 0.9em 0 0.45em;
  font-weight: 600;
  color: rgb(241 245 249);
}
.prompt-markdown-lite-preview__body :deep(h1) {
  font-size: 1.25em;
}
.prompt-markdown-lite-preview__body :deep(h2) {
  font-size: 1.15em;
}
.prompt-markdown-lite-preview__body :deep(h3) {
  font-size: 1.05em;
}
.prompt-markdown-lite-preview__body :deep(p) {
  margin: 0.55em 0;
  color: rgb(203 213 225);
}
.prompt-markdown-lite-preview__body :deep(ul),
.prompt-markdown-lite-preview__body :deep(ol) {
  margin: 0.55em 0;
  padding-left: 1.35em;
}
.prompt-markdown-lite-preview__body :deep(code) {
  padding: 1px 5px;
  border-radius: 4px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 0.92em;
  background: rgb(30 41 59 / 0.8);
}
.prompt-markdown-lite-preview__body :deep(pre) {
  margin: 0.65em 0;
  padding: 10px 12px;
  overflow: auto;
  border-radius: 8px;
  background: rgb(15 23 42 / 0.85);
  border: 1px solid rgb(51 65 85 / 0.6);
}
.prompt-markdown-lite-preview__body :deep(pre code) {
  padding: 0;
  background: transparent;
  font-size: 12px;
}
.prompt-markdown-lite-preview__body :deep(strong) {
  font-weight: 600;
  color: rgb(226 232 240);
}
</style>
