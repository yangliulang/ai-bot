<!--
作者: 杨永的Agent
日期: 2026-05-13
修改功能: 成功页「返回 Telegram 对话」随环境 / `VITE_TELEGRAM_BOT_URL` / `tg_bot` query（见 onboarding.ts）
日期: 2026-05-12
修改功能: 已绑定态用中性 surface + 左色条 callout，避免 success alert 双层绿色堆叠
日期: 2026-05-12
修改功能: 「已绑定」横幅仅在 `bindingRowCreated === false`（服务端 UPDATE / 重复绑定）时展示
修改功能: 若 session 中为 `saved` + `agentTradingApiBindingStatus === 'BOUND'`，展示「已完成绑定」成功提示条
日期: 2026-05-12
修改功能: 成功页子账户行仅展示服务端返回；bind 与 validate 同源 httpClient
日期: 2026-05-12
修改功能: onboarding 第 3 步独立路由 /onboarding/success；读 session 绑定结果；无则退回校验页
-->
<script setup lang="ts">
import { CheckCircleFilled, LinkOutlined } from '@ant-design/icons-vue'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import OnboardingPanel from '@/features/onboarding/ui/OnboardingPanel.vue'
import { useAgentOnboardingRouteContext } from '@/shared/composables/useAgentOnboardingRouteContext'
import {
  readAgentOnboardingBindResult,
  clearAgentOnboardingFlowSession,
  type AgentOnboardingBindResult,
} from '@/shared/lib/agentOnboardingSession'
import { OPENAPI_BASE_STORAGE_KEY } from '@/shared/lib/openapiBaseUrl'

const router = useRouter()
const { route, tgCardPrimary, telegramBotOpenUrl } = useAgentOnboardingRouteContext()

const bindResult = ref<AgentOnboardingBindResult | null>(null)

const successSubaccountDisplay = computed(() => {
  if (!bindResult.value) return ''
  const id = bindResult.value.agentSubAccountId?.trim()
  if (id) return id
  return '—'
})

/** 重复绑定：服务端在同一 tg 上 UPDATE 已有行时 `bindingRowCreated === false` */
const showBoundConfirmedBanner = computed(() => {
  const r = bindResult.value
  if (!r) return false
  return (
    r.saved === true &&
    r.agentTradingApiBindingStatus === 'BOUND' &&
    r.bindingRowCreated === false
  )
})

const rowStyles = {
  label: { width: '112px', color: '#666666', fontSize: '13px' },
  content: { fontSize: '13px' },
} as const

onMounted(() => {
  const stored = readAgentOnboardingBindResult()
  if (!stored) {
    void router.replace({ name: 'onboarding-validate', query: { ...route.query } })
    return
  }
  bindResult.value = stored
})

function resetFlow() {
  clearAgentOnboardingFlowSession()
  try {
    sessionStorage.removeItem(OPENAPI_BASE_STORAGE_KEY)
  } catch {
    /* ignore */
  }
  void router.push({ name: 'onboarding-validate', query: { ...route.query } })
}
</script>

<template>
  <div class="dl-main__narrow">
    <div v-if="!bindResult" class="dl-onboarding-route-loading" aria-busy="true">
      <a-spin size="large" />
    </div>
    <OnboardingPanel
      v-else title="绑定完成" tone="success" :close-to="false" standalone>
      <div
        class="dl-onboarding-result"
        :class="{ 'dl-onboarding-result--bound': showBoundConfirmedBanner }"
      >
        <div class="dl-success-icon-wrap" aria-hidden="true">
          <CheckCircleFilled />
        </div>
        <p class="dl-onboarding-result__title">绑定成功</p>
        <span class="dl-onboarding-result__lead">
          请在该子账户<strong>现货 USDT</strong>预留扣费余额，然后返回 Telegram 继续使用 Bot。
        </span>
        <div
          v-if="showBoundConfirmedBanner"
          class="dl-onboarding-bound-callout"
          role="status"
          aria-live="polite"
        >
          <span class="dl-onboarding-bound-callout__accent" aria-hidden="true" />
          <div class="dl-onboarding-bound-callout__body">
            <span class="dl-onboarding-bound-callout__badge">已绑定</span>
            <p class="dl-onboarding-bound-callout__title">服务端已确认，当前账户处于已绑定状态</p>
            <p class="dl-onboarding-bound-callout__detail">
              无需再次绑定；可直接点击下方按钮返回 Telegram 使用 Bot。
            </p>
          </div>
        </div>
      </div>

      <div class="dl-description-wrap dl-onboarding-result__summary">
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
          <a-descriptions-item label="子账户">
            <span class="dl-onboarding-mono">{{ successSubaccountDisplay }}</span>
          </a-descriptions-item>
        </a-descriptions>
      </div>

      <div class="dl-success-steps dl-success-steps--compact">
        <span class="dl-onboarding-result__next">
          首次打开 Bot 请先点「Start」，再对话或下单。
        </span>
      </div>

      <a-button
        type="primary"
        size="large"
        block
        :href="telegramBotOpenUrl"
        target="_blank"
        rel="noreferrer"
        class="dl-onboarding-submit-btn"
      >
        <template #icon>
          <LinkOutlined />
        </template>
        返回 Telegram 对话
      </a-button>
      <div class="dl-onboarding-result__secondary">
        <a-button type="link" size="small" @click="resetFlow">重新配置</a-button>
      </div>
    </OnboardingPanel>
  </div>
</template>
