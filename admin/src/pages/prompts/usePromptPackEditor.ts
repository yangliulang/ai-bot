/**
 * Prompt Pack 编辑器：载入详情、Markdown 正文 workbench、PATCH / 发布 / 版本 / 回滚。
 *
 * · 供 **`PromptPackEditorPage`** 全页使用（与原型 **`/prompts/editor/:packId`** 对齐）
 *
 * 作者: 杨永的Agent
 * 日期: 2026-05-22
 * 修改功能: 保存/发布/回滚成功与失败改用全局 **`adminToast`**
 * 作者: 杨永的Agent
 * 日期: 2026-05-21
 * 修改功能: 编辑器展示名优先 **`detail.title`**（`resolvePromptPackDisplayTitle`）
 * 作者: 杨永的Agent
 * 日期: 2026-05-20
 * 修改功能: 接 fork/versions/rollback · PATCH If-Match · 优先读 **`bodyMarkdown`**
 * 作者: 杨永的Agent
 * 日期: 2026-05-19
 * 修改功能: workbench 双栏编辑（Markdown Lite · 脏检查 · ⌘S · session 缓存 · 发布校验）
 * 作者: 杨永的Agent
 * 日期: 2026-05-18
 * 修改功能: **`usePromptPackEditor`** 抽 composable；**`explainPromptPackApiError`** 供治理页复用
 */

import { computed, onMounted, onUnmounted, ref, watch, type ComputedRef, type Ref } from 'vue'

import type { PromptPackPatchBody, PromptPackDetail, PromptPackVersionEntry } from '@/shared/api/admin-prompt-packs'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import {
  forkPromptPack,
  getPromptPack,
  listPromptPackVersions,
  patchPromptPack,
  publishPromptPack,
  resolvePromptPackDisplayTitle,
  rollbackPromptPack,
} from '@/shared/api/admin-prompt-packs'
import { AppError } from '@/shared/api/errors'
import {
  approximateTokensFromUtf8,
  clearSessionEditorBody,
  editorBodyToMessages,
  extractPlaceholderKeys,
  loadSessionEditorBody,
  packMessagesMutable,
  saveSessionEditorBody,
  serializeWorkbench,
  serverBodyMarkdown,
  validatePublishPack,
  type PromptWorkbenchSnapshot,
} from '@/shared/lib/prompt-editor-messages'

function fmtJson(v: unknown): string {
  return JSON.stringify(v, null, 2)
}

export function normalizeDetailVariableSchema(d: PromptPackDetail | null): Record<string, unknown> {
  if (!d?.variableSchema || typeof d.variableSchema !== 'object' || Array.isArray(d.variableSchema))
    return {}
  return { ...(d.variableSchema as Record<string, unknown>) }
}

function stringifySchemaComparable(o: Record<string, unknown>): string {
  const keys = Object.keys(o).sort()
  const sorted: Record<string, unknown> = {}
  for (const k of keys) sorted[k] = o[k]
  return fmtJson(sorted)
}

function tryParseVariableSchemaObject(raw: string):
  | { ok: true; value: Record<string, unknown> }
  | { ok: false; error: string } {
  const trimmed = raw.trim()
  const src = trimmed === '' ? '{}' : trimmed
  try {
    const parsed: unknown = JSON.parse(src)
    if (parsed === null) return { ok: true, value: {} }
    if (typeof parsed !== 'object' || Array.isArray(parsed)) {
      return {
        ok: false,
        error:
          'variableSchema 须为 JSON 对象。空对象 `{}` 表示不显式声明自定义占位符键。',
      }
    }
    return { ok: true, value: parsed as Record<string, unknown> }
  } catch {
    return { ok: false, error: 'variableSchema JSON 语法无效。' }
  }
}

export function formatPromptPackAt(iso?: string | null): string {
  if (!iso) return '—'
  return iso.replace('T', ' ').slice(0, 16)
}

