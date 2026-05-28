<!--
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 编辑页面板 **lg 双列**、表单 **w-full** 去固定 max-width；触发条件行改 Grid
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 人工确认规则新建/编辑（POST/PUT · 对齐原型 ConfirmationRuleEditorPage）
-->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import {
  defaultOperatorForField,
  emptyTriggerCondition,
  operatorsForField,
  RISK_LEVEL_OPTIONS,
  RULE_ACTION_OPTIONS,
  SCENARIO_OPTIONS,
  TRIGGER_FIELD_OPTIONS,
  TRIGGER_OPERATOR_OPTIONS,
  type ConfirmationRuleWriteBody,
  type RiskLevel,
  type RuleAction,
  type ScenarioKey,
  type TriggerConditionRow,
  type TriggerFieldKey,
  type TriggerOpKey,
} from '@/entities/confirmation-rules/confirmation-rules-catalog'
import {
  createConfirmationRule,
  explainConfirmationRuleError,
  getConfirmationRule,
  updateConfirmationRule,
} from '@/shared/api/admin-confirmation-rules'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminPageHeader from '@/shared/ui/AdminPageHeader.vue'
import UiButton from '@/shared/ui/UiButton.vue'
import UiInput from '@/shared/ui/UiInput.vue'
import UiSelect, { type UiSelectOption } from '@/shared/ui/UiSelect.vue'
import UiSwitch from '@/shared/ui/UiSwitch.vue'

const route = useRoute()
const router = useRouter()

const isCreate = computed(() => route.name === 'ai.confirmation-rules.new')

const ruleId = computed(() => {
  const p = route.params.ruleId
  const raw = Array.isArray(p) ? p[0] : p
  return typeof raw === 'string' ? decodeURIComponent(raw.trim()) : ''
})

const loading = ref(false)
const loadError = ref<string | null>(null)
const saveLoading = ref(false)
const saveError = ref<string | null>(null)

const title = ref('')
const summary = ref('')
const riskLevel = ref<RiskLevel>('medium')
const triggerConditions = ref<TriggerConditionRow[]>([emptyTriggerCondition()])
const scenarios = ref<ScenarioKey[]>([])
const action = ref<RuleAction>('second_confirm')
const defaultEnabled = ref(true)

const riskOptions: UiSelectOption[] = RISK_LEVEL_OPTIONS.map((o) => ({
  value: o.value,
  label: o.label,
}))

const actionOptions: UiSelectOption[] = RULE_ACTION_OPTIONS.map((o) => ({
  value: o.value,
  label: o.label,
}))

function operatorOptions(fieldKey: TriggerFieldKey): UiSelectOption[] {
  return operatorsForField(fieldKey).map((op) => {
    const label = TRIGGER_OPERATOR_OPTIONS.find((x) => x.value === op)?.label ?? op
    return { value: op, label }
  })
}

const fieldOptions: UiSelectOption[] = TRIGGER_FIELD_OPTIONS.map((o) => ({
  value: o.value,
  label: o.label,
}))

function resetCreateForm() {
  title.value = ''
  summary.value = ''
  riskLevel.value = 'medium'
  triggerConditions.value = [emptyTriggerCondition()]
  scenarios.value = []
  action.value = 'second_confirm'
  defaultEnabled.value = true
}

async function loadRule() {
  if (isCreate.value) {
    resetCreateForm()
    return
  }
  const id = ruleId.value
  if (!id) {
    loadError.value = '无效的规则 ID'
    return
  }
  loading.value = true
  loadError.value = null
  try {
    const row = await getConfirmationRule(id)
    if (row.isBuiltin) {
      loadError.value = '内置规则不可编辑，请在列表中查看或切换启用状态。'
      return
    }
    title.value = row.title
    summary.value = row.summary
    riskLevel.value = row.riskLevel
    triggerConditions.value =
      row.triggerConditions.length > 0
        ? row.triggerConditions.map((c) => ({ ...c }))
        : [emptyTriggerCondition()]
    scenarios.value = [...row.scenarios]
    action.value = row.action
    defaultEnabled.value = row.defaultEnabled
  } catch (e) {
    loadError.value = explainConfirmationRuleError(e)
  } finally {
    loading.value = false
  }
}

