<!--
作者: 杨永的Agent
日期: 2026-05-27
修改功能: 协查 · POST intent/recognize 调试（plan.clarify / policyCodes / nextStep · FE_HANDOFF S11）
-->
<script setup lang="ts">
import { ref } from 'vue'

import { AppError } from '@/shared/api/errors'
import {
  postAgentIntentRecognize,
  type AgentIntentRecognizeResponse,
} from '@/shared/api/agent-runtime'
import {
  isNotionalResolveStep,
  zhIntentPlanNextStep,
  zhPolicyCode,
} from '@/shared/lib/intent-plan-display'
import { UiButton, UiInput } from '@/shared/ui'

const messageText = ref('')
const userId = ref('')
const sessionId = ref('')
const previousScenarioId = ref('')
const locale = ref('')

const loading = ref(false)
const errorText = ref<string | null>(null)
const result = ref<AgentIntentRecognizeResponse | null>(null)

async function runRecognize() {
  const text = messageText.value.trim()
  if (!text) {
    errorText.value = '请输入用户话术'
    return
  }
  loading.value = true
  errorText.value = null
  result.value = null
  try {
    result.value = await postAgentIntentRecognize({
      text,
      userId: userId.value.trim() || undefined,
      sessionId: sessionId.value.trim() || undefined,
      previousScenarioId: previousScenarioId.value.trim() || undefined,
      locale: locale.value.trim() || undefined,
      channel: 'admin_probe',
    })
  } catch (e) {
    errorText.value = e instanceof AppError ? e.message : '意图识别失败'
  } finally {
    loading.value = false
  }
}

function nextStepBadgeClass(step: string | null | undefined): string {
  const s = (step ?? '').trim()
  if (s === 'CLARIFY') return 'border-amber-500/40 bg-amber-500/12 text-amber-100/95'
  if (isNotionalResolveStep(s)) return 'border-sky-500/40 bg-sky-500/12 text-sky-100/95'
  if (s === 'CONFIRM_TYPE_A') return 'border-emerald-500/40 bg-emerald-500/12 text-emerald-100/95'
  return 'border-slate-600 bg-slate-800/60 text-slate-200'
}
</script>

<template>
  <section class="admin-panel overflow-hidden p-0">
    <div class="border-b border-slate-800/90 px-4 py-2.5 sm:px-5">
      <h2 class="text-sm font-medium text-slate-200">意图调试</h2>
      <p class="mt-1 text-xs text-slate-500">
        <code class="rounded bg-slate-800 px-1 font-mono text-[11px]">POST /api/v1/agent/intent/recognize</code>
        · 展示裁决层 <code class="font-mono text-[11px]">plan</code>（澄清行、policyCodes、名义解析步）。
      </p>
    </div>
    <div class="space-y-4 p-4 sm:p-5">
      <div class="grid gap-3 md:grid-cols-2">
        <UiInput
          v-model="messageText"
          class="md:col-span-2"
          label="用户话术"
          placeholder="如：全部买入 BCH、全仓杠杆 全部买入 ETH"
        />
        <UiInput v-model="userId" label="userId（可选）" placeholder="Telegram / 运营探测用" />
        <UiInput v-model="sessionId" label="sessionId（可选）" placeholder="tg:{chatId} 等多轮键" />
        <UiInput
          v-model="previousScenarioId"
          label="previousScenarioId（可选）"
          placeholder="上一轮已解析场景"
        />
        <UiInput v-model="locale" label="locale（可选）" placeholder="zh-Hans / en" />
      </div>
      <UiButton type="button" size="sm" :loading="loading" @click="runRecognize">识别</UiButton>
      <p v-if="errorText" class="text-sm text-rose-400" role="alert">{{ errorText }}</p>

      <div v-if="result" class="space-y-4 rounded-lg border border-slate-800 bg-slate-950/50 p-4 text-sm">
        <div class="flex flex-wrap items-center gap-2">
          <span class="text-xs text-slate-500">plan.nextStep</span>
          <span
            v-if="result.plan?.nextStep"
            class="inline-flex rounded border px-2 py-0.5 font-mono text-[11px] font-medium"
            :class="nextStepBadgeClass(result.plan.nextStep)"
          >
            {{ result.plan.nextStep }}
          </span>
          <span v-else class="text-slate-500">—</span>
          <span class="text-xs text-slate-400">{{ zhIntentPlanNextStep(result.plan?.nextStep) }}</span>
        </div>

        <dl class="grid gap-2 text-xs sm:grid-cols-2">
          <div>
            <dt class="text-slate-500">resolvedScenarioId</dt>
            <dd class="font-mono text-slate-200">{{ result.plan?.resolvedScenarioId ?? result.scenarioId ?? '—' }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">effectiveLocale</dt>
            <dd class="font-mono text-slate-200">{{ result.effectiveLocale ?? '—' }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">orchestrationVersion</dt>
            <dd class="font-mono text-slate-400">{{ result.orchestrationVersion ?? '—' }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">nlu.source</dt>
            <dd class="font-mono text-slate-400">{{ result.nlu?.source ?? result.nluSource ?? '—' }}</dd>
          </div>
        </dl>

        <div v-if="result.plan?.policyCodes?.length">
          <p class="mb-1.5 text-xs font-medium text-slate-400">policyCodes</p>
          <ul class="space-y-1">
            <li
              v-for="code in result.plan.policyCodes"
              :key="code"
              class="rounded border border-slate-800/90 bg-slate-900/40 px-2 py-1 font-mono text-[11px] text-slate-300"
            >
              {{ zhPolicyCode(code) }}
            </li>
          </ul>
        </div>
        <p v-else class="text-xs text-slate-600">policyCodes：无</p>

        <div v-if="result.plan?.clarify?.length">
          <p class="mb-1.5 text-xs font-medium text-slate-400">plan.clarify</p>
          <ol class="list-decimal space-y-1.5 pl-5 text-xs leading-relaxed text-slate-300">
            <li v-for="(line, idx) in result.plan.clarify" :key="idx">{{ line }}</li>
          </ol>
        </div>
        <p v-else class="text-xs text-slate-600">plan.clarify：无</p>

        <p v-if="result.plan?.note" class="text-xs text-slate-500">
          note：<span class="text-slate-400">{{ result.plan.note }}</span>
        </p>

        <details class="text-xs text-slate-500">
          <summary class="cursor-pointer text-slate-400 hover:text-slate-300">原始 JSON</summary>
          <pre class="mt-2 max-h-48 overflow-auto rounded border border-slate-800 bg-slate-950 p-2 font-mono text-[10px] text-slate-400">{{ JSON.stringify(result, null, 2) }}</pre>
        </details>
      </div>
    </div>
  </section>
</template>
