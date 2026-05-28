<!--
作者: 杨永的Agent
日期: 2026-05-13
修改功能: 描述列表标签改为「子账户 API Key / 子账户 Secret Key」
作者: 杨永的Agent
日期: 2026-05-13
修改功能: 绑定请求携带 `subAccountId`；成功结果 `agentSubAccountId` 缺省时回退用户填写的子账户 ID
作者: 杨永的Agent
日期: 2026-05-12
修改功能: session 写入 `bindingRowCreated`，供成功页仅在重复绑定（UPDATE）时展示「已绑定」横幅
修改功能: 成功后 session 写入 `saved`/`agentTradingApiBindingStatus`，供成功页识别 BOUND
日期: 2026-05-12
修改功能: 「确认绑定」经 httpClient 调 `/api/v1/me/agent/bindings/trading-api`，Body 与校验步字段一致（openapi/api_key/secret/telegram/deeplink_token 等）
日期: 2026-05-12
修改功能: onboarding 第 2 步独立路由 /onboarding/confirm；读 session 待绑定快照，确认后 POST 绑定并跳转成功页
-->
<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import OnboardingPanel from '@/features/onboarding/ui/OnboardingPanel.vue'
import { useAgentOnboardingRouteContext } from '@/shared/composables/useAgentOnboardingRouteContext'
import { errorMessageFromKy } from '@/shared/api/agentApiBinding'
import { postTradingApiBinding } from '@/shared/api/tradingApiBinding'
import {
  readAgentOnboardingPendingBind,
  clearAgentOnboardingPendingBind,
  saveAgentOnboardingBindResult,
  type AgentOnboardingPendingBind,
} from '@/shared/lib/agentOnboardingSession'

function newIdempotencyKey(): string {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID()
    }
  } catch {
    /* fallback */
  }
  return `idem-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`
}

function maskCredentialForDisplay(raw: string): string {
  const t = raw.trim()
  if (!t) return '—'
  if (t.length <= 8) return '••••••••'
  return `${t.slice(0, 4)}…${t.slice(-4)}`
}

const router = useRouter()
const { route, tgCardPrimary, showTgProfileMeta, tgProfileSummary, deeplinkToken } =
  useAgentOnboardingRouteContext()

const pendingBind = ref<AgentOnboardingPendingBind | null>(null)
const confirmBindLoading = ref(false)
const bindError = ref<string | null>(null)

const rowStyles = {
  label: { width: '112px', color: '#666666', fontSize: '13px' },
  content: { fontSize: '13px' },
} as const

onMounted(() => {
  const p = readAgentOnboardingPendingBind()
  if (!p) {
    void router.replace({ name: 'onboarding-validate', query: { ...route.query } })
    return
  }
  pendingBind.value = p
})

function backToValidate() {
  clearAgentOnboardingPendingBind()
  bindError.value = null
  void router.push({ name: 'onboarding-validate', query: { ...route.query } })
}

async function onConfirmBind() {
  const p = pendingBind.value
  if (!p) {
    bindError.value = '会话已过期，请返回上一步重新校验。'
    return
  }
  bindError.value = null
  confirmBindLoading.value = true
  try {
    const result = await postTradingApiBinding({
      openapiBaseUrl: p.openapiRoot,
      idempotencyKey: newIdempotencyKey(),
      apiKey: p.apiKey,
      apiSecret: p.apiSecret,
      subAccountId: p.subAccountId,
      deeplinkToken: deeplinkToken.value,
      ...(p.telegram ? { telegram: p.telegram } : {}),
    })
    clearAgentOnboardingPendingBind()
    const subId = result.agentSubAccountId?.trim() || p.subAccountId.trim()
    saveAgentOnboardingBindResult({
      agentSubAccountId: subId || undefined,
      saved: result.saved,
      agentTradingApiBindingStatus: result.agentTradingApiBindingStatus,
      bindingRowCreated: result.bindingRowCreated,
    })
    await router.push({ name: 'onboarding-success', query: { ...route.query } })
  } catch (e) {
    bindError.value = e instanceof Error ? e.message : await errorMessageFromKy(e)
  } finally {
    confirmBindLoading.value = false
  }
}
</script>

<template>
  <div class="dl-main__narrow">
    <div v-if="!pendingBind" class="dl-onboarding-route-loading" aria-busy="true">
      <a-spin size="large" />
    </div>
    <OnboardingPanel
      v-else
      title="绑定确认"
      subtitle="第 2 步：密钥已通过校验。请核对以下信息与上一步填写一致，确认后向服务端提交绑定。"
      :close-to="false"
      standalone
    >
      <p class="dl-onboarding-lead" style="margin-bottom: 14px">
        确认即调用绑定接口；服务端若返回子账户标识将优先展示，否则保留上一步填写的子账户 ID。
      </p>

      <div class="dl-description-wrap" style="margin-bottom: 18px">
        <a-descriptions
          :column="1"
          bordered
          size="small"
          :label-style="rowStyles.label"
          :content-style="rowStyles.content"
        >
          <a-descriptions-item label="Telegram">
            <span class="dl-onboarding-mono">{{ tgCardPrimary || '—' }}</span>
          </a-descriptions-item>
          <a-descriptions-item v-if="showTgProfileMeta" label="Telegram 资料">
            {{ tgProfileSummary }}
          </a-descriptions-item>
          <a-descriptions-item label="OpenAPI 基准地址">
            <span class="dl-onboarding-mono">{{ pendingBind.openapiRoot || '—' }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="子账户 API Key">
            <span class="dl-onboarding-mono">{{ maskCredentialForDisplay(pendingBind.apiKey) }}</span>
          </a-descriptions-item>
          <a-descriptions-item label="子账户 Secret Key">
            <span class="dl-onboarding-mono">••••••••（不展示，仅随确认提交）</span>
          </a-descriptions-item>
          <a-descriptions-item label="子账户 ID">
            <span class="dl-onboarding-mono">{{ pendingBind.subAccountId?.trim() || '—' }}</span>
          </a-descriptions-item>
        </a-descriptions>
      </div>

      <a-alert
        v-if="bindError"
        type="error"
        show-icon
        role="alert"
        class="dl-onboarding-alert"
        :message="bindError"
      />

      <a-button
        type="primary"
        size="large"
        block
        :loading="confirmBindLoading"
        class="dl-onboarding-submit-btn"
        @click="onConfirmBind"
      >
        确认绑定
      </a-button>
      <div class="dl-onboarding-result__secondary">
        <a-button type="link" size="small" :disabled="confirmBindLoading" @click="backToValidate">
          返回修改
        </a-button>
      </div>
    </OnboardingPanel>
  </div>
</template>
