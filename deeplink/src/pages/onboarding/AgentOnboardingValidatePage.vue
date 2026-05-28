<!--
作者: 杨永的Agent
日期: 2026-05-13
修改功能: 表单项文案改为「子账户 API Key / 子账户 Secret Key」
作者: 杨永的Agent
日期: 2026-05-13
修改功能: 校验表单增加「子账户 ID」并随 validate / bind POST 提交 `sub_account_id`
作者: 杨永的Agent
日期: 2026-05-12
修改功能: 进入本页时清除上一轮绑定成功会话态（bind result），避免误开 /success 看到过期结论；不清理 pending（支持浏览器返回）
-->
<script setup lang="ts">
import { SafetyCertificateOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import OnboardingPanel from '@/features/onboarding/ui/OnboardingPanel.vue'
import { useAgentOnboardingRouteContext } from '@/shared/composables/useAgentOnboardingRouteContext'
import { errorMessageFromKy, validateAgentApiKeys } from '@/shared/api/agentApiBinding'
import {
  saveAgentOnboardingPendingBind,
  clearAgentOnboardingBindResult,
} from '@/shared/lib/agentOnboardingSession'
import {
  DEFAULT_OPENAPI_BASE_URL,
  isProbablyValidOpenapiBaseUrl,
  normalizeOpenapiBaseUrl,
  OPENAPI_BASE_STORAGE_KEY,
} from '@/shared/lib/openapiBaseUrl'
import { buildTelegramInboundPayload } from '@/shared/lib/onboarding'

type BindFormValues = {
  openapiBaseUrl: string
  subAccountId: string
  apiKey: string
  apiSecret: string
  agree: boolean
}

const router = useRouter()
const {
  route,
  effectivePrefill,
  legacyUsernamePlain,
  tgCardPrimary,
  hasTgIdentity,
  tgProfileSummary,
  showTgProfileMeta,
} = useAgentOnboardingRouteContext()

const loading = ref(false)
const errorMsg = ref<string | null>(null)

const formState = reactive<BindFormValues>({
  openapiBaseUrl: DEFAULT_OPENAPI_BASE_URL,
  subAccountId: '',
  apiKey: '',
  apiSecret: '',
  agree: false,
})

function persistOpenapiBaseUrl() {
  try {
    sessionStorage.setItem(OPENAPI_BASE_STORAGE_KEY, formState.openapiBaseUrl)
  } catch {
    /* ignore */
  }
}

watch(
  () => formState.openapiBaseUrl,
  () => persistOpenapiBaseUrl(),
)

function onOpenapiBaseBlur() {
  if (!isProbablyValidOpenapiBaseUrl(formState.openapiBaseUrl)) {
    message.warning('OpenAPI 基准地址无效，已恢复默认地址')
    formState.openapiBaseUrl = DEFAULT_OPENAPI_BASE_URL
    persistOpenapiBaseUrl()
    return
  }
  formState.openapiBaseUrl = normalizeOpenapiBaseUrl(formState.openapiBaseUrl)
  persistOpenapiBaseUrl()
}

onMounted(() => {
  clearAgentOnboardingBindResult()
  try {
    const saved = sessionStorage.getItem(OPENAPI_BASE_STORAGE_KEY)?.trim()
    if (saved) formState.openapiBaseUrl = normalizeOpenapiBaseUrl(saved)
  } catch {
    /* ignore */
  }
})

async function agreeRuleValidator(_rule: unknown, v: boolean) {
  if (v) return Promise.resolve()
  return Promise.reject(new Error('请先阅读并勾选确认'))
}

const agreeFormRules = [{ validator: agreeRuleValidator }]

const openapiFormRules = [
  {
    validator: async (_rule: unknown, v: string) => {
      const t = String(v ?? '').trim()
      if (!t) return Promise.reject(new Error('请填写 OpenAPI 基准地址'))
      if (!isProbablyValidOpenapiBaseUrl(t)) {
        return Promise.reject(new Error('OpenAPI 基准地址格式无效'))
      }
      return Promise.resolve()
    },
  },
]

const subAccountIdFormRules = [
  {
    validator: async (_rule: unknown, v: string) => {
      const t = String(v ?? '').trim()
      if (!t) return Promise.reject(new Error('请填写子账户 ID'))
      if (t.length > 128) return Promise.reject(new Error('子账户 ID 过长'))
      return Promise.resolve()
    },
  },
]

async function onFinish(values: BindFormValues) {
  errorMsg.value = null
  const subAccountId = values.subAccountId.trim()
  const apiKey = values.apiKey.trim()
  const apiSecret = values.apiSecret.trim()
  if (!apiKey || !apiSecret) {
    errorMsg.value = '请填写子账户 API Key 与子账户 Secret Key。'
    return
  }

  const openapiRoot = normalizeOpenapiBaseUrl(values.openapiBaseUrl)
  formState.openapiBaseUrl = openapiRoot
  persistOpenapiBaseUrl()

  const telegram = buildTelegramInboundPayload(
    effectivePrefill.value,
    legacyUsernamePlain.value || undefined,
  )

  loading.value = true
  try {
    await validateAgentApiKeys({
      api_key: apiKey,
      secret_key: apiSecret,
      openapi_base_url: openapiRoot,
      sub_account_id: subAccountId,
      ...(telegram ? { telegram } : {}),
    })

    saveAgentOnboardingPendingBind({
      apiKey,
      apiSecret,
      openapiRoot,
      subAccountId,
      ...(telegram ? { telegram } : {}),
    })
    message.success('密钥校验通过，请核对信息后确认绑定')
    await router.push({ name: 'onboarding-confirm', query: { ...route.query } })
  } catch (e) {
    errorMsg.value = e instanceof Error ? e.message : await errorMessageFromKy(e)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="dl-main__narrow">
    <OnboardingPanel
      title="绑定交易助手"
      subtitle="第 1 步：确认 Telegram 后填入子账户 API Key 与 Secret Key；点「校验」仅验证密钥，通过后进入下一页确认绑定。"
      :close-to="false"
      standalone
    >
      <section class="dl-onboarding-block" aria-labelledby="onboarding-tg-heading">
        <h3 id="onboarding-tg-heading" class="dl-onboarding-section-title">Telegram</h3>
        <div class="dl-onboarding-tg-card">
          <div class="dl-onboarding-tg-card__icon" aria-hidden="true">
            <SafetyCertificateOutlined />
          </div>
          <div class="dl-onboarding-tg-card__body">
            <div class="dl-onboarding-tg-card__label">Telegram</div>
            <div
              v-if="hasTgIdentity"
              class="dl-onboarding-tg-card__value dl-onboarding-mono"
            >
              {{ tgCardPrimary }}
            </div>
            <div v-else class="dl-onboarding-tg-card__value dl-onboarding-tg-card__value--muted">
              未识别（请从 Bot 链接进入）
            </div>
            <div v-if="showTgProfileMeta" class="dl-onboarding-tg-card__meta">
              {{ tgProfileSummary }}
            </div>
          </div>
        </div>
        <p v-if="!hasTgIdentity" class="dl-onboarding-footnote">
          请从 Bot 携带的链接进入；调试可加
          <span class="dl-onboarding-mono">?tg_username=demo</span>
          或
          <span class="dl-onboarding-mono">tg_id</span>
          /
          <span class="dl-onboarding-mono">tg_first_name</span>
          等参数（与首页入站写入的会话一致）。
        </p>
      </section>

      <a-divider class="dl-onboarding-divider" />

      <section class="dl-onboarding-block" aria-labelledby="onboarding-api-heading">
        <p class="dl-onboarding-lead">
          须填写<strong>子账户</strong>的 API Key 与 Secret Key；用于校验与托管，请勿泄露。
        </p>
        <p class="dl-onboarding-openapi-doc">
          交易所 REST 网关根（文档
          <a
            href="https://exchangedocsv2.gitbook.io/open-api-doc-v2"
            target="_blank"
            rel="noopener noreferrer"
            class="dl-link-muted"
          >OpenAPI</a>
          中的 <code class="dl-onboarding-openapi-code">baseurl</code>）须与所内一致；默认为常见
          <code class="dl-onboarding-openapi-code">openapi</code>
          子域示例，可按环境改写。点击「校验」后将请求服务端验证密钥。
        </p>
        <a-form
          :model="formState"
          layout="vertical"
          :required-mark="false"
          :scroll-to-first-error="{ behavior: 'smooth', block: 'center' }"
          @finish="onFinish"
        >
          <a-form-item
            label="OpenAPI 基准地址"
            name="openapiBaseUrl"
            :rules="openapiFormRules"
          >
            <a-input
              v-model:value="formState.openapiBaseUrl"
              size="large"
              placeholder="https://openapi.coobit.cc"
              autocomplete="off"
              :disabled="loading"
              @blur="onOpenapiBaseBlur"
            />
          </a-form-item>
          <a-form-item label="子账户 ID" name="subAccountId" :rules="subAccountIdFormRules">
            <a-input
              v-model:value="formState.subAccountId"
              size="large"
              autocomplete="off"
              placeholder="交易所子账户 ID（非 API Key）"
              :disabled="loading"
            />
          </a-form-item>
          <a-form-item
            label="子账户 API Key"
            name="apiKey"
            :rules="[{ required: true, message: '请粘贴子账户 API Key' }]"
          >
            <a-input
              v-model:value="formState.apiKey"
              size="large"
              autocomplete="off"
              placeholder="子账户 API Key"
              :disabled="loading"
            />
          </a-form-item>
          <a-form-item
            label="子账户 Secret Key"
            name="apiSecret"
            :rules="[{ required: true, message: '请粘贴子账户 Secret Key' }]"
          >
            <a-input-password
              v-model:value="formState.apiSecret"
              size="large"
              autocomplete="new-password"
              placeholder="子账户 Secret Key"
              :disabled="loading"
            />
          </a-form-item>

          <a-alert
            v-if="errorMsg"
            type="error"
            show-icon
            role="alert"
            class="dl-onboarding-alert"
            :message="errorMsg"
          />

          <a-form-item
            name="agree"
            :value-prop-name="'checked'"
            class="dl-consent-row--form-item"
            :rules="agreeFormRules"
          >
            <div class="dl-consent-row">
              <a-checkbox v-model:checked="formState.agree">
                <span class="dl-onboarding-consent-text">
                  授权用于查询与交易；<strong>不提币</strong>、不改安全设置；风险自担。
                </span>
              </a-checkbox>
            </div>
          </a-form-item>

          <a-form-item class="dl-onboarding-submit-wrap">
            <a-button
              type="primary"
              html-type="submit"
              size="large"
              block
              :loading="loading"
              class="dl-onboarding-submit-btn"
            >
              校验
            </a-button>
          </a-form-item>
        </a-form>
      </section>

      <p class="dl-onboarding-footnote dl-onboarding-footnote--center">
        校验失败时请按提示核对交易所侧权限与子账户状态。
      </p>
    </OnboardingPanel>
  </div>
</template>
