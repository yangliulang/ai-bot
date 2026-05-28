<!--
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 应用/重载/恢复默认反馈改用全局 **`adminToast`**
作者: 杨永的Agent
日期: 2026-05-22
修改功能: 各策略面板字段改为响应式 2/4 列网格（checkbox 2–3 列 · 数值 4 列 · 开发信息 2 列）
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 初始加载 **GET /admin/orchestration/policy**；运营字段应用仍 sessionStorage（FE_HANDOFF Phase2）
作者: 杨永的Agent
日期: 2026-05-15
修改功能: 运行编排「执行策略」Tab — sessionStorage 演示持久化，对齐 product-doc RuntimeOrchestration · ExecutionPolicyTab（FE_HANDOFF）
-->
<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'

import {
  DEFAULT_EXECUTION_POLICY,
  executionPolicyFromApi,
  FAILURE_STOP_OPTIONS,
  FALLBACK_ENGINEERING_SPEC_REFS,
  type ExecutionPolicyState,
} from '@/entities/orchestration/execution-policy-model'
import { getOrchestrationPolicy } from '@/shared/api/admin-orchestration'
import { AppError } from '@/shared/api/errors'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import {
  ADMIN_TOOLBAR_CLUSTER_CLASS,
  ADMIN_TOOLBAR_META_CLASS,
} from '@/shared/ui/toolbar-controls'
import UiButton from '@/shared/ui/UiButton.vue'
import UiInput from '@/shared/ui/UiInput.vue'
import UiSelect from '@/shared/ui/UiSelect.vue'
import UiSwitch from '@/shared/ui/UiSwitch.vue'

/** 面板内表单域：窄屏 1 列，中屏 2 列，宽屏 4 列 */
const PANEL_FIELD_GRID_4 =
  'grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2 lg:grid-cols-4 lg:gap-x-5'
/** 开关类：中屏起 2 列，宽屏 3 列（每 panel 约 3 项） */
const PANEL_TOGGLE_GRID = 'grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3'
/** 开发信息折叠区：中屏 2 列 */
const PANEL_FIELD_GRID_2 = 'grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2 lg:gap-x-5'

const STORAGE_KEY = 'chainup-admin-orchestration-policy-v1'

const policy = reactive<ExecutionPolicyState>({ ...DEFAULT_EXECUTION_POLICY })
const engineeringSpecRefs = ref<string[]>([...FALLBACK_ENGINEERING_SPEC_REFS])
const dirty = ref(false)
const apiLoading = ref(false)
const apiError = ref<string | null>(null)
const registryVersion = ref<string | null>(null)

function loadFromStorage() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const parsed = JSON.parse(raw) as Partial<ExecutionPolicyState>
    Object.assign(policy, DEFAULT_EXECUTION_POLICY, parsed)
  } catch {
    /* ignore corrupt session */
  }
}

function persist() {
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(policy))
}

function markDirty() {
  dirty.value = true
}

function onApply() {
  persist()
  dirty.value = false
  adminToastSuccess('已应用（运营字段保存在本会话 sessionStorage；工程预算以服务端为准）')
}

function onResetDefault() {
  void loadPolicyFromApi(true)
}

async function loadPolicyFromApi(resetSession = false, toastOnSuccess = resetSession) {
  apiLoading.value = true
  apiError.value = null
  try {
    const api = await getOrchestrationPolicy()
    registryVersion.value = api.orchestrationRegistryVersion
    Object.assign(policy, executionPolicyFromApi(api))
    engineeringSpecRefs.value =
      api.engineeringSpecRefs?.length > 0 ? api.engineeringSpecRefs : [...FALLBACK_ENGINEERING_SPEC_REFS]
    if (resetSession) {
      sessionStorage.removeItem(STORAGE_KEY)
      dirty.value = false
      if (toastOnSuccess) adminToastSuccess('已从服务端恢复默认')
    } else {
      loadFromStorage()
      if (toastOnSuccess) adminToastSuccess('已重新加载')
    }
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '加载执行策略失败'
    apiError.value = msg
    adminToastError(msg)
    Object.assign(policy, DEFAULT_EXECUTION_POLICY)
    engineeringSpecRefs.value = [...FALLBACK_ENGINEERING_SPEC_REFS]
  } finally {
    apiLoading.value = false
  }
}

onMounted(() => {
  void loadPolicyFromApi(false)
})

function numField(key: keyof ExecutionPolicyState, fallback: number): string {
  const v = policy[key]
  return typeof v === 'number' && !Number.isNaN(v) ? String(v) : String(fallback)
}

function setNumField(key: keyof ExecutionPolicyState, s: string, min: number, max?: number) {
  const n = Number(s)
  if (Number.isNaN(n)) return
  let x = n
  if (x < min) x = min
  if (max !== undefined && x > max) x = max
  ;(policy as Record<string, unknown>)[key as string] = x
  markDirty()
}
</script>