export function explainPromptPackApiError(e: unknown, fallback: string): string {
  if (!(e instanceof AppError)) return fallback
  const msg = e.message || fallback
  const code = e.code ?? ''
  const st = e.status
  if (st === 409) {
    if (code === 'AGENT_PROMPT_PACK_VERSION_CONFLICT') {
      return `${msg}（版本冲突：请刷新页面后再保存。）`
    }
    if (code === 'PROMPT_PACK_LOCKED') {
      return `${msg}（该包已锁定，不能修改正文；请 fork 新版本线。）`
    }
    if (code === 'PROMPT_PACK_DEPRECATED' || code === 'PROMPT_PACK_DISABLED') {
      return `${msg}（该行已下线或停用，不能改写正文。）`
    }
  }
  if (code === 'AGENT_PROMPT_PACK_ID_CONFLICT') {
    return `${msg}（Prompt ID 冲突：请更换或留空由服务端生成。）`
  }
  if (code === 'PROMPT_SCENARIO_INVALID') {
    return `${msg}（TRADING / ANALYSIS 发布时 scenarioId 须在场景寄存器内。）`
  }
  if (code === 'PROMPT_PUBLISH_INVALID_STATE') {
    return `${msg}（仅 DRAFT 状态可发布。）`
  }
  if (code === 'PROMPT_VALIDATION_FAILED') {
    return `${msg}（占位符须在平台白名单 ∪ variableSchema 键；正文不得触发 denylist。）`
  }
  if (code === 'PROMPT_SAFETY_VIOLATION') {
    return `${msg}（命中越狱用语闸；请修改正文后再保存或发布。）`
  }
  if (code === 'PROMPT_SKILL_REF_INVALID') {
    return `${msg}（skillSpecRef 未发布或无效；请在「技能与工具」Publish 后再发布 Prompt。）`
  }
  if (code === 'PROMPT_SKILL_VERSION_ROLLBACK') {
    return `${msg}（技能规范版本不可回退。）`
  }
  return msg
}

export interface UsePromptPackEditorOptions {
  onInvalidateSummaryList?: () => void | Promise<void>
}

