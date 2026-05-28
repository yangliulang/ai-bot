<!--
作者: 杨永的Agent
日期: 2026-05-21
修改功能: 「Prompt 名称」只读框展示 **`detail.title`** · scenarioId 副文案（FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 接 BE 编辑器 API：版本履历 · 回滚 · LOCKED fork · If-Match 保存
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 修复模板内 `{{name}}` 示例文案的 Vue 插值嵌套引号编译错误
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 全页对齐产品原型：双栏布局 · Markdown Lite · 版本与发布侧栏 · 脏检查/⌘S
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 编辑页 AdminPage 全宽
作者: 杨永的Agent
日期: 2026-05-18
修改功能: /prompts/editor/:promptPackId 独立 Prompt 正文编辑页
-->
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import PromptMarkdownLiteField from '@/features/prompts/PromptMarkdownLiteField.vue'
import { PHASE1_PLATFORM_PROMPT_PLACEHOLDER_EXAMPLES } from '@/shared/copy/prompt-platform-placeholders'
import { promptGovernancePublicationLabel } from '@/shared/lib/prompt-editor-messages'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminPageHeader from '@/shared/ui/AdminPageHeader.vue'
import UiButton from '@/shared/ui/UiButton.vue'
import UiInput from '@/shared/ui/UiInput.vue'
import UiModal from '@/shared/ui/UiModal.vue'
import { usePromptPackEditor } from '@/pages/prompts/usePromptPackEditor'

const route = useRoute()
const router = useRouter()

/** 文档示例占位符（勿在模板写 `{{ '{{…}}' }}`，会与 Vue 插值冲突） */
const DOC_PLACEHOLDER_EXAMPLE = '{{ name }}'

function formatPlaceholderToken(key: string): string {
  return `{{${key}}}`
}

const promptPackId = computed(() => {
  const p = route.params.promptPackId
  const raw = Array.isArray(p) ? p[0] : p
  return typeof raw === 'string' ? raw.trim() : ''
})

const {
  detail,
  detailLoading,
  detailError,
  packTitle,
  bodyMarkdown,
  variableSchemaRaw,
  variableSchemaValidation,
  detailLifecycleUpper,
  detailIsDraft,
  canEditBody,
  dirty,
  tokenApprox,
  placeholderKeys,
  saveDraftDisabled,
  saveLoading,
  saveError,
  versionHistory,
  versionsLoading,
  versionsError,
  canRollback,
  publishLoading,
  publishError,
  rollbackLoading,
  rollbackError,
  forkLoading,
  forkError,
  formatPromptPackAt,
  validatePublishForConfirm,
  revertWorkbench,
  formatVariableSchemaEditor,
  saveDraft,
  publishDraft,
  rollbackToVersion,
  forkNewDraftLine,
} = usePromptPackEditor(promptPackId)

const publishModalOpen = ref(false)
const publishBlockReasons = ref<string[]>([])
const rollbackModalOpen = ref(false)
const rollbackTargetVersion = ref('')

const pubLabel = computed(() =>
  detail.value ? promptGovernancePublicationLabel(detail.value.lifecycle) : null,
)

const pageTitleSuffix = computed(() => packTitle.value.trim() || detail.value?.promptPackId || '…')

function zhPromptPackKind(k: string): string {
  const m: Record<string, string> = {
    SYSTEM: '系统',
    TRADING: '交易',
    ANALYSIS: '分析',
    SAFETY: '安全防护',
  }
  return m[k] ?? k
}

function onPublishClick() {
  const { ok, reasons } = validatePublishForConfirm()
  if (!ok) {
    publishBlockReasons.value = reasons
    publishModalOpen.value = true
    return
  }
  publishBlockReasons.value = []
  publishModalOpen.value = true
}

async function confirmPublish() {
  if (publishBlockReasons.value.length > 0) {
    publishModalOpen.value = false
    return
  }
  publishModalOpen.value = false
  if (dirty.value) await saveDraft()
  await publishDraft()
}

function onKeySave(e: KeyboardEvent) {
  if (!(e.ctrlKey || e.metaKey) || e.key !== 's') return
  e.preventDefault()
  if (!saveDraftDisabled.value) void saveDraft()
}

function openRollbackModal() {
  const first = versionHistory.value[0]
  rollbackTargetVersion.value = first?.promptPackVersion ?? ''
  rollbackModalOpen.value = true
}

async function confirmRollback() {
  rollbackModalOpen.value = false
  if (dirty.value) {
    const ok = window.confirm('有未保存的正文更改，回滚将覆盖当前草稿。是否继续？')
    if (!ok) return
  }
  await rollbackToVersion(rollbackTargetVersion.value)
}

