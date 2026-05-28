<!--
作者: 杨永的Agent
日期: 2026-05-26
修改功能: **I05** 实例参数可编辑保存 · **I04** 登记/解绑子账户（真实 API 联调）
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 详情顶栏 **DELETE** 实例 + **UiModal** 二次确认（I06 · 成功后回列表）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 基础信息去掉冗长时点说明（表头已由 **AdminTimeTh** 后缀 `(UTC+8)`/`(UTC)` 标注）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 时点与顶栏 UTC+8 / UTC 模式一致（FE_HANDOFF）
作者: 杨永的Agent
日期: 2026-05-16
修改功能: 运行控制二次确认改为 UiModal（替换原生 confirm）；接口失败在弹窗内展示错误
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 运行控制 Start / Resume / Pause / Stop 统一二次确认（confirm）
作者: 杨永的Agent
日期: 2026-05-14
修改功能: **G01 / R01–R06 / L01–L03**（接续 FE_HANDOFF）：门禁横幅与轮询、单实例 Runtime、日志 Tab；**FR-AM-I03** 详情分区与类型对齐 **`AdminAgentInstanceItem`**
作者: 杨永的Agent
日期: 2026-05-13
修改功能: Agent 实例详情 GET `/instances/{instanceId}`；移除旧「交易绑定运维」入口文案依赖，绑定摘要集中在详情
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 移除「Agent 运行时探针」快捷入口（联调页已下线）
-->
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import AgentInstanceLogsTabs from '@/features/agents/AgentInstanceLogsTabs.vue'
import GlobalAgentGateBanner from '@/features/agents/GlobalAgentGateBanner.vue'
import {
  mapAgentRowToListVm,
} from '@/entities/agents/agent-instance-list-vm'
import {
  getGlobalAgentGate,
  postAgentInstanceRuntimeAction,
  type AgentRuntimeControlAction,
  type GlobalAgentGateResponse,
} from '@/shared/api/agent-agent-control'
import {
  bindInstanceSubaccount,
  deleteAgentInstance,
  formatAgentInstanceDeleteError,
  formatAgentInstanceWriteError,
  getAgentInstance,
  patchAgentInstance,
  unbindInstanceSubaccount,
  type AgentInstanceRow,
  type InstanceOverridesPatch,
  type TradingApiBindingStatus,
} from '@/shared/api/agent-instances'
import { AppError } from '@/shared/api/errors'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import { showAdminPageDevMeta } from '@/shared/config/constants'
import { zhAgentState, zhRuntimeState, zhSubAccountStatus } from '@/shared/copy/zh-agent-labels'
import { formatIsoTime } from '@/shared/copy/zh-runtime'
import {
  agentStateTagClass,
  formatInstanceAt,
  runtimeStateTagClass,
} from '@/shared/utils/agent-instance-ui'
import { buildObservabilitySearch } from '@/shared/utils/observability-deep-link'
import AdminPage from '@/shared/ui/AdminPage.vue'
import { AdminPageHeader, UiButton, UiInput, UiModal, UiSelect, type UiSelectOption } from '@/shared/ui'

const route = useRoute()
const router = useRouter()

const row = ref<AgentInstanceRow | null>(null)
const loading = ref(false)
const loadError = ref<string | null>(null)

const instanceId = computed(() => {
  const raw = route.params.instanceId
  return typeof raw === 'string' ? raw : Array.isArray(raw) ? raw[0] ?? '' : ''
})

const listVm = computed(() => (row.value ? mapAgentRowToListVm(row.value) : null))

function bindingBadgeClass(s: TradingApiBindingStatus): string {
  return s === 'BOUND'
    ? 'border-emerald-500/40 bg-emerald-500/15 text-emerald-200'
    : 'border-slate-600 bg-slate-800/80 text-slate-400'
}