function onFieldKeyChange(index: number, fk: string) {
  const fieldKey = fk as TriggerFieldKey
  const row = triggerConditions.value[index]
  if (!row) return
  triggerConditions.value[index] = {
    ...row,
    fieldKey,
    operator: defaultOperatorForField(fieldKey),
  }
}

function addCondition() {
  triggerConditions.value = [...triggerConditions.value, emptyTriggerCondition()]
}

function removeCondition(index: number) {
  if (triggerConditions.value.length <= 1) return
  triggerConditions.value = triggerConditions.value.filter((_, i) => i !== index)
}

function toggleScenario(key: ScenarioKey, checked: boolean) {
  if (checked) {
    if (!scenarios.value.includes(key)) scenarios.value = [...scenarios.value, key]
  } else {
    scenarios.value = scenarios.value.filter((k) => k !== key)
  }
}

function buildBody(): ConfirmationRuleWriteBody | null {
  const conditions = triggerConditions.value
    .filter((c) => String(c.value ?? '').trim())
    .map((c) => {
      const fk = c.fieldKey
      let op = c.operator
      if (!operatorsForField(fk).includes(op)) op = defaultOperatorForField(fk)
      return { fieldKey: fk, operator: op, value: String(c.value).trim() }
    })
  if (!title.value.trim()) {
    saveError.value = '请输入规则名称'
    return null
  }
  if (!summary.value.trim()) {
    saveError.value = '请输入规则说明'
    return null
  }
  if (!conditions.length) {
    saveError.value = '请至少添加一条触发条件并填写比较值'
    return null
  }
  if (!scenarios.value.length) {
    saveError.value = '请至少选择一个适用场景'
    return null
  }
  return {
    title: title.value.trim(),
    summary: summary.value.trim(),
    riskLevel: riskLevel.value,
    triggerConditions: conditions,
    scenarios: [...scenarios.value],
    action: action.value,
    defaultEnabled: defaultEnabled.value,
  }
}

async function onSave() {
  saveError.value = null
  const body = buildBody()
  if (!body) return
  saveLoading.value = true
  try {
    if (isCreate.value) {
      await createConfirmationRule(body)
    } else {
      await updateConfirmationRule(ruleId.value, body)
    }
    router.push({ name: 'ai.confirmation-rules' })
  } catch (e) {
    saveError.value = explainConfirmationRuleError(e)
  } finally {
    saveLoading.value = false
  }
}

watch(
  () => route.fullPath,
  () => {
    void loadRule()
  },
)