async function onForkFromLocked() {
  const nextId = await forkNewDraftLine()
  if (nextId) {
    await router.push({ name: 'prompts.editor', params: { promptPackId: nextId } })
  }
}

onMounted(() => window.addEventListener('keydown', onKeySave))
onUnmounted(() => window.removeEventListener('keydown', onKeySave))
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      :title="`Prompt · ${pageTitleSuffix}`"
      title-size="editor"
      density="compact"
      description="维护 Prompt 内容与版本"
      :crumbs="[
        { label: '提示词治理', to: '/prompts/strategy' },
        { label: '编辑正文' },
      ]"
    >
      <template #badges>
        <span
          v-if="dirty"
          class="inline-flex rounded-full border border-amber-600/45 bg-amber-950/35 px-2 py-0.5 text-[11px] font-medium text-amber-200/95"
        >
          未保存
        </span>
      </template>
      <template #actions>
        <RouterLink to="/prompts/strategy">
          <UiButton type="button" variant="secondary" size="sm">返回列表</UiButton>
        </RouterLink>
      </template>
    </AdminPageHeader>

    <div
      v-if="!promptPackId"
      class="mt-6 rounded-[var(--radius-ui-lg)] border border-amber-800/45 bg-amber-950/20 px-4 py-4 text-[13px] text-amber-100"
      role="status"
    >
      无效的 Prompt ID。请从
      <RouterLink class="underline-offset-4 hover:text-amber-50 hover:underline" to="/prompts/strategy">
        提示词治理
      </RouterLink>
      列表进入。
    </div>

    <div v-else-if="detailLoading" class="mt-8 space-y-4" aria-busy="true">
      <div class="h-10 w-2/3 max-w-xl animate-pulse rounded bg-slate-800/80" />
      <div class="grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(17rem,22rem)]">
        <div class="h-96 animate-pulse rounded-md bg-slate-800/40" />
        <div class="h-72 animate-pulse rounded-md bg-slate-800/30" />
      </div>
    </div>

    <p v-else-if="detailError" class="mt-6 text-sm text-amber-300">{{ detailError }}</p>

    <template v-else-if="detail">
      <div
        v-if="detailLifecycleUpper === 'LOCKED'"
        class="mt-5 flex flex-col gap-3 rounded-[var(--radius-ui)] border border-amber-800/40 bg-amber-950/25 px-4 py-3 text-sm text-amber-100/95 sm:flex-row sm:items-center sm:justify-between"
        role="status"
      >
        <div>
          <p class="font-medium text-amber-100">已发布版本正文已冻结</p>
          <p class="mt-1 text-xs leading-relaxed text-amber-200/80">
            须先复制为新草稿版本线（fork）后再改写正文；发布后将再次进入 LOCKED。
          </p>
          <p v-if="forkError" class="mt-2 text-xs text-rose-300/95">{{ forkError }}</p>
        </div>
        <UiButton type="button" size="sm" :loading="forkLoading" @click="onForkFromLocked">
          复制草稿
        </UiButton>
      </div>

      <div class="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(17rem,22rem)] lg:items-start">
        <div class="space-y-4">
          <section class="admin-panel p-4 sm:p-5">
            <h2 class="mb-4 text-sm font-semibold text-white">基础信息</h2>
            <div class="space-y-4">
              <div>
                <label class="mb-1 block text-xs text-slate-500" for="editor-pack-title">Prompt 名称</label>
                <UiInput
                  id="editor-pack-title"
                  v-model="packTitle"
                  placeholder="列表与标题展示名"
                  :disabled="true"
                />
                <p class="mt-1 text-[11px] text-slate-500">
                  展示名由服务端解析（<span class="font-mono text-slate-600">title</span> · 只读）；Phase1 不可 PATCH 改名。
                </p>
                <p v-if="detail.scenarioId?.trim()" class="mt-0.5 font-mono text-[11px] text-slate-600">
                  scenarioId · {{ detail.scenarioId }}
                </p>
              </div>
              <div class="grid gap-4 sm:grid-cols-2">
                <div>
                  <span class="mb-1 block text-xs text-slate-500">Prompt Key（唯一）</span>
                  <p class="break-all font-mono text-xs text-emerald-200/90">{{ detail.promptPackId }}</p>
                </div>
                <div>
                  <span class="mb-1 block text-xs text-slate-500">Prompt 类型</span>
                  <span
                    class="inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium border-slate-600/70 bg-slate-800/60 text-slate-200"
                  >
                    {{ zhPromptPackKind(String(detail.promptPackType ?? '')) }}
                  </span>
                </div>
                <div class="sm:col-span-2">
                  <span class="mb-1 block text-xs text-slate-500">状态</span>
                  <span
                    v-if="pubLabel"
                    class="inline-flex rounded-full border px-2 py-0.5 text-[11px] font-medium"
                    :class="pubLabel.badgeClass"
                  >
                    {{ pubLabel.zh }}
                  </span>
                  <span
                    v-if="detailIsDraft"
                    class="ml-2 inline-flex rounded-full border border-violet-600/40 bg-violet-950/30 px-2 py-0.5 text-[11px] font-medium text-violet-200/90"
                  >
                    可发布草稿
                  </span>
                </div>
              </div>
            </div>
          </section>

          <section class="admin-panel p-4 sm:p-5">
            <h2 class="mb-2 text-sm font-semibold text-white">Prompt 内容</h2>
            <p class="mb-4 text-xs leading-relaxed text-slate-500">
              使用 <strong class="font-medium text-slate-400">Markdown Lite</strong>（标题、列表、加粗、围栏代码等）；占位符如
              <code class="rounded bg-slate-800 px-1 font-mono text-[10px] text-slate-300">{{ DOC_PLACEHOLDER_EXAMPLE }}</code>
              。预览为安全渲染，不涉及 Tool / Playground。
            </p>
            <PromptMarkdownLiteField
              v-model="bodyMarkdown"
              :disabled="!canEditBody"
              :min-editor-height-px="380"
            />
            <div v-if="placeholderKeys.length > 0" class="mt-4">
              <p class="mb-2 text-xs text-slate-500">正文中占位符一览</p>
              <div class="flex flex-wrap gap-1.5">
                <span
                  v-for="k in placeholderKeys"
                  :key="k"
                  class="inline-flex rounded border border-sky-700/40 bg-sky-950/30 px-2 py-0.5 font-mono text-[11px] text-sky-200/90"
                >
                  {{ formatPlaceholderToken(k) }}
                </span>
              </div>
            </div>
            <p v-else class="mt-3 text-[11px] text-slate-500">
              未检测到 <code class="rounded bg-slate-800 px-1 font-mono text-[10px]">{{ DOC_PLACEHOLDER_EXAMPLE }}</code> 形占位符
            </p>
          </section>

          <details class="admin-panel px-4 py-3 [&_summary::-webkit-details-marker]:hidden">
            <summary class="cursor-pointer list-none text-xs font-medium text-slate-400 transition-colors hover:text-slate-200">
              高级 · variableSchema（JSON）
            </summary>
            <p class="mt-3 text-[11px] leading-relaxed text-slate-500">
              Phase1 平台白名单示例：
              <span
                v-for="ex in PHASE1_PLATFORM_PROMPT_PLACEHOLDER_EXAMPLES"
                :key="ex"
                class="mr-1 inline font-mono text-[10px] text-slate-400"
              >{{ ex }}</span>
            </p>
            <div class="mt-3 flex flex-wrap justify-end gap-2">
              <UiButton type="button" variant="ghost" size="sm" :disabled="!dirty" @click="revertWorkbench">
                放弃更改
              </UiButton>
              <UiButton
                type="button"
                variant="secondary"
                size="sm"
                :disabled="!variableSchemaValidation.ok"
                @click="formatVariableSchemaEditor"
              >
                格式化
              </UiButton>
            </div>
            <textarea
              v-model="variableSchemaRaw"
              spellcheck="false"
              rows="6"
              :disabled="!canEditBody"
              class="mt-2 box-border w-full resize-y rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 font-mono text-xs text-slate-200 [color-scheme:dark] focus:border-sky-600 focus:outline-none focus:ring-1 focus:ring-sky-600/45 disabled:opacity-60"
            />
            <p v-if="!variableSchemaValidation.ok" class="mt-2 text-xs text-rose-300/95">
              {{ variableSchemaValidation.error }}
            </p>
          </details>
        </div>

        <aside class="admin-panel sticky top-4 p-4 sm:p-5 lg:top-6">
          <h2 class="mb-4 text-sm font-semibold text-white">版本与发布</h2>
          <div class="space-y-4 text-sm">
            <div>
              <p class="text-xs text-slate-500">Token（粗估）</p>
              <p class="mt-0.5 text-xl font-semibold tabular-nums text-white">{{ tokenApprox }}</p>
              <p class="text-xs text-slate-500">字数 {{ bodyMarkdown.length.toLocaleString() }}</p>
            </div>

            <div class="border-t border-slate-800/80 pt-4">
              <p class="text-xs text-slate-500">当前版本</p>
              <p class="mt-0.5 font-mono text-slate-200">
                {{ detail.promptPackVersion ? `v${detail.promptPackVersion}` : '—（尚未发布）' }}
              </p>
            </div>
            <div>
              <p class="text-xs text-slate-500">最近更新</p>
              <p class="mt-0.5 text-slate-300">{{ formatPromptPackAt(detail.updatedAt) }}</p>
            </div>

            <div class="border-t border-slate-800/80 pt-4">
              <p class="mb-2 text-xs font-medium text-slate-400">版本历史（最近）</p>
              <p v-if="versionsLoading" class="text-xs text-slate-500">加载中…</p>
              <p v-else-if="versionsError" class="text-xs text-amber-300/95">{{ versionsError }}</p>
              <ul
                v-else-if="versionHistory.length > 0"
                class="max-h-[12rem] space-y-1 overflow-auto pl-4 text-xs text-slate-500"
              >
                <li
                  v-for="v in versionHistory.slice(0, 12)"
                  :key="`${v.promptPackVersion}-${v.publishedAt}`"
                  class="list-disc"
                >
                  v{{ v.promptPackVersion }} · {{ formatPromptPackAt(v.publishedAt) }}
                  <span v-if="v.event" class="text-slate-600">（{{ v.event }}）</span>
                </li>
              </ul>
              <p v-else class="text-xs text-slate-500">暂无记录</p>
            </div>

            <div class="space-y-2 border-t border-slate-800/80 pt-4">
              <UiButton
                type="button"
                variant="secondary"
                class="w-full"
                :loading="saveLoading"
                :disabled="saveDraftDisabled"
                @click="saveDraft"
              >
                保存草稿（⌘S）
              </UiButton>
              <UiButton
                type="button"
                variant="secondary"
                class="w-full"
                :disabled="!canRollback"
                :loading="rollbackLoading"
                @click="openRollbackModal"
              >
                从历史版本恢复
              </UiButton>
              <UiButton
                type="button"
                class="w-full"
                :loading="publishLoading"
                :disabled="!canEditBody || !detailIsDraft"
                @click="onPublishClick"
              >
                发布
              </UiButton>
            </div>

            <p class="text-[11px] leading-relaxed text-slate-500">
              发布后由 Runtime 消费的绑定关系请在编排控制台维护。
            </p>
            <p v-if="saveError" class="text-xs text-rose-300/95">{{ saveError }}</p>
            <p v-if="publishError" class="text-xs text-rose-300/95">{{ publishError }}</p>
            <p v-if="rollbackError" class="text-xs text-rose-300/95">{{ rollbackError }}</p>
          </div>
        </aside>
      </div>
    </template>

    <UiModal
      v-model:open="rollbackModalOpen"
      title="回滚到历史版本？"
      :show-default-close="true"
    >
      <p class="text-sm leading-relaxed text-slate-400">
        将按服务端快照回滚生效指针；未保存的正文可能被覆盖，请先按需保存草稿。
      </p>
      <label class="mt-4 block text-xs text-slate-500" for="rollback-version-select">目标版本</label>
      <select
        id="rollback-version-select"
        v-model="rollbackTargetVersion"
        class="mt-1 box-border w-full rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200 [color-scheme:dark] focus:border-sky-600 focus:outline-none focus:ring-1 focus:ring-sky-600/45"
      >
        <option v-for="v in versionHistory" :key="v.promptPackVersion" :value="v.promptPackVersion">
          v{{ v.promptPackVersion }} · {{ formatPromptPackAt(v.publishedAt) }}
        </option>
      </select>
      <template #footer>
        <UiButton type="button" variant="ghost" size="sm" @click="rollbackModalOpen = false">取消</UiButton>
        <UiButton
          type="button"
          size="sm"
          :loading="rollbackLoading"
          :disabled="!rollbackTargetVersion"
          @click="confirmRollback"
        >
          确认回滚
        </UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="publishModalOpen"
      :title="publishBlockReasons.length ? '暂不可发布' : '发布当前草稿？'"
      :show-default-close="true"
    >
      <template v-if="publishBlockReasons.length">
        <ul class="list-disc space-y-2 pl-5 text-sm text-slate-300">
          <li v-for="(r, i) in publishBlockReasons" :key="i">{{ r }}</li>
        </ul>
      </template>
      <p v-else class="text-sm leading-relaxed text-slate-400">
        将按环境策略把当前草稿升为对外生效版本（以服务端为准）。若有未保存更改将先保存草稿。
      </p>
      <template #footer>
        <UiButton type="button" variant="ghost" size="sm" @click="publishModalOpen = false">取消</UiButton>
        <UiButton
          v-if="!publishBlockReasons.length"
          type="button"
          size="sm"
          :loading="publishLoading"
          @click="confirmPublish"
        >
          确认发布
        </UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>