async function load() {
  const id = instanceId.value.trim()
  if (!id) {
    loadError.value = '缺少 instanceId'
    return
  }
  loading.value = true
  loadError.value = null
  row.value = null
  try {
    row.value = await getAgentInstance(id)
  } catch (e) {
    loadError.value = e instanceof AppError ? e.message : e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

const runtimeGate = ref<GlobalAgentGateResponse | null>(null)
let gatePollTimer: ReturnType<typeof setInterval> | null = null

async function refreshRuntimeGate() {
  try {
    runtimeGate.value = await getGlobalAgentGate()
  } catch {
    /* 静默：横幅仍有独立轮询 */
  }
}

const startResumeBlocked = computed(() => {
  const g = runtimeGate.value
  if (!g) return false
  return !g.globalAgentSwitchOn || g.opsSuspended
})

const runtimeBusy = ref(false)
const runtimeActionBusy = ref<AgentRuntimeControlAction | null>(null)

function runtimeDisabled(action: AgentRuntimeControlAction): boolean {
  if (loading.value || runtimeBusy.value || runtimeConfirmOpen.value) return true
  if ((action === 'start' || action === 'resume') && startResumeBlocked.value) return true
  return false
}

function runtimeLoading(action: AgentRuntimeControlAction): boolean {
  return runtimeBusy.value && runtimeActionBusy.value === action
}

const runtimeConfirmOpen = ref(false)
const pendingRuntimeAction = ref<AgentRuntimeControlAction | null>(null)
const runtimeConfirmError = ref<string | null>(null)

const instanceDeleteOpen = ref(false)
const instanceDeleteSubmitting = ref(false)
const instanceDeleteError = ref<string | null>(null)

const runtimeConfirmMeta = computed(() => {
  const action = pendingRuntimeAction.value
  if (!action) {
    return {
      title: '确认操作',
      description: '',
      primaryLabel: '确认',
    }
  }
  const titles: Record<AgentRuntimeControlAction, string> = {
    start: '确认 Start',
    resume: '确认 Resume',
    pause: '确认 Pause',
    stop: '确认 Stop',
  }
  const descriptions: Record<AgentRuntimeControlAction, string> = {
    start: '实例将从停止态进入可调度；实际仍受全局门禁与后端策略约束。',
    resume: '实例将从暂停态恢复运行；实际仍受全局门禁与后端策略约束。',
    pause: '实例将进入暂停态，新执行将按平台策略受限（在飞请求可能继续收尾）。',
    stop: '实例将停止运行；可按 Start 再次拉起。',
  }
  const primaryLabel: Record<AgentRuntimeControlAction, string> = {
    start: '确认 Start',
    resume: '确认 Resume',
    pause: '确认 Pause',
    stop: '确认 Stop',
  }
  return {
    title: titles[action],
    description: descriptions[action],
    primaryLabel: primaryLabel[action],
  }
})

watch(runtimeConfirmOpen, (open) => {
  if (!open && !runtimeBusy.value) {
    pendingRuntimeAction.value = null
    runtimeConfirmError.value = null
  }
})

function cancelRuntimeConfirm() {
  if (runtimeBusy.value) return
  runtimeConfirmOpen.value = false
}

async function submitRuntimeConfirm() {
  const action = pendingRuntimeAction.value
  const id = instanceId.value.trim()
  if (!action || !id) return
  runtimeConfirmError.value = null
  runtimeBusy.value = true
  runtimeActionBusy.value = action
  try {
    row.value = await postAgentInstanceRuntimeAction(id, action)
    runtimeConfirmOpen.value = false
    pendingRuntimeAction.value = null
  } catch (e) {
    runtimeConfirmError.value =
      e instanceof AppError ? [e.code, e.message].filter(Boolean).join(' · ') : '操作失败'
  } finally {
    runtimeBusy.value = false
    runtimeActionBusy.value = null
  }
}

function openInstanceDeleteConfirm() {
  if (runtimeConfirmOpen.value || instanceDeleteSubmitting.value) return
  instanceDeleteError.value = null
  instanceDeleteOpen.value = true
}

function cancelInstanceDelete() {
  if (instanceDeleteSubmitting.value) return
  instanceDeleteOpen.value = false
  instanceDeleteError.value = null
}

async function confirmedInstanceDelete() {
  const id = instanceId.value.trim()
  if (!id) return
  instanceDeleteSubmitting.value = true
  instanceDeleteError.value = null
  try {
    await deleteAgentInstance(id)
    instanceDeleteOpen.value = false
    await router.replace({ path: '/agents/instances' })
  } catch (e) {
    instanceDeleteError.value = formatAgentInstanceDeleteError(e)
  } finally {
    instanceDeleteSubmitting.value = false
  }
}

function runRuntime(action: AgentRuntimeControlAction) {
  const id = instanceId.value.trim()
  if (!id) return
  if ((action === 'start' || action === 'resume') && startResumeBlocked.value) {
    window.alert('当前全局门禁禁止 Start / Resume（见顶部 G01 横幅）。')
    return
  }
  if (runtimeConfirmOpen.value) return
  pendingRuntimeAction.value = action
  runtimeConfirmError.value = null
  runtimeConfirmOpen.value = true
}

watch(instanceId, () => {
  void load()
})

onMounted(() => {
  void load()
  void refreshRuntimeGate()
  gatePollTimer = setInterval(refreshRuntimeGate, 30_000)
})

onUnmounted(() => {
  if (gatePollTimer) clearInterval(gatePollTimer)
})

const observabilityExecutionHref = computed(() => {
  const uid = row.value?.telegramUserId?.trim()
  if (!uid) return '/observability'
  return `/observability${buildObservabilitySearch({ userId: uid, tab: 'execution' })}`
})

/** 执行记录页 keyword：与列表同源 Observability API，`q` 走 keyword */
const executionsKeywordHref = computed(() => {
  const uid = row.value?.telegramUserId?.trim()
  if (!uid) return '/runtime/executions'
  const sp = new URLSearchParams()
  sp.set('q', uid)
  return `/runtime/executions?${sp.toString()}`
})

const masterUserIdLine = computed(() => {
  const u = row.value?.userId?.trim()
  return u || null
})

const overridesPreferredLanguage = ref('')
const overridesCooldownSec = ref('')
const overridesSymbolPreference = ref('')
const overridesVoiceEnabled = ref<'unset' | 'true' | 'false'>('unset')
const overridesSaving = ref(false)
const overridesError = ref<string | null>(null)

const voiceEnabledOptions: UiSelectOption[] = [
  { value: 'unset', label: '未设置' },
  { value: 'true', label: '开启' },
  { value: 'false', label: '关闭' },
]

function syncOverridesFormFromRow() {
  const o = row.value?.instanceOverrides
  overridesPreferredLanguage.value =
    typeof o?.preferredLanguage === 'string' ? o.preferredLanguage : ''
  const cd = o?.cooldownPreferenceSec
  overridesCooldownSec.value =
    typeof cd === 'number' && Number.isFinite(cd) ? String(Math.trunc(cd)) : ''
  overridesSymbolPreference.value =
    typeof o?.symbolPreference === 'string' ? o.symbolPreference : ''
  const ve = o?.voiceOutputEnabled
  if (ve === true) overridesVoiceEnabled.value = 'true'
  else if (ve === false) overridesVoiceEnabled.value = 'false'
  else overridesVoiceEnabled.value = 'unset'
}

watch(row, () => syncOverridesFormFromRow(), { immediate: true })

async function saveInstanceOverrides() {
  const id = instanceId.value.trim()
  if (!id) return
  const patch: InstanceOverridesPatch = {}
  const lang = overridesPreferredLanguage.value.trim()
  if (lang) patch.preferredLanguage = lang
  const sym = overridesSymbolPreference.value.trim()
  if (sym) patch.symbolPreference = sym
  const cdRaw = overridesCooldownSec.value.trim()
  if (cdRaw) {
    const n = Number(cdRaw)
    if (!Number.isFinite(n) || n < 0 || n > 86400) {
      overridesError.value = 'cooldownPreferenceSec 须为 0～86400 的整数'
      return
    }
    patch.cooldownPreferenceSec = Math.trunc(n)
  }
  if (overridesVoiceEnabled.value === 'true') patch.voiceOutputEnabled = true
  else if (overridesVoiceEnabled.value === 'false') patch.voiceOutputEnabled = false

  if (Object.keys(patch).length === 0) {
    overridesError.value = '请至少填写一项实例参数'
    return
  }

  overridesSaving.value = true
  overridesError.value = null
  try {
    row.value = await patchAgentInstance(id, { instanceOverrides: patch })
    syncOverridesFormFromRow()
    adminToastSuccess('已保存实例参数')
  } catch (e) {
    const msg = formatAgentInstanceWriteError(e)
    overridesError.value = msg
    adminToastError(msg)
  } finally {
    overridesSaving.value = false
  }
}

const bindSubAccountInput = ref('')
const bindSubmitting = ref(false)
const bindError = ref<string | null>(null)

const unbindOpen = ref(false)
const unbindSubmitting = ref(false)
const unbindError = ref<string | null>(null)

watch(row, () => {
  bindSubAccountInput.value = row.value?.exchangeSubAccountUserId?.toString().trim() ?? ''
})

async function submitBindSubaccount() {
  const id = instanceId.value.trim()
  const sub = bindSubAccountInput.value.trim()
  if (!id || !sub) {
    bindError.value = '请填写子账户 ID'
    return
  }
  bindSubmitting.value = true
  bindError.value = null
  try {
    row.value = await bindInstanceSubaccount(id, { subAccountId: sub })
    bindSubAccountInput.value = row.value.exchangeSubAccountUserId?.toString().trim() ?? sub
    adminToastSuccess('已登记子账户')
  } catch (e) {
    const msg = formatAgentInstanceWriteError(e)
    bindError.value = msg
    adminToastError(msg)
  } finally {
    bindSubmitting.value = false
  }
}

function openUnbindConfirm() {
  unbindError.value = null
  unbindOpen.value = true
}

function cancelUnbind() {
  if (unbindSubmitting.value) return
  unbindOpen.value = false
  unbindError.value = null
}

async function confirmedUnbind() {
  const id = instanceId.value.trim()
  if (!id) return
  unbindSubmitting.value = true
  unbindError.value = null
  try {
    await unbindInstanceSubaccount(id)
    unbindOpen.value = false
    row.value = await getAgentInstance(id)
    adminToastSuccess('已解绑 API 托管')
  } catch (e) {
    const msg = formatAgentInstanceWriteError(e)
    unbindError.value = msg
    adminToastError(msg)
  } finally {
    unbindSubmitting.value = false
  }
}

const appendix82Json = computed(() => {
  const o = row.value?.appendix82
  if (!o || typeof o !== 'object' || Object.keys(o).length === 0) return null
  try {
    return JSON.stringify(o, null, 2)
  } catch {
    return String(o)
  }
})

const rowStyles = {
  dt: 'w-[168px] shrink-0 py-2 text-xs font-medium uppercase tracking-wide text-slate-500 sm:w-[188px]',
  dd: 'min-w-0 py-2 text-sm text-slate-200',
} as const
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="实例详情"
      :subline="instanceId"
      dev-meta="pageId · ai.agents-instance-detail"
      :crumbs="[
        { label: '实例管理', to: '/agents/instances' },
        { label: '详情' },
      ]"
    >
      <template #actions>
        <UiButton type="button" variant="secondary" size="sm" :loading="loading" @click="load">
          刷新
        </UiButton>
        <UiButton
          v-if="row"
          type="button"
          variant="danger"
          size="sm"
          :disabled="loading || instanceDeleteSubmitting"
          @click="openInstanceDeleteConfirm"
        >
          删除实例
        </UiButton>
      </template>
    </AdminPageHeader>

    <GlobalAgentGateBanner />

    <div
      v-if="loadError"
      class="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-sm text-amber-200"
      role="alert"
    >
      {{ loadError }}
    </div>

    <div
      v-else-if="loading && !row"
      class="rounded-lg border border-slate-800 bg-slate-950/40 px-4 py-14 text-center text-sm text-slate-500"
    >
      加载中…
    </div>

    <template v-else-if="row && listVm">
      <!-- 概览（I03 分区 · 状态摘要） -->
      <section class="admin-panel overflow-hidden p-4 sm:p-5">
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="min-w-0 flex-1 space-y-3">
            <div class="flex flex-wrap items-center gap-2">
              <span
                class="inline-flex rounded border px-2 py-0.5 text-xs font-medium"
                :class="agentStateTagClass(listVm.agentState)"
              >
                {{ zhAgentState(listVm.agentState) }}
              </span>
              <span
                class="inline-flex rounded border px-2 py-0.5 text-xs font-medium"
                :class="runtimeStateTagClass(listVm.runtimeState)"
              >
                {{ zhRuntimeState(listVm.runtimeState) }}
              </span>
              <span
                class="inline-flex rounded border px-2 py-0.5 text-xs font-medium"
                :class="bindingBadgeClass(row.tradingApiBindingStatus)"
              >
                {{ row.tradingApiBindingStatus === 'BOUND' ? '托管 API 已绑定' : '未绑定托管 API' }}
              </span>
            </div>
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-slate-500">模板（钉扎版本）</p>
              <p class="mt-1 text-lg font-semibold tracking-tight text-white">
                {{ listVm.templateDisplayName }}
                <span class="font-mono text-base font-normal text-slate-500">v{{ listVm.templateVersion }}</span>
              </p>
              <p class="mt-1 font-mono text-xs text-slate-500">templateId · {{ row.templateId }}</p>
            </div>
            <p v-if="showAdminPageDevMeta && row.agentState" class="font-mono text-[11px] text-slate-600">
              API agentState={{ row.agentState }} · runtimeState={{ row.runtimeState ?? '—' }}
            </p>
          </div>
          <div class="flex w-full shrink-0 flex-col gap-2 sm:flex-row lg:w-auto lg:flex-col">
            <RouterLink
              class="inline-flex items-center justify-center rounded-md bg-emerald-600 px-4 py-2.5 text-center text-sm font-medium text-white transition-colors hover:bg-emerald-500"
              :to="observabilityExecutionHref"
            >
              执行链路协查
            </RouterLink>
            <RouterLink
              class="inline-flex items-center justify-center rounded-md border border-slate-600 bg-slate-900 px-4 py-2.5 text-center text-sm font-medium text-slate-200 transition-colors hover:border-slate-500 hover:bg-slate-800"
              :to="executionsKeywordHref"
            >
              执行记录（关键字）
            </RouterLink>
          </div>
        </div>
      </section>

      <!-- 基础信息 -->
      <section class="admin-panel overflow-hidden p-4 sm:p-5">
        <h2 class="mb-3 text-[15px] font-semibold text-white">基础信息</h2>
        <dl class="divide-y divide-slate-800">
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">channel</dt>
            <dd :class="`${rowStyles.dd} font-mono text-slate-400`">{{ row.channel }}</dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">telegramUserId</dt>
            <dd :class="`${rowStyles.dd} font-mono`">{{ row.telegramUserId }}</dd>
          </div>
          <div v-if="masterUserIdLine" class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">userId（主站）</dt>
            <dd :class="`${rowStyles.dd} font-mono text-slate-300`">{{ masterUserIdLine }}</dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">账号摘要</dt>
            <dd :class="rowStyles.dd">{{ listVm.userEmailMasked }}</dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">最后阻断原因</dt>
            <dd :class="`${rowStyles.dd} text-slate-300`">{{ listVm.lastProductBlockReason }}</dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">createdAt</dt>
            <dd :class="`${rowStyles.dd} text-slate-400`">{{ formatIsoTime(row.createdAt) }}</dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">updatedAt</dt>
            <dd :class="`${rowStyles.dd} text-slate-400`">{{ formatIsoTime(row.updatedAt) }}</dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">lastActiveAt</dt>
            <dd :class="`${rowStyles.dd} font-mono text-slate-400`">{{ formatInstanceAt(row.lastActiveAt) }}</dd>
          </div>
        </dl>
      </section>

      <!-- 绑定（无 Secret · I03/I04） -->
      <section class="admin-panel overflow-hidden p-4 sm:p-5">
        <h2 class="mb-1 text-[15px] font-semibold text-white">绑定与交易 API</h2>
        <p class="mb-4 max-w-3xl text-xs leading-relaxed text-slate-500">
          控制台可登记 <code class="rounded bg-slate-800 px-1">exchangeSubAccountUserId</code>；API 密钥须在 Telegram / Deeplink 完成托管。解绑仅删除托管行，实例保留。
        </p>
        <dl class="divide-y divide-slate-800">
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">子账户列表态</dt>
            <dd :class="rowStyles.dd">
              <span class="text-slate-200">{{ zhSubAccountStatus(listVm.subAccountStatus) }}</span>
              <span class="ml-2 font-mono text-xs text-slate-500">({{ row.subAccountStatus ?? '—' }})</span>
            </dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">exchangeSubAccountUserId</dt>
            <dd :class="`${rowStyles.dd} font-mono text-slate-300`">
              {{ row.exchangeSubAccountUserId?.toString().trim() ? row.exchangeSubAccountUserId : '—' }}
            </dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">tradingApiBindingStatus</dt>
            <dd :class="rowStyles.dd">
              <span
                class="inline-flex rounded border px-2 py-0.5 text-xs font-medium"
                :class="bindingBadgeClass(row.tradingApiBindingStatus)"
              >
                {{ row.tradingApiBindingStatus }}
              </span>
            </dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">openapiBaseUrl</dt>
            <dd :class="`${rowStyles.dd} font-mono break-all text-slate-400`">
              {{ row.openapiBaseUrl ?? '—' }}
            </dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">bindingId</dt>
            <dd :class="`${rowStyles.dd} font-mono text-slate-400`">{{ row.bindingId ?? '—' }}</dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">tgUsername</dt>
            <dd :class="`${rowStyles.dd} font-mono`">{{ row.tgUsername ?? '—' }}</dd>
          </div>
          <div class="flex flex-col gap-0 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">tgLang</dt>
            <dd :class="rowStyles.dd">{{ row.tgLang ?? '—' }}</dd>
          </div>
        </dl>
        <div class="mt-4 space-y-3 rounded-lg border border-slate-800 bg-slate-950/40 p-4">
          <p class="text-xs font-medium text-slate-400">子账户登记（I04）</p>
          <UiInput
            v-model="bindSubAccountInput"
            label="subAccountId / exchangeSubAccountUserId"
            placeholder="登记后写入 exchangeSubAccountUserId"
            autocomplete="off"
          />
          <div class="flex flex-wrap gap-2">
            <UiButton
              type="button"
              variant="secondary"
              size="sm"
              :loading="bindSubmitting"
              :disabled="loading || unbindSubmitting"
              @click="submitBindSubaccount"
            >
              登记子账户
            </UiButton>
            <UiButton
              type="button"
              variant="danger"
              size="sm"
              :disabled="loading || bindSubmitting || row.tradingApiBindingStatus === 'NONE'"
              @click="openUnbindConfirm"
            >
              解绑 API 托管
            </UiButton>
          </div>
          <p v-if="bindError" class="text-sm text-rose-300" role="alert">{{ bindError }}</p>
        </div>
        <div class="mt-4 flex flex-wrap gap-2">
          <RouterLink
            class="text-sm font-medium text-sky-400 hover:text-sky-300"
            to="/system/channels"
          >
            渠道管理
          </RouterLink>
        </div>
      </section>

      <!-- 运行控制（R01–R06 · POST `/instances/{id}/runtime/{action}`） -->
      <section class="admin-panel overflow-hidden p-4 sm:p-5">
        <h2 class="mb-1 text-[15px] font-semibold text-white">运行控制</h2>
        <p class="mb-4 max-w-3xl text-xs leading-relaxed text-slate-500">
          Start / Resume 受全局门禁 G01 与后端校验约束（横幅关闭或运维挂起时按钮禁用）；失败原因见服务端返回（含 <code class="rounded bg-slate-800 px-1">agentState</code> /
          <code class="rounded bg-slate-800 px-1">reasonCodes</code>）。
        </p>
        <div class="flex flex-wrap gap-2">
          <UiButton
            type="button"
            variant="secondary"
            size="sm"
            :loading="runtimeLoading('start')"
            :disabled="runtimeDisabled('start')"
            title="将弹出确认对话框；G01 门禁关闭时不可用"
            @click="runRuntime('start')"
          >
            Start
          </UiButton>
          <UiButton
            type="button"
            variant="secondary"
            size="sm"
            :loading="runtimeLoading('resume')"
            :disabled="runtimeDisabled('resume')"
            title="将弹出确认对话框；G01 门禁关闭时不可用"
            @click="runRuntime('resume')"
          >
            Resume
          </UiButton>
          <UiButton
            type="button"
            variant="secondary"
            size="sm"
            :loading="runtimeLoading('pause')"
            :disabled="runtimeDisabled('pause')"
            title="将弹出确认对话框"
            @click="runRuntime('pause')"
          >
            Pause
          </UiButton>
          <UiButton
            type="button"
            variant="danger"
            size="sm"
            :loading="runtimeLoading('stop')"
            :disabled="runtimeDisabled('stop')"
            title="将弹出确认对话框"
            @click="runRuntime('stop')"
          >
            Stop
          </UiButton>
        </div>
      </section>

      <!-- 实例参数（I05 · instanceOverrides） -->
      <section class="admin-panel overflow-hidden p-4 sm:p-5">
        <h2 class="mb-1 text-[15px] font-semibold text-white">实例参数</h2>
        <p class="mb-4 text-xs text-slate-500">
          instanceOverrides 白名单键（PATCH 合并）；拒绝 Secret 等未登记键。
        </p>
        <div class="grid gap-4 sm:grid-cols-2">
          <UiInput
            v-model="overridesPreferredLanguage"
            label="preferredLanguage"
            placeholder="如 zh-Hans"
            autocomplete="off"
          />
          <UiInput
            v-model="overridesCooldownSec"
            label="cooldownPreferenceSec"
            placeholder="0～86400"
            inputmode="numeric"
            autocomplete="off"
          />
          <UiInput
            v-model="overridesSymbolPreference"
            label="symbolPreference"
            placeholder="如 BTCUSDT"
            autocomplete="off"
          />
          <UiSelect
            v-model="overridesVoiceEnabled"
            label="voiceOutputEnabled"
            :options="voiceEnabledOptions"
          />
        </div>
        <div class="mt-4 flex flex-wrap items-center gap-2">
          <UiButton
            type="button"
            variant="secondary"
            size="sm"
            :loading="overridesSaving"
            :disabled="loading"
            @click="saveInstanceOverrides"
          >
            保存实例参数
          </UiButton>
        </div>
        <p v-if="overridesError" class="mt-2 text-sm text-rose-300" role="alert">{{ overridesError }}</p>
      </section>

      <!-- 附录 A §8.2 运营摘要 -->
      <section v-if="appendix82Json" class="admin-panel overflow-hidden p-4 sm:p-5">
        <h2 class="mb-1 text-[15px] font-semibold text-white">运营附录摘要</h2>
        <p class="mb-3 text-xs text-slate-500">appendix82（后端按需填充 · SC-AM-14）</p>
        <pre
          class="max-h-72 overflow-auto rounded-lg border border-slate-800 bg-slate-950/80 p-3 font-mono text-[11px] leading-relaxed text-sky-200/90"
          >{{ appendix82Json }}</pre
        >
      </section>

      <AgentInstanceLogsTabs :instance-id="row.instanceId" :telegram-user-id="row.telegramUserId ?? ''" />

      <!-- 原始字段（运维核对 instanceId 等） -->
      <section class="rounded-lg border border-slate-800/80 bg-slate-950/20 px-4 py-3 sm:px-5">
        <h3 class="text-xs font-medium uppercase tracking-wide text-slate-500">技术字段</h3>
        <dl class="mt-2 divide-y divide-slate-800/90">
          <div class="flex flex-col gap-0 py-2 sm:flex-row sm:gap-4">
            <dt :class="rowStyles.dt">instanceId</dt>
            <dd :class="`${rowStyles.dd} font-mono text-xs text-slate-400`">{{ row.instanceId }}</dd>
          </div>
        </dl>
      </section>
    </template>

    <UiModal
      v-model:open="unbindOpen"
      title="确认解绑 API 托管"
      :show-default-close="false"
      description="DELETE binding · 204。保留 agent_instance；tradingApiBindingStatus 将变为 NONE。"
    >
      <div class="space-y-3 text-sm text-slate-300">
        <p>
          实例
          <span class="font-mono text-white">{{ instanceId }}</span>
        </p>
        <p v-if="unbindError" class="text-rose-300">{{ unbindError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="unbindSubmitting" @click="cancelUnbind">
          取消
        </UiButton>
        <UiButton variant="danger" type="button" :loading="unbindSubmitting" @click="confirmedUnbind">
          确认解绑
        </UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="instanceDeleteOpen"
      title="确认删除 Agent 实例"
      :show-default-close="false"
      description="硬删除 agent_instance（DELETE · 204）。不删除 Telegram 交易 API 绑定行。"
    >
      <div class="space-y-3 text-sm text-slate-300">
        <p>
          即将删除
          <span class="font-mono text-white">{{ instanceId }}</span>
        </p>
        <p v-if="instanceDeleteError" class="text-rose-300">{{ instanceDeleteError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="instanceDeleteSubmitting" @click="cancelInstanceDelete">
          取消
        </UiButton>
        <UiButton
          variant="danger"
          type="button"
          :loading="instanceDeleteSubmitting"
          @click="confirmedInstanceDelete"
        >
          确认删除
        </UiButton>
      </template>
    </UiModal>

    <UiModal
      v-model:open="runtimeConfirmOpen"
      :title="runtimeConfirmMeta.title"
      :description="runtimeConfirmMeta.description"
      :show-default-close="false"
    >
      <div class="space-y-3 text-sm text-slate-300">
        <p>
          目标实例
          <span class="font-mono text-white">{{ instanceId }}</span>
        </p>
        <p v-if="runtimeConfirmError" class="text-rose-300">{{ runtimeConfirmError }}</p>
      </div>
      <template #footer>
        <UiButton variant="ghost" type="button" :disabled="runtimeBusy" @click="cancelRuntimeConfirm">
          取消
        </UiButton>
        <UiButton
          :variant="pendingRuntimeAction === 'stop' ? 'danger' : 'secondary'"
          type="button"
          :loading="runtimeBusy"
          @click="submitRuntimeConfirm"
        >
          {{ runtimeConfirmMeta.primaryLabel }}
        </UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>
