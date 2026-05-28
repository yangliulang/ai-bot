<!--
作者: 杨永的Agent
日期: 2026-05-28
修改功能: 使用策略 Tab 增加 MemoryRuntimeConfigPanel（MR-MEM-01 · keys §2.1～§2.2）
作者: 杨永的Agent
日期: 2026-05-28
修改功能: runtime Tab 自适应多列网格（策略/记忆并排 · 网关表单三列/两列）
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 使用策略「保存」成功反馈改为锚定按钮 tooltip（UiAnchorTip）
修改功能: apiModel 表单与策略下拉 catalog modelId 标签；网关 422 提示
修改功能: 添加模型弹窗移除预置模型下拉，仅手填 modelId
修改功能: 使用策略 Tab 增量「网关策略」分区（intentNluUseLlm + telegramLlmNarrate）
修改功能: 交互对齐 product-doc `/ai-settings`：双 Tab「厂商与模型 / 使用策略」、可展开厂商表、策略分区与运行时下拉
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 对齐产品原型 Tab「厂商与模型 / 使用策略」；目录表迁至 AiSettingsCatalogPanel
作者: 杨永的Agent
日期: 2026-05-12
修改功能: Provider secretRef 帮助文案 — env 变量名 vs 明文入库、安全提示；对齐 FE_HANDOFF 最新小节
作者: 杨永的Agent
日期: 2026-05-13
修改功能: 添加模型弹窗 — 方舟 modelId 与控制台开通一致之说明（FE_HANDOFF 可选项）
-->
<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { AppError } from '@/shared/api/errors'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import {
  createAiModel,
  createAiProvider,
  deleteAiModel,
  deleteAiProvider,
  getAiGatewayDefaults,
  listAiModels,
  listAiProviders,
  patchAiGatewayDefaults,
  patchAiModel,
  patchAiProvider,
  probeAiProviderHealth,
  type AiGatewayDefaults,
  type LlmModelSummary,
  type LlmProviderSummary,
} from '@/shared/api/admin-ai-settings'
import AiSettingsCatalogPanel from '@/features/ai-settings/AiSettingsCatalogPanel.vue'
import GatewayPolicyPanel from '@/features/ai-settings/GatewayPolicyPanel.vue'
import MemoryRuntimeConfigPanel from '@/features/ai-settings/MemoryRuntimeConfigPanel.vue'
import {
  DEFAULT_BASE_URL_BY_CATALOG,
  LLM_VENDOR_CATALOG_LABELS,
  LLM_VENDOR_CATALOG_OPTIONS,
  type LlmVendorCatalogKind,
} from '@/features/ai-settings/catalog-constants'
import {
  emptyTelegramLlmNarrate,
  mergeTelegramLlmNarrateFromDefaults,
} from '@/features/ai-settings/gateway-policy-constants'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminPageHeader from '@/shared/ui/AdminPageHeader.vue'
import UiAnchorTip from '@/shared/ui/UiAnchorTip.vue'
import UiButton from '@/shared/ui/UiButton.vue'
import UiModal from '@/shared/ui/UiModal.vue'
import { UiInput, UiSelect, UiSwitch, type UiSelectOption } from '@/shared/ui'

const OPT_NONE = '__none__'

type AiSettingsTab = 'catalog' | 'runtime'

const route = useRoute()
const router = useRouter()

const aiSettingsTab = computed<AiSettingsTab>(() => {
  const raw = route.query.tab
  const t = Array.isArray(raw) ? raw[0] : raw
  return t === 'runtime' ? 'runtime' : 'catalog'
})

function setAiSettingsTab(next: AiSettingsTab) {
  const query = { ...route.query } as Record<string, string | string[]>
  if (next === 'catalog') {
    delete query.tab
  } else {
    query.tab = 'runtime'
  }
  void router.replace({ path: route.path, query })
}

const numInputClass =
  'box-border h-10 min-h-10 w-full rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 text-sm text-white [color-scheme:dark] outline-none transition-[border-color,box-shadow] duration-200 focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600/60'

const SCENARIO_FIELDS = [
  { key: 'scenarioChatModel' as const, label: '普通问答' },
  { key: 'scenarioTradingModel' as const, label: '交易执行' },
  { key: 'scenarioRiskModel' as const, label: '风险判断' },
]

const loading = ref(true)
const saving = ref(false)
const saveGatewayTipRef = ref<InstanceType<typeof UiAnchorTip> | null>(null)
const loadError = ref<string | null>(null)
const saveError = ref<string | null>(null)

const providers = ref<LlmProviderSummary[]>([])
const models = ref<LlmModelSummary[]>([])

const probeByProvider = ref<Record<string, string>>({})