<template>
  <div class="space-y-4">
    <div
      class="rounded-lg border border-sky-500/25 bg-sky-500/10 px-4 py-3 text-sm leading-relaxed text-sky-100/95"
      role="note"
    >
      面向运营：配置是否允许自动跑完编排、人工确认的开关、名义金额与杠杆上限、以及失败与超时策略。初始值来自
      <strong class="font-medium text-white">GET /admin/orchestration/policy</strong>
      （寄存器
      <span v-if="registryVersion" class="font-mono text-sky-200/90">{{ registryVersion }}</span>
      ）；「应用」仅将运营侧改动写入浏览器 sessionStorage。工程预算（工具步/编排步）以 AI 网关 defaults 为准，修改请至
      <RouterLink to="/ai-settings" class="font-medium text-sky-300 underline-offset-2 hover:text-sky-200">
        模型配置
      </RouterLink>
      。
    </div>

    <p v-if="apiError" class="text-sm text-amber-300" role="alert">{{ apiError }}</p>

    <section class="admin-panel space-y-4 p-4 sm:p-5">
      <div class="flex flex-wrap items-center justify-between gap-2">
        <h3 class="text-[13px] font-semibold text-white">自动执行策略</h3>
        <UiButton
          type="button"
          variant="secondary"
          size="sm"
          :loading="apiLoading"
          @click="loadPolicyFromApi(false, true)"
        >
          重新加载
        </UiButton>
      </div>
      <div :class="PANEL_TOGGLE_GRID">
        <label
          class="flex cursor-pointer items-center justify-between gap-3 text-sm leading-snug text-slate-300"
        >
          <span>允许自动执行</span>
          <UiSwitch
            v-model="policy.autoExecutionAllowed"
            size="sm"
            aria-label="允许自动执行"
            :disabled="apiLoading"
            @update:model-value="markDirty"
          />
        </label>
        <label
          class="flex cursor-pointer items-center justify-between gap-3 text-sm leading-snug text-slate-300"
        >
          <span>高风控交易场景禁止自动落单</span>
          <UiSwitch
            v-model="policy.blockAutoHighRiskWrite"
            size="sm"
            aria-label="高风控交易场景禁止自动落单"
            :disabled="apiLoading"
            @update:model-value="markDirty"
          />
        </label>
        <label
          class="flex cursor-pointer items-center justify-between gap-3 text-sm leading-snug text-slate-300 sm:col-span-2 lg:col-span-1"
        >
          <span>查询与行情类默认可自动执行</span>
          <UiSwitch
            v-model="policy.queryAutoDefault"
            size="sm"
            aria-label="查询与行情类默认可自动执行"
            :disabled="apiLoading"
            @update:model-value="markDirty"
          />
        </label>
      </div>
    </section>

    <section class="admin-panel space-y-4 p-4 sm:p-5">
      <h3 class="text-[13px] font-semibold text-white">确认与加码</h3>
      <div :class="PANEL_TOGGLE_GRID">
        <label
          class="flex cursor-pointer items-center justify-between gap-3 text-sm leading-snug text-slate-300"
        >
          <span>交易/资金写操作须用户确认</span>
          <UiSwitch
            v-model="policy.confirmationRequiredForWrites"
            size="sm"
            aria-label="交易/资金写操作须用户确认"
            :disabled="apiLoading"
            @update:model-value="markDirty"
          />
        </label>
        <label
          class="flex cursor-pointer items-center justify-between gap-3 text-sm leading-snug text-slate-300"
        >
          <span>大额名义须二次确认</span>
          <UiSwitch
            v-model="policy.secondConfirmLargeNotional"
            size="sm"
            aria-label="大额名义须二次确认"
            :disabled="apiLoading"
            @update:model-value="markDirty"
          />
        </label>
        <label
          class="flex cursor-pointer items-center justify-between gap-3 text-sm leading-snug text-slate-300 sm:col-span-2 lg:col-span-1"
        >
          <span>高杠杆变更须额外确认</span>
          <UiSwitch
            v-model="policy.highLeverageConfirm"
            size="sm"
            aria-label="高杠杆变更须额外确认"
            :disabled="apiLoading"
            @update:model-value="markDirty"
          />
        </label>
      </div>
    </section>

    <section class="admin-panel space-y-4 p-4 sm:p-5">
      <h3 class="text-[13px] font-semibold text-white">风险限制</h3>
      <div :class="PANEL_FIELD_GRID_4">
        <UiInput
          :model-value="numField('maxNotionalUsdt', 50000)"
          label="单笔最大金额（USDT）"
          type="number"
          :disabled="apiLoading"
          @update:model-value="(v) => setNumField('maxNotionalUsdt', v, 1)"
        />
        <UiInput
          :model-value="numField('maxLeverage', 20)"
          label="最大杠杆（倍）"
          type="number"
          :disabled="apiLoading"
          @update:model-value="(v) => setNumField('maxLeverage', v, 1, 125)"
        />
        <UiInput
          :model-value="numField('maxDailyWriteOperations', 200)"
          label="单日写类操作上限"
          type="number"
          :disabled="apiLoading"
          @update:model-value="(v) => setNumField('maxDailyWriteOperations', v, 1)"
        />
        <UiInput
          v-model="policy.rateLimitNote"
          class="sm:col-span-2 lg:col-span-4"
          label="高频 / 频控说明"
          :disabled="apiLoading"
          @update:model-value="markDirty"
        />
      </div>
    </section>

    <section class="admin-panel space-y-4 p-4 sm:p-5">
      <h3 class="text-[13px] font-semibold text-white">执行稳定性</h3>
      <div :class="PANEL_FIELD_GRID_4">
        <UiInput
          :model-value="numField('maxRetries', 3)"
          label="最大自动重试次数"
          type="number"
          :disabled="apiLoading"
          @update:model-value="(v) => setNumField('maxRetries', v, 0, 20)"
        />
        <UiInput
          :model-value="numField('executionTimeoutSeconds', 120)"
          label="单次执行超时（秒）"
          type="number"
          :disabled="apiLoading"
          @update:model-value="(v) => setNumField('executionTimeoutSeconds', v, 5, 600)"
        />
        <UiSelect
          v-model="policy.failureStopPolicy"
          class="sm:col-span-2 lg:col-span-2"
          label="失败终止策略"
          :options="FAILURE_STOP_OPTIONS"
          :disabled="apiLoading"
          @update:model-value="markDirty"
        />
      </div>
    </section>

    <details class="admin-panel overflow-hidden p-4 sm:p-5">
      <summary class="cursor-pointer text-sm font-medium text-slate-200">
        开发信息（Runtime / 契约镜像）
      </summary>
      <p class="mt-3 text-xs leading-relaxed text-slate-500">
        以下与 FR-AO06、runtime-contract、retry-policy 对签；勿对用户暴露字段名作为主叙事。
      </p>
      <div class="mt-4" :class="PANEL_FIELD_GRID_2">
        <UiInput
          :model-value="numField('maxToolCalls', 32)"
          label="工具调用步数上限（引擎）"
          type="number"
          :disabled="apiLoading"
          @update:model-value="(v) => setNumField('maxToolCalls', v, 1, 999)"
        />
        <UiInput
          :model-value="numField('maxOrchestrationSteps', 48)"
          label="编排步骤上限（引擎）"
          type="number"
          :disabled="apiLoading"
          @update:model-value="(v) => setNumField('maxOrchestrationSteps', v, 1, 999)"
        />
        <label
          class="flex cursor-pointer items-center justify-between gap-3 text-sm leading-snug text-slate-300 sm:col-span-2"
        >
          <span>启用模型回合上限</span>
          <UiSwitch
            v-model="policy.modelRoundsLimitEnabled"
            size="sm"
            aria-label="启用模型回合上限"
            :disabled="apiLoading"
            @update:model-value="markDirty"
          />
        </label>
        <UiInput
          :model-value="numField('maxModelRounds', 16)"
          label="模型回合上限"
          type="number"
          :disabled="apiLoading || !policy.modelRoundsLimitEnabled"
          @update:model-value="(v) => setNumField('maxModelRounds', v, 1, 99)"
        />
        <UiInput
          v-model="policy.budgetExceededStableCode"
          label="预算超出稳定码（引擎）"
          :disabled="apiLoading"
          @update:model-value="markDirty"
        />
        <UiInput
          v-model="policy.cClassPoolNote"
          label="C 类外网池（引擎文案）"
          :disabled="apiLoading"
          @update:model-value="markDirty"
        />
        <UiInput
          v-model="policy.retrySummary"
          label="重试策略摘要（spec）"
          :disabled="apiLoading"
          @update:model-value="markDirty"
        />
        <UiInput
          v-model="policy.unknownHandlingSummary"
          label="UNKNOWN / 超时摘要（spec）"
          :disabled="apiLoading"
          @update:model-value="markDirty"
        />
        <div class="sm:col-span-2">
          <p class="text-xs font-medium text-slate-500">规格互引</p>
          <ul class="mt-2 list-inside list-disc space-y-1 text-xs text-slate-400">
            <li v-for="p in engineeringSpecRefs" :key="p">
              <code class="rounded bg-slate-900 px-1 py-0.5 font-mono text-[11px] text-slate-300">{{ p }}</code>
            </li>
          </ul>
        </div>
      </div>
    </details>

    <div :class="ADMIN_TOOLBAR_CLUSTER_CLASS">
      <UiButton type="button" variant="primary" size="sm" :disabled="apiLoading" @click="onApply">应用</UiButton>
      <UiButton type="button" variant="secondary" size="sm" :loading="apiLoading" @click="onResetDefault">
        恢复服务端默认
      </UiButton>
      <span v-if="dirty" :class="[ADMIN_TOOLBAR_META_CLASS, 'text-amber-300']">未应用</span>
    </div>
  </div>
</template>