onMounted(() => {
  void loadRule()
})
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      :title="isCreate ? '新建风控规则' : '编辑风控规则'"
      title-size="editor"
      density="compact"
      description="配置风险条件与命中后的处理方式；字段均为业务语义，不涉及渠道或引擎实现细节。"
      :dev-meta="`${isCreate ? 'POST' : 'PUT'} /api/v1/admin/confirmation-rules`"
      :subline="!isCreate && ruleId ? ruleId : undefined"
      :crumbs="[
        { label: '人工确认规则', to: { name: 'ai.confirmation-rules' } },
        { label: isCreate ? '新建' : '编辑' },
      ]"
    >
      <template #actions>
        <RouterLink :to="{ name: 'ai.confirmation-rules' }" class="shrink-0">
          <UiButton type="button" variant="secondary" size="sm">返回列表</UiButton>
        </RouterLink>
      </template>
    </AdminPageHeader>

    <div
      v-if="loading"
      class="grid gap-6 py-8 lg:grid-cols-2"
      aria-busy="true"
    >
      <div class="h-40 animate-pulse rounded-lg bg-slate-800/50" />
      <div class="h-40 animate-pulse rounded-lg bg-slate-800/50" />
      <div class="h-56 animate-pulse rounded-lg bg-slate-800/40 lg:col-span-2" />
    </div>

    <p v-else-if="loadError" class="text-sm text-amber-300">{{ loadError }}</p>

    <form v-else class="w-full space-y-6" @submit.prevent="onSave">
      <p v-if="saveError" class="text-sm text-rose-300" role="alert">{{ saveError }}</p>

      <div class="grid gap-6 lg:grid-cols-2 lg:items-start">
        <section class="admin-panel space-y-4 p-4 sm:p-5">
          <h2 class="text-[13px] font-semibold text-white">基础信息</h2>
          <UiInput v-model="title" label="规则名称" placeholder="如：高杠杆交易二次确认" />
          <UiInput
            v-model="summary"
            label="规则说明"
            placeholder="如：当杠杆超过 20× 时，用户需再次确认风险。"
          />
        </section>

        <div class="flex flex-col gap-6">
          <section class="admin-panel space-y-4 p-4 sm:p-5">
            <h2 class="text-[13px] font-semibold text-white">风险等级</h2>
            <UiSelect v-model="riskLevel" label="风险等级" :options="riskOptions" />
          </section>

          <section class="admin-panel space-y-4 p-4 sm:p-5">
            <h2 class="text-[13px] font-semibold text-white">处理动作</h2>
            <UiSelect v-model="action" label="命中后的处理动作" :options="actionOptions" />
            <details class="rounded-md border border-slate-800/90 bg-slate-950/40 px-3 py-2 text-xs text-slate-500">
              <summary class="cursor-pointer text-slate-400">各动作说明（展开查看）</summary>
              <ul class="mt-2 space-y-2">
                <li v-for="opt in RULE_ACTION_OPTIONS" :key="opt.value">
                  <span class="font-medium text-slate-300">{{ opt.label }}</span>
                  ：{{ opt.hint }}
                </li>
              </ul>
            </details>
            <label class="flex cursor-pointer items-center justify-between gap-3 text-sm text-slate-300">
              <span>保存后立即启用</span>
              <UiSwitch v-model="defaultEnabled" size="sm" aria-label="保存后立即启用" />
            </label>
          </section>
        </div>

        <section class="admin-panel space-y-4 p-4 sm:p-5 lg:col-span-2">
          <h2 class="text-[13px] font-semibold text-white">触发条件</h2>
          <p class="text-xs leading-relaxed text-slate-500">
            通过「字段 / 运算符 / 值」组合定义命中条件，可添加多行。
          </p>
          <div class="space-y-4">
            <div
              v-for="(row, index) in triggerConditions"
              :key="index"
              class="grid gap-3 border-b border-slate-800/80 pb-4 sm:grid-cols-[minmax(0,1.2fr)_minmax(0,0.65fr)_minmax(0,1fr)_auto] sm:items-end last:border-0 last:pb-0"
            >
              <UiSelect
                :model-value="row.fieldKey"
                label="字段"
                :options="fieldOptions"
                @update:model-value="(v) => onFieldKeyChange(index, v)"
              />
              <UiSelect
                v-model="row.operator"
                label="运算符"
                :options="operatorOptions(row.fieldKey)"
              />
              <UiInput v-model="row.value" label="值" placeholder="如 50000、20" />
              <UiButton
                type="button"
                variant="ghost"
                size="sm"
                class="sm:mb-0.5 sm:justify-self-end"
                :disabled="triggerConditions.length <= 1"
                @click="removeCondition(index)"
              >
                删除
              </UiButton>
            </div>
          </div>
          <UiButton type="button" variant="secondary" size="sm" @click="addCondition">添加条件</UiButton>
        </section>

        <section class="admin-panel space-y-4 p-4 sm:p-5 lg:col-span-2">
          <h2 class="text-[13px] font-semibold text-white">适用场景</h2>
          <p class="text-xs text-slate-500">可多选，覆盖规则生效的业务面</p>
          <div class="grid gap-2 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
            <label
              v-for="opt in SCENARIO_OPTIONS"
              :key="opt.value"
              class="flex cursor-pointer items-center justify-between gap-3 rounded-md border border-slate-800 bg-slate-950/40 px-3 py-2 text-sm text-slate-300 transition-colors hover:border-slate-700"
            >
              <span class="min-w-0">{{ opt.label }}</span>
              <UiSwitch
                :model-value="scenarios.includes(opt.value)"
                size="sm"
                :aria-label="`适用场景 ${opt.label}`"
                @update:model-value="toggleScenario(opt.value, $event)"
              />
            </label>
          </div>
        </section>
      </div>

      <div
        class="flex flex-wrap gap-3 border-t border-slate-800/80 pt-5"
      >
        <UiButton type="submit" :loading="saveLoading">保存</UiButton>
        <RouterLink :to="{ name: 'ai.confirmation-rules' }">
          <UiButton type="button" variant="secondary">取消</UiButton>
        </RouterLink>
      </div>
    </form>
  </AdminPage>
</template>