const expandedProviderIds = ref<string[]>([])
const providerCatalogKindById = ref<Record<string, LlmVendorCatalogKind>>({})

const providerModalOpen = ref(false)
const providerModalMode = ref<'create' | 'edit'>('create')
const editingProvider = ref<LlmProviderSummary | null>(null)
const newProviderVendorPreset = ref<LlmVendorCatalogKind>('openai')
const newProviderCustomDisplayName = ref('')
const newProviderDisplayName = ref('')
const newProviderBaseUrl = ref('')
const newProviderSecretRef = ref('')
const providerCreateError = ref<string | null>(null)
const providerCreating = ref(false)

const modelModalOpen = ref(false)
const modelModalParent = ref<LlmProviderSummary | null>(null)
const newModelProviderId = ref('')
const newModelId = ref('')
const newModelApiModel = ref('')
const newModelStatus = ref('enabled')
const newModelContextWindow = ref('')
const modelCreateError = ref<string | null>(null)
const modelCreating = ref(false)

const deletingModelId = ref<string | null>(null)
const deletingProviderId = ref<string | null>(null)
const providerDeleteError = ref<{ providerId: string; message: string } | null>(null)

const providerDeleteConfirmOpen = ref(false)
const providerPendingDelete = ref<LlmProviderSummary | null>(null)
const modelDeleteConfirmOpen = ref(false)
const modelPendingDelete = ref<LlmModelSummary | null>(null)

const gatewayPolicy = reactive({
  intentNluUseLlm: false,
  intentClarifyUseLlm: false,
  telegramLlmNarrate: emptyTelegramLlmNarrate(),
})

const form = reactive({
  defaultProviderId: OPT_NONE,
  defaultModelId: OPT_NONE,
  defaultInferenceModel: '',
  scenarioChatModel: '',
  scenarioTradingModel: '',
  scenarioRiskModel: '',
  maxContextTokens: 128000,
  maxOutputTokens: 4096,
  timeoutSec: 120,
  fallbackOnPrimaryFailure: true,
  fallbackOnTimeout: true,
  downgradePeakTraffic: false,
  fallbackModel: '',
  maxTokensPerRequest: 32000,
  dailyTokenBudgetM: 50,
  rateLimitRpm: 600,
  budgetMaxToolCalls: 32,
  budgetMaxOrchestrationSteps: 32,
  /** 文本：留空表示 orchestration 中 maxModelTurnsPerExecution = null */
  budgetMaxModelTurns: '',
})

function catalogKindForProvider(p: LlmProviderSummary): LlmVendorCatalogKind {
  const mapped = providerCatalogKindById.value[p.providerId]
  if (mapped) return mapped
  const id = p.providerId.toLowerCase()
  if (id.includes('openai')) return 'openai'
  if (id.includes('anthropic') || id.includes('claude')) return 'anthropic'
  if (id.includes('deepseek')) return 'deepseek'
  return 'none'
}

const showVolcModelIdHint = computed(() => {
  const parent = modelModalParent.value
  if (!parent) return false
  return parent.baseUrl.toLowerCase().includes('volces.com')
})

function reconcileRuntimeFormWithCatalog() {
  const pidSet = new Set(providers.value.map((p) => p.providerId))
  if (form.defaultProviderId !== OPT_NONE && !pidSet.has(form.defaultProviderId)) {
    form.defaultProviderId = OPT_NONE
  }
  const ids = new Set(models.value.map((m) => m.modelId))
  const byModelId = new Map(models.value.map((m) => [m.modelId, m]))

  function pruneModelRef(raw: string): string {
    const v = raw.trim()
    if (!v) return ''
    return ids.has(v) ? v : ''
  }

  form.defaultInferenceModel = pruneModelRef(form.defaultInferenceModel)
  form.scenarioChatModel = pruneModelRef(form.scenarioChatModel)
  form.scenarioTradingModel = pruneModelRef(form.scenarioTradingModel)
  form.scenarioRiskModel = pruneModelRef(form.scenarioRiskModel)
  form.fallbackModel = pruneModelRef(form.fallbackModel)

  if (form.defaultModelId !== OPT_NONE && form.defaultModelId) {
    const row = byModelId.get(form.defaultModelId)
    if (!row) {
      form.defaultModelId = OPT_NONE
    } else if (form.defaultProviderId !== OPT_NONE && row.providerId !== form.defaultProviderId) {
      form.defaultModelId = OPT_NONE
    }
  }
}

function toastSuccess(msg: string) {
  adminToastSuccess(msg)
}

function toastError(msg: string) {
  adminToastError(msg)
}

