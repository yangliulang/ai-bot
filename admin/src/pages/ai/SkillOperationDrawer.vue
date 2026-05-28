<!--
作者: Cursor Agent
日期: 2026-05-26
修改功能: 技能操作规范详情抽屉 · 交互对齐原型 · 样式对齐 admin 整站
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import {
  countRequiredParams,
  parseSkillOperationView,
  type SkillOperationView,
} from '@/entities/tool-registry/parse-skill-operation-view'
import {
  getSkillRegistryEntry,
  matrixStatusClass,
  matrixStatusLabel,
  skillDomainLabel,
  type SkillRegistryRowView,
} from '@/entities/tool-registry/skill-registry-catalog'
import {
  SKILL_CONTRACT_STATUS,
  SKILL_DRAWER,
  SKILL_OVERVIEW_METRICS,
  SKILL_SPEC_SECTION,
  type SkillSpecSectionKey,
} from '@/entities/tool-registry/tool-registry-copy'
import {
  explainSkillSpecApiError,
  getSkillOperationSpecVersionBody,
  getSkillOperationSpecVersions,
  publishSkillOperationSpec,
  type SkillSpecVersionEntry,
} from '@/shared/api/admin-skill-specs'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import { copyTextToClipboard } from '@/shared/utils/copy-to-clipboard'
import { UiButton, UiModal, UiInput, UiStatChip } from '@/shared/ui'

import SkillSpecSectionPanel from '@/pages/ai/SkillSpecSectionPanel.vue'

const props = defineProps<{
  skillId: string | null
  row: SkillRegistryRowView | null
}>()

const emit = defineEmits<{
  close: []
  published: []
}>()

type DrawerTab = 'overview' | 'spec'

const mainTab = ref<DrawerTab>('overview')
const specSection = ref<SkillSpecSectionKey>('params')
const rawOpen = ref(false)

const versions = ref<SkillSpecVersionEntry[]>([])
const versionsLoading = ref(false)
const versionsError = ref<string | null>(null)
const selectedVersion = ref<string | null>(null)
const bodyPreview = ref<string | null>(null)
const bodyLoading = ref(false)
const bodyError = ref<string | null>(null)

const publishOpen = ref(false)
const publishVersion = ref('')
const publishBody = ref('')
const publishSubmitting = ref(false)
const publishError = ref<string | null>(null)

const entry = computed(() => {
  const id = props.skillId
  if (!id) return null
  return getSkillRegistryEntry(id)
})

const drawerTitle = computed(
  () => entry.value?.summary ?? props.row?.summary ?? SKILL_DRAWER.fallbackTitle,
)

const parsedView = computed<SkillOperationView | null>(() => {
  if (!bodyPreview.value) return null
  try {
    return parseSkillOperationView(bodyPreview.value)
  } catch {
    return null
  }
})

const contractStatus = computed<'complete' | 'missing' | 'n/a'>(() => {
  if (!props.row?.publishRequired) return 'n/a'
  if (props.row.contractComplete) return 'complete'
  if (parsedView.value) return 'missing'
  return 'missing'
})

const specSections = computed(() => {
  const view = parsedView.value
  if (!view) return []
  return (
    [
      { key: 'params' as const, label: SKILL_SPEC_SECTION.params.label, count: view.requiredParams.rows.length },
      { key: 'validation' as const, label: SKILL_SPEC_SECTION.validation.label, count: view.validations.rows.length },
      { key: 'confirm' as const, label: SKILL_SPEC_SECTION.confirm.label, count: view.confirmation.rows.length },
      { key: 'unknown' as const, label: SKILL_SPEC_SECTION.unknown.label, count: view.unknown.rows.length },
      { key: 'refusal' as const, label: SKILL_SPEC_SECTION.refusal.label, count: view.refusals.rows.length },
      {
        key: 'api' as const,
        label: SKILL_SPEC_SECTION.api.label,
        count: view.apiText?.trim() ? 1 : 0,
      },
    ] as const
  ).map((s) => ({ ...s, disabled: s.key === 'api' && s.count === 0 }))
})

const overviewMetrics = computed(() => {
  const view = parsedView.value
  if (!view) return null
  return [
    {
      label: SKILL_OVERVIEW_METRICS.required,
      value: `${countRequiredParams(view)} ${SKILL_OVERVIEW_METRICS.unitItem}`,
    },
    {
      label: SKILL_OVERVIEW_METRICS.validation,
      value: `${view.validations.rows.length} ${SKILL_OVERVIEW_METRICS.unitRule}`,
    },
    {
      label: SKILL_OVERVIEW_METRICS.confirm,
      value: `${view.confirmation.rows.length} ${SKILL_OVERVIEW_METRICS.unitItem}`,
    },
    {
      label: SKILL_OVERVIEW_METRICS.refusal,
      value: `${view.refusals.rows.length} ${SKILL_OVERVIEW_METRICS.unitRule}`,
    },
  ]
})