export function usePromptPackEditor(
  packId: Ref<string> | ComputedRef<string>,
  opts: UsePromptPackEditorOptions = {},
) {
  const detail = ref<PromptPackDetail | null>(null)
  const detailLoading = ref(false)
  const detailError = ref<string | null>(null)

  const versionHistory = ref<PromptPackVersionEntry[]>([])
  const versionsLoading = ref(false)
  const versionsError = ref<string | null>(null)

  const packTitle = ref('')
  const bodyMarkdown = ref('')
  const variableSchemaRaw = ref('{}')
  const baseline = ref('')

  const saveLoading = ref(false)
  const saveError = ref<string | null>(null)

  const publishLoading = ref(false)
  const publishError = ref<string | null>(null)

  const rollbackLoading = ref(false)
  const rollbackError = ref<string | null>(null)

  const forkLoading = ref(false)
  const forkError = ref<string | null>(null)

  function workbenchSnapshot(): PromptWorkbenchSnapshot {
    return {
      packTitle: packTitle.value,
      body: bodyMarkdown.value,
      variableSchemaRaw: variableSchemaRaw.value,
    }
  }

  function bumpBaseline(): void {
    baseline.value = serializeWorkbench(workbenchSnapshot())
  }

  function resetWorkbenchFromDetail(d: PromptPackDetail, preferSessionBody = true): void {
    const fromServer = serverBodyMarkdown(d)
    const sess = preferSessionBody ? loadSessionEditorBody(d.promptPackId) : null
    bodyMarkdown.value = sess ?? fromServer
    packTitle.value = resolvePromptPackDisplayTitle(d)
    variableSchemaRaw.value = fmtJson(normalizeDetailVariableSchema(d))
    bumpBaseline()
  }

  async function reloadVersions(id: string) {
    versionsLoading.value = true
    versionsError.value = null
    try {
      const res = await listPromptPackVersions(id)
      versionHistory.value = res.items ?? []
    } catch (e) {
      versionHistory.value = []
      versionsError.value = explainPromptPackApiError(e, '加载版本履历失败')
    } finally {
      versionsLoading.value = false
    }
  }

  async function reloadDetail(id: string) {
    const d = await getPromptPack(id)
    detail.value = d
    resetWorkbenchFromDetail(d)
    await reloadVersions(id)
  }

  async function invalidateListMaybe() {
    await opts.onInvalidateSummaryList?.()
  }

  const variableSchemaValidation = computed(() => tryParseVariableSchemaObject(variableSchemaRaw.value))

  const detailLifecycleUpper = computed(() => String(detail.value?.lifecycle ?? '').toUpperCase())

  const detailIsDraft = computed(() => detailLifecycleUpper.value === 'DRAFT')

  const detailIsLocked = computed(() => detailLifecycleUpper.value === 'LOCKED')

  const canEditBody = computed(() => {
    if (!detail.value) return false
    return packMessagesMutable(detail.value.lifecycle)
  })

  const canRollback = computed(() => {
    const lc = detailLifecycleUpper.value
    return (lc === 'PUBLISHED' || lc === 'LOCKED') && versionHistory.value.length > 0
  })

  const workbenchSig = computed(() => serializeWorkbench(workbenchSnapshot()))

  const dirty = computed(() => baseline.value.length > 0 && workbenchSig.value !== baseline.value)

  const bodyDirty = computed(() => {
    if (!detail.value) return false
    return bodyMarkdown.value !== serverBodyMarkdown(detail.value)
  })

  const schemaDirty = computed(() => {
    if (!detail.value) return false
    const v = variableSchemaValidation.value
    if (!v.ok) return true
    const fromServer = normalizeDetailVariableSchema(detail.value)
    return stringifySchemaComparable(v.value) !== stringifySchemaComparable(fromServer)
  })

  const tokenApprox = computed(() => approximateTokensFromUtf8(bodyMarkdown.value))
  const placeholderKeys = computed(() => extractPlaceholderKeys(bodyMarkdown.value))

  const saveDraftDisabled = computed(() => {
    if (!detail.value || !canEditBody.value || saveLoading.value) return true
    if (!dirty.value) return true
    if (schemaDirty.value && !variableSchemaValidation.value.ok) return true
    return false
  })

  async function loadPackEffect(id: string) {
    detail.value = null
    versionHistory.value = []
    packTitle.value = ''
    bodyMarkdown.value = ''
    variableSchemaRaw.value = '{}'
    baseline.value = ''
    detailError.value = null
    versionsError.value = null
    publishError.value = null
    rollbackError.value = null
    forkError.value = null
    saveError.value = null

    detailLoading.value = true
    try {
      await reloadDetail(id)
    } catch (e) {
      detailError.value = explainPromptPackApiError(e, '加载详情失败')
    } finally {
      detailLoading.value = false
    }
  }

  function clearAll() {
    detail.value = null
    versionHistory.value = []
    packTitle.value = ''
    bodyMarkdown.value = ''
    variableSchemaRaw.value = '{}'
    baseline.value = ''
    detailError.value = null
    versionsError.value = null
    publishError.value = null
    rollbackError.value = null
    forkError.value = null
    saveError.value = null
    detailLoading.value = false
  }

  watch(
    () => String(packId.value ?? '').trim(),
    (id) => {
      if (!id) {
        clearAll()
        return
      }
      void loadPackEffect(id)
    },
    { immediate: true },
  )

  watch(bodyMarkdown, (body) => {
    const id = String(packId.value ?? '').trim()
    if (!id || !dirty.value) return
    saveSessionEditorBody(id, body)
  })

  function onBeforeUnload(e: BeforeUnloadEvent) {
    if (!dirty.value) return
    e.preventDefault()
    e.returnValue = ''
  }

  onMounted(() => window.addEventListener('beforeunload', onBeforeUnload))
  onUnmounted(() => window.removeEventListener('beforeunload', onBeforeUnload))

  async function saveDraft() {
    const id = String(packId.value ?? '').trim()
    if (!id || !detail.value || !canEditBody.value) return

    const body: PromptPackPatchBody = {}
    if (bodyDirty.value) {
      body.messages = editorBodyToMessages(bodyMarkdown.value, detail.value.messages)
    }
    if (schemaDirty.value) {
      const sv = variableSchemaValidation.value
      if (!sv.ok) {
        saveError.value = sv.error
        return
      }
      body.variableSchema = sv.value
    }
    if (!body.messages && body.variableSchema === undefined) return

    saveLoading.value = true
    saveError.value = null
    try {
      const next = await patchPromptPack(id, body, {
        ifMatch: detail.value.rowVersion ?? detail.value.etag,
      })
      detail.value = next
      resetWorkbenchFromDetail(next, false)
      clearSessionEditorBody(id)
      adminToastSuccess('草稿已保存')
      await invalidateListMaybe()
    } catch (e) {
      const msg = explainPromptPackApiError(e, '保存失败')
      saveError.value = msg
      adminToastError(msg)
    } finally {
      saveLoading.value = false
    }
  }

  async function publishDraft() {
    const id = String(packId.value ?? '').trim()
    if (!id || !detail.value || !detailIsDraft.value) return
    publishLoading.value = true
    publishError.value = null
    try {
      const result = await publishPromptPack(id)
      await invalidateListMaybe()
      await reloadDetail(id)
      adminToastSuccess(`已发布：lifecycle=${result.lifecycle}，版本 v${result.promptPackVersion}`)
    } catch (e) {
      const msg = explainPromptPackApiError(e, '发布失败')
      publishError.value = msg
      adminToastError(msg)
    } finally {
      publishLoading.value = false
    }
  }

  async function rollbackToVersion(promptPackVersion: string) {
    const id = String(packId.value ?? '').trim()
    if (!id || !promptPackVersion.trim()) return
    rollbackLoading.value = true
    rollbackError.value = null
    try {
      const result = await rollbackPromptPack(id, { promptPackVersion: promptPackVersion.trim() })
      await invalidateListMaybe()
      await reloadDetail(id)
      adminToastSuccess(`已回滚至 v${result.promptPackVersion}（${result.lifecycle}）`)
    } catch (e) {
      const msg = explainPromptPackApiError(e, '回滚失败')
      rollbackError.value = msg
      adminToastError(msg)
    } finally {
      rollbackLoading.value = false
    }
  }

  /** LOCKED 包在编辑器内 fork 出新 DRAFT（返回新 id，由页面负责跳转） */
  async function forkNewDraftLine(newPromptPackId?: string): Promise<string | null> {
    const id = String(packId.value ?? '').trim()
    if (!id) return null
    forkLoading.value = true
    forkError.value = null
    try {
      const next = await forkPromptPack(id, newPromptPackId?.trim() ? { promptPackId: newPromptPackId.trim() } : undefined)
      await invalidateListMaybe()
      return next.promptPackId
    } catch (e) {
      forkError.value = explainPromptPackApiError(e, '复制草稿失败')
      return null
    } finally {
      forkLoading.value = false
    }
  }

  return {
    detail,
    detailLoading,
    detailError,
    versionHistory,
    versionsLoading,
    versionsError,
    packTitle,
    bodyMarkdown,
    variableSchemaRaw,
    variableSchemaValidation,
    detailLifecycleUpper,
    detailIsDraft,
    detailIsLocked,
    canEditBody,
    canRollback,
    dirty,
    bodyDirty,
    schemaDirty,
    tokenApprox,
    placeholderKeys,
    saveDraftDisabled,
    saveLoading,
    saveError,
    publishLoading,
    publishError,
    rollbackLoading,
    rollbackError,
    forkLoading,
    forkError,
    fmtJson,
    formatPromptPackAt,
    normalizeDetailVariableSchema,
    validatePublishForConfirm: () => {
      if (!detail.value) return { ok: false, reasons: ['未加载包详情'] }
      return validatePublishPack(detail.value, bodyMarkdown.value)
    },
    revertWorkbench() {
      if (!detail.value) return
      resetWorkbenchFromDetail(detail.value, false)
      clearSessionEditorBody(detail.value.promptPackId)
      saveError.value = null
    },
    formatVariableSchemaEditor() {
      const v = variableSchemaValidation.value
      if (!v.ok) return
      variableSchemaRaw.value = stringifySchemaComparable(v.value)
    },
    saveDraft,
    publishDraft,
    rollbackToVersion,
    forkNewDraftLine,
    loadPackEffect,
    reloadVersions,
  }
}