function applyGatewayPolicy(d: AiGatewayDefaults) {
  gatewayPolicy.intentNluUseLlm = Boolean(d.intentNluUseLlm ?? false)
  gatewayPolicy.intentClarifyUseLlm = Boolean(d.intentClarifyUseLlm ?? false)
  gatewayPolicy.telegramLlmNarrate = mergeTelegramLlmNarrateFromDefaults(d.telegramLlmNarrate)
}

function applyDefaults(d: AiGatewayDefaults) {
  applyGatewayPolicy(d)
  form.defaultProviderId = d.defaultProviderId ? String(d.defaultProviderId) : OPT_NONE
  form.defaultModelId = d.defaultModelId ? String(d.defaultModelId) : OPT_NONE
  form.defaultInferenceModel = String(d.defaultInferenceModel ?? '')
  form.scenarioChatModel = String(d.scenarioChatModel ?? '')
  form.scenarioTradingModel = String(d.scenarioTradingModel ?? '')
  form.scenarioRiskModel = String(d.scenarioRiskModel ?? '')
  form.maxContextTokens = Number(d.maxContextTokens ?? 128000)
  form.maxOutputTokens = Number(d.maxOutputTokens ?? 4096)
  form.timeoutSec = Number(d.timeoutSec ?? 120)
  form.fallbackOnPrimaryFailure = Boolean(d.fallbackOnPrimaryFailure ?? true)
  form.fallbackOnTimeout = Boolean(d.fallbackOnTimeout ?? true)
  form.downgradePeakTraffic = Boolean(d.downgradePeakTraffic ?? false)
  form.fallbackModel = String(d.fallbackModel ?? '')
  form.maxTokensPerRequest = Number(d.maxTokensPerRequest ?? 32000)
  form.dailyTokenBudgetM = Number(d.dailyTokenBudgetM ?? 50)
  form.rateLimitRpm = Number(d.rateLimitRpm ?? 600)
  const b = d.orchestrationExecutionBudget
  if (b && typeof b === 'object') {
    form.budgetMaxToolCalls = Number((b as { maxToolCallsPerExecution?: number }).maxToolCallsPerExecution ?? 32)
    form.budgetMaxOrchestrationSteps = Number(
      (b as { maxOrchestrationStepsPerExecution?: number }).maxOrchestrationStepsPerExecution ?? 32,
    )
    const mt = (b as { maxModelTurnsPerExecution?: number | null }).maxModelTurnsPerExecution
    form.budgetMaxModelTurns =
      mt == null || mt === undefined ? '' : String(Math.trunc(Number(mt)))
  }
  reconcileRuntimeFormWithCatalog()
}

