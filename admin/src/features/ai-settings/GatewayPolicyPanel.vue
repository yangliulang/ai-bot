<!--
作者: 杨永的Agent
日期: 2026-05-28
修改功能: 网关策略面板自适应多列（NLU/澄清 · narrate 分组网格）
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 网关策略增加 intentClarifyUseLlm（S11 澄清 LLM 润色）
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 使用策略 Tab — 网关策略（intentNluUseLlm + telegramLlmNarrate 9 场景）
-->
<script setup lang="ts">
import { ref } from 'vue'

import { AppError } from '@/shared/api/errors'
import {
  patchAiGatewayDefaults,
  type AiGatewayDefaults,
} from '@/shared/api/admin-ai-settings'
import {
  INTENT_CLARIFY_ENV_VAR,
  INTENT_NLU_ENV_VAR,
  NARRATE_READONLY_FIELDS,
  NARRATE_TYPE_A_FIELDS,
  type TelegramLlmNarrateKey,
} from '@/features/ai-settings/gateway-policy-constants'
import { adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import UiSwitch from '@/shared/ui/UiSwitch.vue'

const props = defineProps<{
  loading?: boolean
  intentNluUseLlm: boolean
  intentClarifyUseLlm: boolean
  telegramLlmNarrate: Record<TelegramLlmNarrateKey, boolean>
}>()

const emit = defineEmits<{
  applied: [defaults: AiGatewayDefaults]
}>()

const savingIntentNlu = ref(false)
const savingIntentClarify = ref(false)
const savingNarrateKey = ref<TelegramLlmNarrateKey | null>(null)

function panelDisabled(): boolean {
  return (
    Boolean(props.loading) ||
    savingIntentNlu.value ||
    savingIntentClarify.value ||
    savingNarrateKey.value !== null
  )
}

async function saveIntentNlu(next: boolean) {
  savingIntentNlu.value = true
  try {
    const updated = await patchAiGatewayDefaults({ intentNluUseLlm: next })
    emit('applied', updated)
    adminToastSuccess('意图 NLU 策略已保存')
  } catch (e) {
    adminToastError(e instanceof AppError ? e.message : '保存失败')
  } finally {
    savingIntentNlu.value = false
  }
}

async function onIntentNluChange(checked: boolean) {
  await saveIntentNlu(checked)
}

async function saveIntentClarify(next: boolean) {
  savingIntentClarify.value = true
  try {
    const updated = await patchAiGatewayDefaults({ intentClarifyUseLlm: next })
    emit('applied', updated)
    adminToastSuccess('澄清 LLM 润色策略已保存')
  } catch (e) {
    adminToastError(e instanceof AppError ? e.message : '保存失败')
  } finally {
    savingIntentClarify.value = false
  }
}

async function onIntentClarifyChange(checked: boolean) {
  await saveIntentClarify(checked)
}

async function saveNarrateKey(key: TelegramLlmNarrateKey, next: boolean) {
  savingNarrateKey.value = key
  try {
    const updated = await patchAiGatewayDefaults({
      telegramLlmNarrate: { [key]: next },
    })
    emit('applied', updated)
    adminToastSuccess('Telegram 叙述策略已保存')
  } catch (e) {
    adminToastError(e instanceof AppError ? e.message : '保存失败')
  } finally {
    savingNarrateKey.value = null
  }
}

async function onNarrateChange(key: TelegramLlmNarrateKey, checked: boolean) {
  await saveNarrateKey(key, checked)
}

function rowDisabled(key: TelegramLlmNarrateKey): boolean {
  return panelDisabled() || savingNarrateKey.value === key
}
</script>

<template>
  <section class="admin-panel space-y-5 p-4 sm:p-5" aria-labelledby="gateway-policy-heading">
    <div class="space-y-1">
      <h2 id="gateway-policy-heading" class="text-sm font-medium text-white">网关策略</h2>
      <p class="text-xs leading-relaxed text-slate-500">
        控制意图 NLU 与 Telegram 场景是否优先走 LLM 叙述。保存后立即写入网关 defaults；部署环境变量为
        <span class="text-slate-400">true</span> 时优先生效于控制台关闭项。
      </p>
    </div>

    <div
      class="rounded-lg border border-slate-800 bg-slate-900/50 px-3 py-2.5 text-xs leading-relaxed text-slate-400"
      role="note"
    >
      <p class="font-medium text-slate-300">环境变量强制开启（优先于 Admin）</p>
      <ul class="mt-1.5 list-disc space-y-1 pl-4">
        <li>
          意图 NLU：<code class="rounded bg-slate-950 px-1 font-mono text-[11px] text-emerald-400/90">{{ INTENT_NLU_ENV_VAR }}=true</code>
          → 对应 Admin <code class="font-mono text-slate-500">intentNluUseLlm</code>
        </li>
        <li>
          澄清润色：<code class="rounded bg-slate-950 px-1 font-mono text-[11px] text-emerald-400/90">{{ INTENT_CLARIFY_ENV_VAR }}=true</code>
          → <code class="font-mono text-slate-500">intentClarifyUseLlm</code>（时间线
          <code class="font-mono text-[11px]">llm.agent.runtime.runtime_clarify</code>）
        </li>
        <li>
          Telegram narrate（示例）：
          <code class="rounded bg-slate-950 px-1 font-mono text-[11px] text-emerald-400/90">CHAINUP_AGENT_TELEGRAM_LLM_NARRATE_READ_MARKET_TICKER=true</code>
          → <code class="font-mono text-slate-500">telegramLlmNarrate.readMarketTicker</code>；其它场景变量名见各行字段名。
        </li>
      </ul>
    </div>

    <div class="grid grid-cols-1 gap-4 border-t border-slate-800/80 pt-4 md:grid-cols-2">
      <div class="space-y-3">
        <h3 class="text-xs font-medium uppercase tracking-wide text-slate-400">意图 NLU</h3>
        <label
          class="flex h-full cursor-pointer items-start justify-between gap-4 rounded-lg border border-slate-800/80 bg-slate-950/40 px-3 py-2.5"
          :class="panelDisabled() ? 'cursor-not-allowed opacity-70' : 'hover:border-slate-700'"
        >
          <span class="min-w-0 space-y-0.5">
            <span class="block text-sm text-slate-200">意图 NLU 优先 LLM</span>
            <span class="block font-mono text-[11px] text-slate-500">intentNluUseLlm</span>
          </span>
          <UiSwitch
            :model-value="intentNluUseLlm"
            size="sm"
            aria-label="意图 NLU 优先 LLM"
            :disabled="panelDisabled()"
            @update:model-value="onIntentNluChange"
          />
        </label>
        <p v-if="savingIntentNlu" class="text-xs text-slate-500" role="status">保存中…</p>
      </div>

      <div class="space-y-3">
        <h3 class="text-xs font-medium uppercase tracking-wide text-slate-400">交易澄清（S11）</h3>
        <label
          class="flex h-full cursor-pointer items-start justify-between gap-4 rounded-lg border border-slate-800/80 bg-slate-950/40 px-3 py-2.5"
          :class="panelDisabled() ? 'cursor-not-allowed opacity-70' : 'hover:border-slate-700'"
        >
          <span class="min-w-0 space-y-0.5">
            <span class="block text-sm text-slate-200">澄清话术 LLM 润色</span>
            <span class="block font-mono text-[11px] text-slate-500">intentClarifyUseLlm</span>
            <span class="block text-[11px] leading-relaxed text-slate-600">
              开启且规则已产出 plan.clarify 时，可走 agent.runtime.runtime_clarify；失败回退规则文案。
            </span>
          </span>
          <UiSwitch
            :model-value="intentClarifyUseLlm"
            size="sm"
            aria-label="澄清话术 LLM 润色"
            :disabled="panelDisabled()"
            @update:model-value="onIntentClarifyChange"
          />
        </label>
        <p v-if="savingIntentClarify" class="text-xs text-slate-500" role="status">保存中…</p>
      </div>
    </div>

    <div class="space-y-4 border-t border-slate-800/80 pt-4">
      <h3 class="text-xs font-medium uppercase tracking-wide text-slate-400">Telegram LLM 叙述</h3>

      <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div class="space-y-2">
          <h4 class="text-xs font-medium text-slate-300">只读行情（5）</h4>
          <ul class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <li
              v-for="field in NARRATE_READONLY_FIELDS"
              :key="field.key"
              class="flex items-start justify-between gap-3 rounded-lg border border-slate-800/80 bg-slate-950/35 px-3 py-2.5"
            >
              <span class="min-w-0">
                <span class="block text-sm text-slate-200">{{ field.label }}</span>
                <span class="block font-mono text-[11px] text-slate-500">{{ field.key }}</span>
              </span>
              <UiSwitch
                :model-value="telegramLlmNarrate[field.key]"
                size="sm"
                :aria-label="field.label"
                :disabled="rowDisabled(field.key)"
                @update:model-value="onNarrateChange(field.key, $event)"
              />
            </li>
          </ul>
        </div>

        <div class="space-y-2">
          <h4 class="text-xs font-medium text-slate-300">交易确认 Type-A（4）</h4>
          <ul class="grid grid-cols-1 gap-2 sm:grid-cols-2">
            <li
              v-for="field in NARRATE_TYPE_A_FIELDS"
              :key="field.key"
              class="flex items-start justify-between gap-3 rounded-lg border border-slate-800/80 bg-slate-950/35 px-3 py-2.5"
            >
              <span class="min-w-0">
                <span class="block text-sm text-slate-200">{{ field.label }}</span>
                <span class="block font-mono text-[11px] text-slate-500">{{ field.key }}</span>
              </span>
              <UiSwitch
                :model-value="telegramLlmNarrate[field.key]"
                size="sm"
                :aria-label="field.label"
                :disabled="rowDisabled(field.key)"
                @update:model-value="onNarrateChange(field.key, $event)"
              />
            </li>
          </ul>
        </div>
      </div>

      <p v-if="savingNarrateKey" class="text-xs text-slate-500" role="status">
        保存 {{ savingNarrateKey }}…
      </p>
    </div>
  </section>
</template>