const displayVersion = computed(
  () => props.row?.skillSpecVersion ?? parsedView.value?.version ?? null,
)

async function loadVersions(skillId: string) {
  versionsLoading.value = true
  versionsError.value = null
  versions.value = []
  try {
    const res = await getSkillOperationSpecVersions(skillId)
    versions.value = res.items
    const pointer = props.row?.skillSpecVersion
    const pick =
      pointer && res.items.some((v) => v.skillSpecVersion === pointer)
        ? pointer
        : (res.items[0]?.skillSpecVersion ?? null)
    selectedVersion.value = pick
  } catch (e) {
    versionsError.value = explainSkillSpecApiError(e, '加载版本履历失败')
  } finally {
    versionsLoading.value = false
  }
}

async function loadBodyPreview(skillId: string, version: string) {
  bodyLoading.value = true
  bodyError.value = null
  bodyPreview.value = null
  try {
    const res = await getSkillOperationSpecVersionBody(skillId, version)
    bodyPreview.value = res.bodyMarkdown
  } catch (e) {
    bodyError.value = explainSkillSpecApiError(e, '加载正文失败')
  } finally {
    bodyLoading.value = false
  }
}

watch(
  () => props.skillId,
  (id) => {
    mainTab.value = 'overview'
    specSection.value = 'params'
    rawOpen.value = false
    versions.value = []
    selectedVersion.value = null
    bodyPreview.value = null
    if (!id) return
    void loadVersions(id)
  },
  { immediate: true },
)

watch(selectedVersion, (ver) => {
  const sid = props.skillId
  if (!sid || !ver) return
  void loadBodyPreview(sid, ver)
})

function openPublishModal() {
  if (props.row?.isRuntimePublished) return
  publishVersion.value = ''
  publishBody.value = bodyPreview.value ?? ''
  publishError.value = null
  publishOpen.value = true
}

async function submitPublish() {
  const sid = props.skillId
  const ver = publishVersion.value.trim()
  if (!sid || !ver) {
    publishError.value = '请填写 skillSpecVersion'
    return
  }
  const bodyMd = publishBody.value.trim()
  if (bodyMd.length < 200) {
    publishError.value = 'bodyMarkdown 须 ≥ 200 字且含契约章节（## 1.）'
    return
  }
  publishSubmitting.value = true
  publishError.value = null
  try {
    const result = await publishSkillOperationSpec(sid, {
      skillSpecVersion: ver,
      bodyMarkdown: bodyMd,
    })
    adminToastSuccess(SKILL_DRAWER.publishSuccess)
    publishOpen.value = false
    emit('published')
    await loadVersions(sid)
    selectedVersion.value = result.skillSpecVersion
  } catch (e) {
    publishError.value = explainSkillSpecApiError(e, SKILL_DRAWER.publishFail)
    adminToastError(publishError.value)
  } finally {
    publishSubmitting.value = false
  }
}

async function copySkillId() {
  if (!props.skillId) return
  const ok = await copyTextToClipboard(props.skillId)
  if (ok) adminToastSuccess(SKILL_DRAWER.copySuccess)
  else adminToastError(SKILL_DRAWER.copyFail)
}
</script>