async function loadAll() {
  loading.value = true
  loadError.value = null
  providerDeleteError.value = null
  try {
    const [pr, mo, def] = await Promise.all([
      listAiProviders(),
      listAiModels(),
      getAiGatewayDefaults(),
    ])
    providers.value = pr.items
    models.value = mo.items
    applyDefaults(def)
  } catch (e) {
    loadError.value = e instanceof AppError ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(loadAll)

watch(providerDeleteConfirmOpen, (open) => {
  if (!open) providerPendingDelete.value = null
})
watch(modelDeleteConfirmOpen, (open) => {
  if (!open) modelPendingDelete.value = null
})

const modelCountForPendingProvider = computed(() => {
  const p = providerPendingDelete.value
  if (!p) return 0
  return models.value.filter((m) => m.providerId === p.providerId).length
})

function runtimeModelOptionLabel(m: LlmModelSummary, providerName: string): string {
  const base = `${m.modelId} · ${providerName}`
  const wire = m.apiModel?.trim()
  if (wire && wire !== m.modelId) return `${base} → ${wire}`
  return base
}

const modelSelectOptions = computed<UiSelectOption[]>(() => {
  const opts: UiSelectOption[] = []
  for (const p of providers.value) {
    for (const m of models.value) {
      if (m.status !== 'enabled') continue
      opts.push({
        value: m.modelId,
        label: runtimeModelOptionLabel(m, p.displayName),
      })
    }
  }
  return opts.sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
})

async function saveGateway() {
  saveError.value = null
  if (form.maxTokensPerRequest > form.maxContextTokens) {
    saveError.value = '单次请求上限不得超过 Max Context'
    return
  }
  const turnsRaw = form.budgetMaxModelTurns.trim()
  const turns: number | null =
    turnsRaw === '' ? null : Number(turnsRaw)
  if (turns !== null && (!Number.isFinite(turns) || turns < 1)) {
    saveError.value = '模型回合上限须为正整数或留空（表示不设）'
    return
  }
  saving.value = true
  try {
    const patch: Record<string, unknown> = {
      defaultProviderId:
        form.defaultProviderId === OPT_NONE ? null : form.defaultProviderId.trim() || null,
      defaultModelId: form.defaultModelId === OPT_NONE ? null : form.defaultModelId.trim() || null,
      defaultInferenceModel: form.defaultInferenceModel.trim(),
      scenarioChatModel: form.scenarioChatModel.trim(),
      scenarioTradingModel: form.scenarioTradingModel.trim(),
      scenarioRiskModel: form.scenarioRiskModel.trim(),
      maxContextTokens: Number(form.maxContextTokens),
      maxOutputTokens: Number(form.maxOutputTokens),
      timeoutSec: Number(form.timeoutSec),
      fallbackOnPrimaryFailure: form.fallbackOnPrimaryFailure,
      fallbackOnTimeout: form.fallbackOnTimeout,
      downgradePeakTraffic: form.downgradePeakTraffic,
      fallbackModel: form.fallbackModel.trim(),
      maxTokensPerRequest: Number(form.maxTokensPerRequest),
      dailyTokenBudgetM: Number(form.dailyTokenBudgetM),
      rateLimitRpm: Number(form.rateLimitRpm),
      orchestrationExecutionBudget: {
        maxToolCallsPerExecution: Number(form.budgetMaxToolCalls),
        maxOrchestrationStepsPerExecution: Number(form.budgetMaxOrchestrationSteps),
        maxModelTurnsPerExecution: turns,
      },
    }
    const next = await patchAiGatewayDefaults(patch)
    applyDefaults(next)
    saveGatewayTipRef.value?.show('已保存')
  } catch (e) {
    saveError.value = e instanceof AppError ? e.message : '保存失败'
    if (e instanceof AppError && (e.status === 409 || e.status === 422)) {
      void loadAll()
    }
  } finally {
    saving.value = false
  }
}

async function deleteProviderRow(p: LlmProviderSummary) {
  providerPendingDelete.value = p
  providerDeleteConfirmOpen.value = true
}

function cancelProviderDelete() {
  providerDeleteConfirmOpen.value = false
  providerPendingDelete.value = null
}

async function confirmedDeleteProvider() {
  const p = providerPendingDelete.value
  if (!p) return
  providerDeleteConfirmOpen.value = false
  providerPendingDelete.value = null
  providerDeleteError.value = null
  deletingProviderId.value = p.providerId
  try {
    await deleteAiProvider(p.providerId)
    toastSuccess(`已删除 Provider ${p.providerId}`)
    await loadAll()
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '删除失败'
    providerDeleteError.value = { providerId: p.providerId, message: msg }
    if (e instanceof AppError && e.status === 409) {
      await loadAll()
    }
  } finally {
    deletingProviderId.value = null
  }
}

async function runProbe(pid: string) {
  probeByProvider.value = { ...probeByProvider.value, [pid]: '…' }
  try {
    const r = await probeAiProviderHealth(pid)
    probeByProvider.value = {
      ...probeByProvider.value,
      [pid]: `${r.ok ? 'ok' : 'fail'} · ${r.latencyMs}ms · ${r.message ?? ''}`,
    }
  } catch (e) {
    probeByProvider.value = {
      ...probeByProvider.value,
      [pid]: e instanceof AppError ? e.message : '探针失败',
    }
  }
}

function openProviderModal() {
  providerModalMode.value = 'create'
  editingProvider.value = null
  newProviderVendorPreset.value = 'openai'
  newProviderCustomDisplayName.value = ''
  newProviderDisplayName.value = ''
  newProviderBaseUrl.value = DEFAULT_BASE_URL_BY_CATALOG.openai
  newProviderSecretRef.value = ''
  providerCreateError.value = null
  providerModalOpen.value = true
}

function openEditProviderModal(row: LlmProviderSummary) {
  providerModalMode.value = 'edit'
  editingProvider.value = row
  newProviderDisplayName.value = row.displayName
  newProviderBaseUrl.value = row.baseUrl
  newProviderSecretRef.value = ''
  providerCreateError.value = null
  providerModalOpen.value = true
}

function onVendorPresetChange(preset: LlmVendorCatalogKind) {
  newProviderVendorPreset.value = preset
  if (preset !== 'none') {
    newProviderBaseUrl.value = DEFAULT_BASE_URL_BY_CATALOG[preset]
  }
}

function onVendorPresetSelect(value: string | number | null) {
  const preset = String(value ?? 'openai') as LlmVendorCatalogKind
  if (preset === 'openai' || preset === 'anthropic' || preset === 'deepseek' || preset === 'none') {
    onVendorPresetChange(preset)
  }
}

function onNewModelEnabledSwitch(checked: boolean) {
  newModelStatus.value = checked ? 'enabled' : 'disabled'
}

async function restoreRuntimeFromServer() {
  saveError.value = null
  try {
    const def = await getAiGatewayDefaults()
    applyDefaults(def)
    toastSuccess('已恢复为服务端当前配置')
  } catch (e) {
    saveError.value = e instanceof AppError ? e.message : '恢复失败'
  }
}

function openAddModelModal(row: LlmProviderSummary) {
  modelModalParent.value = row
  modelCreateError.value = null
  newModelId.value = ''
  newModelApiModel.value = ''
  newModelStatus.value = 'enabled'
  newModelContextWindow.value = ''
  newModelProviderId.value = row.providerId
  modelModalOpen.value = true
  if (!expandedProviderIds.value.includes(row.providerId)) {
    expandedProviderIds.value = [...expandedProviderIds.value, row.providerId]
  }
}

async function toggleModelEnabled(m: LlmModelSummary, enabled: boolean) {
  try {
    await patchAiModel(m.modelId, { status: enabled ? 'enabled' : 'disabled' })
    await loadAll()
    reconcileRuntimeFormWithCatalog()
  } catch (e) {
    toastError(e instanceof AppError ? e.message : '更新失败')
  }
}

async function submitNewModel() {
  const parent = modelModalParent.value
  const pid = (parent?.providerId ?? newModelProviderId.value).trim()
  const mid = newModelId.value.trim()
  if (!pid || !mid) {
    modelCreateError.value = '请填写 modelId'
    return
  }
  const cwRaw = newModelContextWindow.value.trim()
  let contextWindowTokens: number | null | undefined
  if (cwRaw === '') contextWindowTokens = undefined
  else {
    const n = Number(cwRaw)
    if (!Number.isFinite(n) || n < 0) {
      modelCreateError.value = 'contextWindowTokens 须为非负数字或留空'
      return
    }
    contextWindowTokens = Math.trunc(n)
  }
  const apiRaw = newModelApiModel.value.trim()
  modelCreating.value = true
  modelCreateError.value = null
  try {
    await createAiModel({
      providerId: pid,
      modelId: mid,
      status: newModelStatus.value.trim() || 'enabled',
      ...(contextWindowTokens !== undefined ? { contextWindowTokens } : {}),
      ...(apiRaw ? { apiModel: apiRaw } : {}),
    })
    modelModalOpen.value = false
    toastSuccess(`已创建模型 ${mid}`)
    await loadAll()
  } catch (e) {
    modelCreateError.value = e instanceof AppError ? e.message : '创建失败'
  } finally {
    modelCreating.value = false
  }
}

async function submitNewProvider() {
  const bu = newProviderBaseUrl.value.trim()
  if (!bu) {
    providerCreateError.value = 'Base URL 必填'
    return
  }
  providerCreating.value = true
  providerCreateError.value = null
  try {
    const ref = newProviderSecretRef.value.trim()
    if (providerModalMode.value === 'edit' && editingProvider.value) {
      await patchAiProvider(editingProvider.value.providerId, {
        displayName: newProviderDisplayName.value.trim() || editingProvider.value.displayName,
        baseUrl: bu,
        ...(ref ? { secretRef: ref } : {}),
      })
      providerModalOpen.value = false
      toastSuccess('已保存厂商')
    } else {
      const preset = newProviderVendorPreset.value
      const dn =
        preset !== 'none'
          ? LLM_VENDOR_CATALOG_LABELS[preset]
          : newProviderCustomDisplayName.value.trim()
      if (!dn) {
        providerCreateError.value = '请填写厂商名称'
        return
      }
      const created = await createAiProvider({
        displayName: dn,
        baseUrl: bu,
        ...(ref ? { secretRef: ref } : {}),
      })
      providerCatalogKindById.value = {
        ...providerCatalogKindById.value,
        [created.providerId]: preset,
      }
      providerModalOpen.value = false
      toastSuccess('已添加厂商')
      expandedProviderIds.value = [...expandedProviderIds.value, created.providerId]
    }
    await loadAll()
  } catch (e) {
    providerCreateError.value = e instanceof AppError ? e.message : '保存失败'
  } finally {
    providerCreating.value = false
  }
}

async function deleteModelRow(m: LlmModelSummary) {
  modelPendingDelete.value = m
  modelDeleteConfirmOpen.value = true
}

function cancelModelDelete() {
  modelDeleteConfirmOpen.value = false
  modelPendingDelete.value = null
}

async function confirmedDeleteModel() {
  const m = modelPendingDelete.value
  if (!m) return
  modelDeleteConfirmOpen.value = false
  modelPendingDelete.value = null
  deletingModelId.value = m.modelId
  try {
    await deleteAiModel(m.modelId)
    toastSuccess(`已删除 ${m.modelId}`)
    await loadAll()
    reconcileRuntimeFormWithCatalog()
  } catch (e) {
    toastError(e instanceof AppError ? e.message : '删除失败')
    if (e instanceof AppError && e.status === 409) {
      await loadAll()
    }
  } finally {
    deletingModelId.value = null
  }
}

</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="模型配置"
      description="模型目录、运行时默认与网关路由；与提示词治理、运行场景联调时以此为准。"
      dev-meta="pageId · ai.settings · /ai-settings"
    />

    <div
      v-if="loadError"
      class="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-200"
      role="alert"
    >
      {{ loadError }}
    </div>

    <template v-if="!loading && !loadError">
      <div class="flex flex-wrap items-end justify-between gap-3 border-b border-slate-800 pb-2">
        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class="admin-seg"
            :class="
              aiSettingsTab === 'catalog'
                ? 'admin-seg-active'
                : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
            "
            @click="setAiSettingsTab('catalog')"
          >
            厂商与模型
          </button>
          <button
            type="button"
            class="admin-seg"
            :class="
              aiSettingsTab === 'runtime'
                ? 'admin-seg-active'
                : 'admin-seg-idle hover:bg-slate-800/65 hover:text-slate-200'
            "
            @click="setAiSettingsTab('runtime')"
          >
            使用策略
          </button>
        </div>
        <UiButton type="button" size="sm" variant="secondary" :disabled="loading" @click="loadAll">
          重新加载
        </UiButton>
      </div>

      <div v-show="aiSettingsTab === 'catalog'" class="space-y-4">
        <p
          v-if="providerDeleteError"
          class="rounded border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-xs text-rose-200"
          role="alert"
        >
          厂商 {{ providerDeleteError.providerId }}：{{ providerDeleteError.message }}
        </p>
        <AiSettingsCatalogPanel
          v-model:expanded-provider-ids="expandedProviderIds"
          :providers="providers"
          :models="models"
          :probe-by-provider="probeByProvider"
          :deleting-provider-id="deletingProviderId"
          :deleting-model-id="deletingModelId"
          @add-provider="openProviderModal"
          @edit-provider="openEditProviderModal"
          @delete-provider="deleteProviderRow"
          @probe="runProbe"
          @add-model="openAddModelModal"
          @toggle-model-enabled="toggleModelEnabled"
          @delete-model="deleteModelRow"
        />
      </div>

      <div v-show="aiSettingsTab === 'runtime'" class="space-y-6">
        <div
          v-if="providers.length === 0 || models.length === 0"
          class="rounded-lg border border-amber-500/35 bg-amber-500/10 px-4 py-3 text-sm leading-relaxed text-amber-100/90"
          role="status"
        >
          当前无可用模型目录，请先在「厂商与模型」添加并启用模型。
        </div>

        <div class="grid grid-cols-1 items-start gap-6 xl:grid-cols-2">
          <GatewayPolicyPanel
            class="min-w-0"
            :loading="loading"
            :intent-nlu-use-llm="gatewayPolicy.intentNluUseLlm"
            :intent-clarify-use-llm="gatewayPolicy.intentClarifyUseLlm"
            :telegram-llm-narrate="gatewayPolicy.telegramLlmNarrate"
            @applied="applyDefaults"
          />

          <MemoryRuntimeConfigPanel class="min-w-0" />
        </div>

        <div class="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
      <!-- 推理与路由 -->
      <section class="admin-panel h-full space-y-4 p-4 sm:p-5">
        <h2 class="text-sm font-medium text-white">推理与路由</h2>
        <UiSelect
          v-model="form.defaultInferenceModel"
          label="默认模型"
          placeholder="选择模型"
          :options="modelSelectOptions"
        />
        <div class="grid gap-4 sm:grid-cols-2">
          <UiSelect
            v-for="s in SCENARIO_FIELDS"
            :key="s.key"
            v-model="form[s.key]"
            :label="s.label"
            :options="modelSelectOptions"
          />
        </div>
      </section>

      <!-- Token 与超时 -->
      <section class="admin-panel h-full space-y-4 p-4 sm:p-5">
        <h2 class="text-sm font-medium text-white">Token 与超时</h2>
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">Max Context</label>
            <input
              v-model.number="form.maxContextTokens"
              type="number"
              min="1024"
              :class="numInputClass"
            />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">Max Output</label>
            <input
              v-model.number="form.maxOutputTokens"
              type="number"
              min="256"
              :class="numInputClass"
            />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">Timeout</label>
            <input v-model.number="form.timeoutSec" type="number" min="5" :class="numInputClass" />
          </div>
        </div>
      </section>

      <!-- 编排执行预算 -->
      <section class="admin-panel h-full space-y-4 p-4 sm:p-5">
        <h2 class="text-sm font-medium text-white">编排执行预算（orchestrationExecutionBudget）</h2>
        <p class="text-xs text-slate-500">
          与 OpenAPI / 后端校验一致：<code class="rounded bg-slate-900 px-1">maxToolCallsPerExecution</code>、
          <code class="rounded bg-slate-900 px-1">maxOrchestrationStepsPerExecution</code> 须 ≥ 1。
        </p>
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">每执行工具调用上限</label>
            <input
              v-model.number="form.budgetMaxToolCalls"
              type="number"
              min="1"
              :class="numInputClass"
            />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">每执行编排步数上限</label>
            <input
              v-model.number="form.budgetMaxOrchestrationSteps"
              type="number"
              min="1"
              :class="numInputClass"
            />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">每执行模型回合上限（可选）</label>
            <input
              v-model="form.budgetMaxModelTurns"
              type="text"
              inputmode="numeric"
              placeholder="留空表示不设"
              :class="numInputClass"
            />
          </div>
        </div>
      </section>
        </div>

        <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <!-- 降级 -->
      <section class="admin-panel h-full space-y-4 p-4 sm:p-5">
        <h2 class="text-sm font-medium text-white">降级</h2>
        <div class="grid gap-3 sm:grid-cols-2">
          <label class="flex cursor-pointer items-center justify-between gap-3 rounded-lg border border-slate-800/80 bg-slate-950/30 px-3 py-2.5 text-sm text-slate-300">
            <span>失败时切换</span>
            <UiSwitch v-model="form.fallbackOnPrimaryFailure" size="sm" aria-label="失败时切换" />
          </label>
          <label class="flex cursor-pointer items-center justify-between gap-3 rounded-lg border border-slate-800/80 bg-slate-950/30 px-3 py-2.5 text-sm text-slate-300">
            <span>超时时降级</span>
            <UiSwitch v-model="form.fallbackOnTimeout" size="sm" aria-label="超时时降级" />
          </label>
          <label class="flex cursor-pointer items-center justify-between gap-3 rounded-lg border border-slate-800/80 bg-slate-950/30 px-3 py-2.5 text-sm text-slate-300">
            <span>高峰期降级</span>
            <UiSwitch v-model="form.downgradePeakTraffic" size="sm" aria-label="高峰期降级" />
          </label>
        </div>
        <UiSelect
          v-model="form.fallbackModel"
          label="降级模型"
          :options="modelSelectOptions"
        />
      </section>

      <!-- 成本与限流 -->
      <section class="admin-panel h-full space-y-4 p-4 sm:p-5">
        <h2 class="text-sm font-medium text-white">成本与限流</h2>
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">单次请求上限</label>
            <input v-model.number="form.maxTokensPerRequest" type="number" min="1024" :class="numInputClass" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">单日预算</label>
            <input v-model.number="form.dailyTokenBudgetM" type="number" min="1" :class="numInputClass" />
          </div>
          <div>
            <label class="mb-1 block text-xs font-medium text-slate-400">RPM 上限</label>
            <input v-model.number="form.rateLimitRpm" type="number" min="1" :class="numInputClass" />
          </div>
        </div>
      </section>
        </div>

        <p v-if="saveError" class="text-sm text-rose-300" role="alert">{{ saveError }}</p>

        <div
          class="sticky bottom-0 z-10 flex flex-wrap items-center gap-2 border-t border-slate-800 bg-slate-950/90 py-3 backdrop-blur-sm"
        >
          <UiAnchorTip ref="saveGatewayTipRef" tone="success">
            <UiButton type="button" :loading="saving" @click="saveGateway">保存</UiButton>
          </UiAnchorTip>
          <UiButton type="button" variant="secondary" :disabled="saving" @click="restoreRuntimeFromServer">
            恢复默认
          </UiButton>
        </div>
      </div>
    </template>

    <UiModal
      v-model:open="modelModalOpen"
      :title="modelModalParent ? `添加模型 · ${modelModalParent.displayName}` : '添加模型'"
      :show-default-close="false"
    >
      <div v-if="modelModalParent" class="space-y-3">
        <UiInput
          v-model="newModelId"
          label="modelId"
          placeholder="登记全局唯一的 modelId（catalog 主键）"
        />
        <UiInput
          v-model="newModelApiModel"
          label="apiModel（可选）"
          placeholder="留空则对端 model 字段使用 modelId"
        />
        <p class="text-xs leading-relaxed text-slate-500">
          不同厂商可共用同一上游 model 串：请为各厂商登记不同的 modelId，并在 apiModel 中填写实际传给对端的
          model 值。
        </p>
        <p v-if="showVolcModelIdHint" class="text-xs leading-relaxed text-slate-500">
          火山方舟：modelId 须与控制台 Endpoint 中已开通的推理接入点 ID 一致；baseUrl 填控制台
          Endpoint 根（如 https://ark.cn-beijing.volces.com）。
        </p>
        <label class="flex cursor-pointer items-center justify-between gap-3 text-sm text-slate-300">
          <span>创建后启用</span>
          <UiSwitch
            :model-value="newModelStatus === 'enabled'"
            size="sm"
            aria-label="创建后启用"
            @update:model-value="onNewModelEnabledSwitch"
          />
        </label>
        <UiInput
          v-model="newModelContextWindow"
          label="contextWindowTokens（可选）"
          placeholder="留空则服务端默认"
        />
        <p v-if="modelCreateError" class="text-sm text-rose-300">{{ modelCreateError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" @click="modelModalOpen = false">取消</UiButton>
        <UiButton type="button" :loading="modelCreating" @click="submitNewModel">添加</UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="providerModalOpen"
      :title="
        providerModalMode === 'create'
          ? '添加厂商'
          : `修改 · ${editingProvider?.displayName ?? ''}`
      "
      :show-default-close="false"
    >
      <div class="space-y-3">
        <template v-if="providerModalMode === 'create'">
          <UiSelect
            :model-value="newProviderVendorPreset"
            label="厂商"
            placeholder="选择厂商 / 接入底座"
            :options="LLM_VENDOR_CATALOG_OPTIONS"
            @update:model-value="onVendorPresetSelect"
          />
          <UiInput
            v-if="newProviderVendorPreset === 'none'"
            v-model="newProviderCustomDisplayName"
            label="自定义厂商名称"
            placeholder="自定义厂商名称"
          />
        </template>
        <template v-else>
          <UiInput v-model="newProviderDisplayName" label="展示名称" placeholder="展示名称" />
        </template>
        <UiInput
          v-model="newProviderBaseUrl"
          label="Base URL"
          placeholder="https://api.example.com/v1"
        />
        <UiInput
          v-model="newProviderSecretRef"
          :label="providerModalMode === 'create' ? '密钥' : '密钥（留空则不修改）'"
          type="password"
          placeholder="KMS 引用或 API Key / 环境变量名"
          autocomplete="new-password"
        />
        <p class="text-xs leading-relaxed text-slate-500">
          推荐环境变量名；Phase1 亦支持 API Key 明文入库。
        </p>
        <p v-if="providerCreateError" class="text-sm text-rose-300">{{ providerCreateError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" @click="providerModalOpen = false">取消</UiButton>
        <UiButton type="button" :loading="providerCreating" @click="submitNewProvider">
          {{ providerModalMode === 'create' ? '添加' : '保存' }}
        </UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="providerDeleteConfirmOpen"
      title="确认删除 Provider"
      :show-default-close="false"
      description="将从目录移除该 Provider；数据库对下属模型为级联删除。网关 defaults 不会自动改写。"
    >
      <div v-if="providerPendingDelete" class="space-y-3">
        <p class="text-sm text-slate-300">
          即将删除
          <span class="font-mono text-white">{{ providerPendingDelete.providerId }}</span>
          <span class="text-slate-500">（{{ providerPendingDelete.displayName }}）</span>
        </p>
        <ul class="list-disc space-y-2 pl-4 text-sm leading-relaxed text-slate-400">
          <li v-if="modelCountForPendingProvider > 0">
            当前列表显示其下 {{ modelCountForPendingProvider }} 条模型目录，将随 CASCADE 一并删除。
          </li>
          <li v-else>当前列表中该 Provider 下暂无模型行；仍请确认无其他环境依赖。</li>
          <li>若网关仍引用 defaultProviderId 或相关 modelId，请在删除后检查并保存网关配置。</li>
        </ul>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" @click="cancelProviderDelete">取消</UiButton>
        <UiButton variant="danger" type="button" @click="confirmedDeleteProvider">确认删除</UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="modelDeleteConfirmOpen"
      title="确认删除模型"
      :show-default-close="false"
      description="删除后不可恢复。若网关默认值仍引用该 modelId，请随后调整并保存。"
    >
      <p v-if="modelPendingDelete" class="text-sm text-slate-300">
        即将移除目录项
        <span class="font-mono text-white">{{ modelPendingDelete.modelId }}</span>
      </p>
      <template #footer>
        <UiButton variant="ghost" type="button" @click="cancelModelDelete">取消</UiButton>
        <UiButton variant="danger" type="button" @click="confirmedDeleteModel">确认删除</UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>