<template>
  <Teleport to="body">
    <Transition name="admin-drawer-scrim">
      <div
        v-if="skillId"
        class="fixed inset-0 z-40 bg-slate-950/55"
        aria-hidden="true"
        @click.self="emit('close')"
      />
    </Transition>
    <Transition name="admin-drawer-panel">
      <aside
        v-if="skillId && row"
        class="admin-skill-operation-drawer fixed inset-y-0 right-0 z-50 flex w-full max-w-[min(880px,100vw-40px)] flex-col border-l border-slate-800 bg-slate-950 shadow-2xl"
        role="dialog"
        aria-modal="true"
        :aria-label="drawerTitle"
      >
        <div class="flex items-start justify-between gap-2 border-b border-slate-800 px-4 py-3">
          <div class="min-w-0">
            <h3 class="text-sm font-medium text-white">{{ drawerTitle }}</h3>
            <p class="mt-0.5 text-xs text-slate-500">{{ SKILL_DRAWER.switchHint }}</p>
          </div>
          <button
            type="button"
            class="rounded p-1 text-slate-500 hover:bg-slate-800 hover:text-slate-300"
            aria-label="关闭"
            @click="emit('close')"
          >
            <svg class="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
              <path d="M6 6l12 12M18 6L6 18" stroke-linecap="round" />
            </svg>
          </button>
        </div>
        <div class="border-b border-slate-800 px-4 py-3">
          <div class="flex flex-wrap gap-2">
            <UiStatChip v-if="skillId && skillDomainLabel(skillId)" tone="violet">
              {{ skillDomainLabel(skillId) }}
            </UiStatChip>
            <span
              class="inline-flex rounded border px-2 py-0.5 text-[11px] font-medium"
              :class="matrixStatusClass(row.matrixStatus)"
            >
              {{ matrixStatusLabel(row.matrixStatus) }}
            </span>
            <UiStatChip v-if="contractStatus === 'complete'" tone="success">
              {{ SKILL_CONTRACT_STATUS.complete }}
            </UiStatChip>
            <UiStatChip v-else-if="contractStatus === 'missing'" tone="neutral">
              {{ SKILL_CONTRACT_STATUS.missing }}
            </UiStatChip>
            <UiStatChip v-else tone="neutral">{{ SKILL_CONTRACT_STATUS.na }}</UiStatChip>
            <UiStatChip v-if="displayVersion" tone="neutral">
              {{ SKILL_DRAWER.version(displayVersion) }}
            </UiStatChip>
            <UiStatChip v-if="row.isRuntimePublished" tone="success">
              {{ SKILL_DRAWER.runtimePublished }}
            </UiStatChip>
            <UiStatChip v-else-if="row.publishRequired" tone="neutral">
              {{ SKILL_DRAWER.runtimeDraft }}
            </UiStatChip>
            <UiStatChip v-if="row.publishRequired" tone="info">{{ SKILL_DRAWER.publishRequired }}</UiStatChip>
            <UiStatChip v-else tone="neutral">{{ SKILL_DRAWER.registerOnly }}</UiStatChip>
          </div>
        </div>

        <div class="flex gap-2 border-b border-slate-800 px-4 py-2">
          <button
            type="button"
            class="admin-seg text-xs sm:text-sm"
            :class="
              mainTab === 'overview'
                ? 'admin-seg-active'
                : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
            "
            @click="mainTab = 'overview'"
          >
            {{ SKILL_DRAWER.tabOverview }}
          </button>
          <button
            type="button"
            class="admin-seg text-xs sm:text-sm"
            :class="
              mainTab === 'spec'
                ? 'admin-seg-active'
                : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
            "
            :disabled="!parsedView && bodyLoading"
            @click="mainTab = 'spec'"
          >
            {{ SKILL_DRAWER.tabSpec }}
          </button>
        </div>

        <div class="flex-1 overflow-y-auto px-4 py-4">
          <div v-if="mainTab === 'overview'" class="space-y-4">
            <div
              v-if="overviewMetrics"
              class="admin-panel grid grid-cols-2 gap-3 p-3 sm:grid-cols-4"
            >
              <div v-for="item in overviewMetrics" :key="item.label">
                <p class="text-[11px] text-slate-500">{{ item.label }}</p>
                <p class="text-sm font-semibold tabular-nums text-slate-100">{{ item.value }}</p>
              </div>
            </div>

            <div class="grid gap-3 sm:grid-cols-2">
              <div class="admin-panel p-3">
                <p class="mb-1 text-xs font-medium text-slate-500">{{ SKILL_DRAWER.labelUserFlow }}</p>
                <p class="text-sm leading-relaxed text-slate-300">{{ row.userFlow }}</p>
              </div>
              <div class="admin-panel p-3">
                <p class="mb-1 text-xs font-medium text-slate-500">{{ SKILL_DRAWER.labelExchange }}</p>
                <p class="text-sm leading-relaxed text-slate-300">{{ row.exchangeAction }}</p>
              </div>
            </div>

            <div
              v-if="row.publishRequired && contractStatus === 'complete'"
              class="rounded-lg border border-sky-500/25 bg-sky-500/10 px-4 py-3 text-sm text-sky-100/95"
            >
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div class="min-w-0 flex-1">
                  <p class="font-medium text-sky-100">{{ SKILL_DRAWER.publishRuntime }}</p>
                  <p class="mt-1 text-xs text-sky-100/85">{{ SKILL_DRAWER.publishRuntimeHint }}</p>
                </div>
                <UiButton
                  type="button"
                  size="sm"
                  :disabled="row.isRuntimePublished"
                  @click="openPublishModal"
                >
                  {{
                    row.isRuntimePublished ? SKILL_DRAWER.publishAlready : SKILL_DRAWER.publishRuntime
                  }}
                </UiButton>
              </div>
            </div>
            <div
              v-else-if="row.publishRequired && contractStatus !== 'complete'"
              class="rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-xs text-amber-100/90"
            >
              {{ SKILL_DRAWER.publishGate }}
            </div>

            <div
              v-if="parsedView?.businessLine"
              class="rounded-lg border border-sky-500/25 bg-sky-500/10 px-4 py-3 text-xs leading-relaxed text-sky-100/90"
            >
              {{ parsedView.businessLine }}
            </div>

            <UiButton
              v-if="parsedView"
              type="button"
              variant="ghost"
              size="sm"
              class="px-0"
              @click="mainTab = 'spec'"
            >
              {{ SKILL_DRAWER.gotoSpec }}
            </UiButton>

            <p
              v-if="!parsedView && row.specNote"
              class="rounded-lg border border-amber-500/30 bg-amber-500/5 px-3 py-2 text-xs text-amber-100/90"
            >
              {{ row.specNote }}
            </p>
          </div>

          <div v-else class="space-y-3">
            <div v-if="bodyLoading" class="py-12 text-center text-xs text-slate-500">
              {{ SKILL_DRAWER.loading }}
            </div>
            <template v-else-if="parsedView">
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="seg in specSections"
                  :key="seg.key"
                  type="button"
                  class="admin-seg inline-flex items-center gap-1.5 text-xs"
                  :class="
                    specSection === seg.key
                      ? 'admin-seg-active'
                      : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
                  "
                  :disabled="seg.disabled"
                  @click="specSection = seg.key"
                >
                  <span>{{ seg.label }}</span>
                  <UiStatChip v-if="seg.count > 0" tone="neutral">{{ seg.count }}</UiStatChip>
                </button>
              </div>
              <SkillSpecSectionPanel :section="specSection" :view="parsedView" />
            </template>
            <p v-else class="py-8 text-center text-xs text-slate-500">
              {{ row.specNote ?? SKILL_DRAWER.emptySpec }}
            </p>
          </div>

          <details v-if="bodyPreview" class="mt-4">
            :open="rawOpen"
            @toggle="rawOpen = ($event.target as HTMLDetailsElement).open"
          >
            <summary class="cursor-pointer text-sm text-slate-400 hover:text-slate-300">
              {{ SKILL_DRAWER.rawCollapse }}
            </summary>
            <pre
              class="admin-skill-spec-raw-md mt-2 max-h-[min(40vh,20rem)] overflow-auto whitespace-pre-wrap rounded border border-slate-800 bg-slate-900/80 p-3 font-mono text-[11px] leading-relaxed text-slate-300"
            >{{ bodyPreview.slice(0, 16000) }}</pre>
          </details>
        </div>

        <div class="flex items-center justify-between gap-2 border-t border-slate-800 px-4 py-3">
          <code class="max-w-[55%] truncate font-mono text-[10px] text-slate-600">{{ skillId }}</code>
          <div class="flex gap-2">
            <UiButton type="button" variant="secondary" size="sm" @click="copySkillId">
              {{ SKILL_DRAWER.copyId }}
            </UiButton>
            <UiButton type="button" size="sm" @click="emit('close')">{{ SKILL_DRAWER.close }}</UiButton>
          </div>
        </div>
      </aside>
    </Transition>
  </Teleport>

  <UiModal v-model:open="publishOpen" title="Publish 技能操作规范">
    <p class="mb-3 text-xs text-slate-500">
      {{ skillId }} · 须单调递增版本号；正文 ≥ 200 字且含 <code class="text-slate-400">## 1.</code>
    </p>
    <label class="mb-3 block">
      <span class="mb-1 block text-xs text-slate-500">skillSpecVersion</span>
      <UiInput v-model="publishVersion" size="sm" placeholder="例如 1.0.1" />
    </label>
    <label class="mb-3 block">
      <span class="mb-1 block text-xs text-slate-500">bodyMarkdown</span>
      <textarea
        v-model="publishBody"
        rows="12"
        class="w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 font-mono text-xs text-slate-200 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
      />
    </label>
    <p v-if="publishError" class="mb-3 text-sm text-rose-400">{{ publishError }}</p>
    <template #footer>
      <UiButton type="button" variant="secondary" size="sm" @click="publishOpen = false">取消</UiButton>
      <UiButton type="button" size="sm" :disabled="publishSubmitting" @click="submitPublish">
        {{ publishSubmitting ? SKILL_DRAWER.publishing : '确认 Publish' }}
      </UiButton>
    </template>
  </UiModal>
</template>
