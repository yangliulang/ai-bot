<!--
作者: 杨永的Agent
日期: 2026-05-20
修改功能: §3/§4 改 **PATCH …/telegram/bot**（`runtimeParams`）；移除 localStorage 演示持久化
作者: 杨永的Agent
日期: 2026-05-20
修改功能: 按 product-doc 原型重构 Telegram · Bot 接入（四段：Bot / Webhook / 渠道能力 / 体验）
-->
<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'

import {
  DEFAULT_TELEGRAM_CHANNEL_UX,
  runtimeParamsFromUxForm,
  uxFormFromRuntimeParams,
  type TelegramChannelUxForm,
} from '@/entities/telegram/telegram-runtime-params'
import {
  AppError,
  deleteTelegramWebhook,
  getTelegramBotStatus,
  getTelegramWebhook,
  patchTelegramBot,
  postTelegramSelfTest,
  setTelegramWebhook,
  type TelegramBotStatus,
  type TelegramWebhookInfo,
  type TelegramWebhookSetPayload,
} from '@/shared/api'
import { telegramDeliveryHints } from '@/shared/lib/telegramDeliveryHints'
import { adminNotifyManualRefresh, adminToastError, adminToastSuccess } from '@/shared/lib/admin-toast'
import { useAsyncAction } from '@/shared/lib/useAsyncAction'
import AdminPage from '@/shared/ui/AdminPage.vue'
import AdminPageHeader from '@/shared/ui/AdminPageHeader.vue'
import UiButton from '@/shared/ui/UiButton.vue'
import UiInput from '@/shared/ui/UiInput.vue'
import UiModal from '@/shared/ui/UiModal.vue'
import UiSelect from '@/shared/ui/UiSelect.vue'
import UiSwitch from '@/shared/ui/UiSwitch.vue'
import type { UiSelectOption } from '@/shared/ui/UiSelect.vue'

const botStatus = ref<TelegramBotStatus | null>(null)
const configVersion = ref<number | null>(null)
const webhookInfo = ref<TelegramWebhookInfo | null>(null)
const loadError = ref<string | null>(null)
const configSaveLoading = ref(false)

const webhookUrlInput = ref('')
const webhookSecretInput = ref('')
const confirmDeleteOpen = ref(false)

const ux = ref<TelegramChannelUxForm>({ ...DEFAULT_TELEGRAM_CHANNEL_UX })

const localeOptions: UiSelectOption[] = [
  { value: 'zh-CN', label: '中文（简体）' },
  { value: 'zh-TW', label: '中文（繁体）' },
  { value: 'en-US', label: 'English (US)' },
]

const botHook = useAsyncAction(() => getTelegramBotStatus())
const webhookHook = useAsyncAction(() => getTelegramWebhook())
const setHook = useAsyncAction((payload: TelegramWebhookSetPayload) => setTelegramWebhook(payload))
const deleteHook = useAsyncAction(() => deleteTelegramWebhook())
const selfTestHook = useAsyncAction(() => postTelegramSelfTest())

const pageLoading = computed(
  () => botHook.loading.value || (webhookHook.loading.value && !webhookInfo.value),
)

const webhookRegistered = computed(() =>
  Boolean(webhookInfo.value?.url && webhookInfo.value.url.length > 0),
)

const webhookHealth = computed<'ok' | 'degraded' | 'unknown'>(() => {
  if (!webhookInfo.value) return 'unknown'
  if (webhookInfo.value.lastErrorMessage?.trim()) return 'degraded'
  if (webhookRegistered.value) return 'ok'
  return 'unknown'
})

const webhookHealthLabel = computed(() => {
  switch (webhookHealth.value) {
    case 'ok':
      return '回调可达 · 最近探测无投递错误'
    case 'degraded':
      return '待确认 · 存在最近投递错误或尚未登记'
    default:
      return '未探测'
  }
})

const botUsernameDisplay = computed(() => {
  const u = botStatus.value?.bot?.username?.trim()
  return u ? `@${u}` : '—'
})

const lastErrorLabel = computed(() => {
  const d = webhookInfo.value?.lastErrorDate
  if (d === null || d === undefined) return ''
  try {
    return new Date(d * 1000).toLocaleString()
  } catch {
    return String(d)
  }
})

const deliveryHints = computed(() =>
  telegramDeliveryHints(webhookInfo.value?.lastErrorMessage),
)

watch(
  () => webhookInfo.value?.url,
  (url) => {
    if (url && !webhookUrlInput.value.trim()) {
      webhookUrlInput.value = url
    }
  },
  { immediate: true },
)

function applyBotStatus(bot: TelegramBotStatus) {
  botStatus.value = bot
  configVersion.value = bot.configVersion ?? null
  ux.value = uxFormFromRuntimeParams(bot.runtimeParams ?? undefined)
}

async function refreshAll(toastOnSuccess = false) {
  loadError.value = null
  try {
    const [bot, wh] = await Promise.all([botHook.run(), webhookHook.run()])
    if (bot !== undefined) applyBotStatus(bot)
    if (wh !== undefined) webhookInfo.value = wh
    adminNotifyManualRefresh(toastOnSuccess, {
      ok: !loadError.value,
      successMessage: '已刷新',
      errorMessage: loadError.value,
    })
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '加载失败'
    loadError.value = msg
    adminNotifyManualRefresh(toastOnSuccess, { ok: false, successMessage: '已刷新', errorMessage: msg })
  }
}

async function saveRuntimeParams(section: 'capabilities' | 'ux') {
  loadError.value = null
  configSaveLoading.value = true
  try {
    const next = await patchTelegramBot(
      { runtimeParams: runtimeParamsFromUxForm(ux.value) },
      { ifMatch: configVersion.value },
    )
    applyBotStatus(next)
    adminToastSuccess(
      section === 'capabilities'
        ? '渠道能力已保存（PATCH runtimeParams）'
        : '用户体验配置已保存（PATCH runtimeParams）',
    )
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '保存失败'
    const status = e instanceof AppError ? e.status : undefined
    if (status === 409) {
      const detail = `${msg}：配置已被他人更新，请刷新后重试。`
      loadError.value = detail
      adminToastError(detail)
      await refreshAll(false)
    } else if (status === 405 || status === 404) {
      const detail =
        `${msg}：服务端尚未开放 PATCH /api/v1/admin/channels/telegram/bot，请由 /be 落地 FR-TG-ADMIN-02 后重试。`
      loadError.value = detail
      adminToastError(detail)
    } else {
      loadError.value = msg
      adminToastError(msg)
    }
  } finally {
    configSaveLoading.value = false
  }
}

async function saveWebhookParams() {
  loadError.value = null
  const url = webhookUrlInput.value.trim()
  const payload: TelegramWebhookSetPayload = {}
  if (url) payload.url = url
  if (webhookSecretInput.value.trim()) payload.secretToken = webhookSecretInput.value.trim()
  try {
    const next = await setHook.run(Object.keys(payload).length ? payload : {})
    if (next !== undefined) {
      webhookInfo.value = next
      adminToastSuccess('Webhook 参数已提交至 Telegram（setWebhook）')
    }
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '保存失败'
    loadError.value = msg
    adminToastError(msg)
  }
}

async function applyDefaultWebhook() {
  loadError.value = null
  try {
    const next = await setHook.run({})
    if (next !== undefined) {
      webhookInfo.value = next
      webhookUrlInput.value = next.url || ''
      adminToastSuccess('已使用服务端默认 URL 注册 / 更新（PUBLIC_BASE_URL）')
    }
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '注册失败'
    loadError.value = msg
    adminToastError(msg)
  }
}

async function runSelfTest() {
  loadError.value = null
  try {
    const result = await selfTestHook.run()
    if (result === undefined) return
    await refreshAll()
    if (result.getMeOk && result.getWebhookInfoOk && !result.errorSummary) {
      adminToastSuccess('测试连接成功：getMe 与 getWebhookInfo 均正常')
    } else {
      const msg = result.errorSummary || '自检未完全通过，请查看 Webhook 投递错误'
      loadError.value = msg
      adminToastError(msg)
    }
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '测试连接失败'
    loadError.value = msg
    adminToastError(msg)
  }
}

async function confirmedDeleteWebhook() {
  loadError.value = null
  try {
    const next = await deleteHook.run()
    if (next !== undefined) {
      webhookInfo.value = next
      adminToastSuccess('Webhook 已从 Telegram 删除')
      confirmDeleteOpen.value = false
    }
  } catch (e) {
    const msg = e instanceof AppError ? e.message : '删除失败'
    loadError.value = msg
    adminToastError(msg)
  }
}

function saveCapabilities() {
  void saveRuntimeParams('capabilities')
}

function saveUx() {
  void saveRuntimeParams('ux')
}

onMounted(() => {
  void refreshAll()
})
</script>

<template>
  <AdminPage>
    <AdminPageHeader
      title="Telegram · Bot 接入控制台"
      :badges="[{ label: 'Bot 接入', tone: 'emerald' }]"
      description="单一 Runtime Agent 下的 Telegram 接入：Bot 身份、Webhook、渠道能力闸与体验配置（不与 Prompt 治理叠床架屋）。"
      dev-meta="pageId · sys.channels"
      :crumbs="[
        { label: '渠道管理', to: '/system/channels' },
        { label: 'Bot 接入' },
      ]"
    >
      <template #actions>
        <UiButton variant="secondary" type="button" size="sm" :loading="pageLoading" @click="refreshAll(true)">
          刷新全部
        </UiButton>
      </template>
    </AdminPageHeader>

    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-0.5"
      enter-to-class="opacity-100 translate-y-0"
    >
      <p
        v-if="loadError"
        role="alert"
        class="rounded-[var(--radius-ui-lg)] border border-rose-500/35 bg-rose-950/25 px-4 py-3 text-sm text-rose-100"
      >
        {{ loadError }}
      </p>
    </Transition>

    <section
      v-if="botStatus?.publicBaseUrl || botStatus?.bindPageUrl"
      class="admin-panel border-emerald-900/30 bg-emerald-950/10 px-4 py-4 sm:px-5"
    >
      <h2 class="text-sm font-semibold text-emerald-200/95">与本机 server/.env 对齐（只读）</h2>
      <p class="mt-2 text-xs leading-relaxed text-slate-500">
        下列值由 <strong class="font-normal text-slate-400">Agent API（8080）</strong> 进程读取
        <code class="text-slate-600">server/.env</code> 后回显；<strong class="font-normal text-slate-400"
          >Admin（5173）</strong
        >
        自身不配置这两项。修改 .env 后须<strong class="font-normal text-slate-400">重启 Agent</strong>，再点「刷新全部」与「使用默认
        URL 注册 / 更新」。
      </p>
      <dl class="mt-4 space-y-3 text-xs">
        <div>
          <dt class="font-medium text-slate-500">CHAINUP_AGENT_PUBLIC_BASE_URL</dt>
          <dd class="mt-1 break-all font-mono text-sm text-slate-200">
            {{ botStatus?.publicBaseUrl || '（未设置）' }}
          </dd>
          <dd class="mt-1 text-slate-600">Telegram Webhook 公网根；拼出默认回调路径 /webhook/telegram/…</dd>
        </div>
        <div>
          <dt class="font-medium text-slate-500">CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL</dt>
          <dd class="mt-1 break-all font-mono text-sm text-slate-200">
            {{ botStatus?.bindPageUrl || '（未设置）' }}
          </dd>
          <dd class="mt-1 text-slate-600">
            未绑定用户收 Bot 消息时的 Deeplink 入口（非本页 §4 演示字段）；须与 ngrok 隧道同源且为 https。
          </dd>
        </div>
        <div v-if="botStatus?.defaultWebhookUrl">
          <dt class="font-medium text-slate-500">默认 Webhook（setWebhook 空 body 时）</dt>
          <dd class="mt-1 break-all font-mono text-sm text-slate-200">
            {{ botStatus.defaultWebhookUrl }}
          </dd>
        </div>
      </dl>
    </section>

    <div class="space-y-6">
      <!-- 1. Bot 基础配置 -->
      <section class="admin-panel overflow-hidden">
        <div class="border-b border-slate-800/80 px-4 py-3 sm:px-5">
          <h2 class="text-sm font-semibold text-white">1. Bot 基础配置</h2>
          <p class="mt-1 text-xs leading-relaxed text-slate-500">
            全渠道共用同一编排与 Agent；渠道层仅负责 Telegram Bot 接入与能力闸。Token 由服务端环境变量托管（
            <code class="text-slate-600">CHAINUP_AGENT_TELEGRAM_BOT_TOKEN</code>），控制台不采集明文。
          </p>
        </div>
        <div class="space-y-4 px-4 py-4 sm:px-5">
          <div v-if="pageLoading && !botStatus" class="h-20 animate-pulse rounded-md bg-slate-800/60" />
          <template v-else>
            <div class="grid gap-4 sm:grid-cols-2">
              <div>
                <label class="mb-1.5 block text-xs font-medium text-slate-400">Bot Token</label>
                <UiInput
                  model-value="••••••••••••••••"
                  label="Bot Token"
                  :standalone-field="true"
                  disabled
                  placeholder="由运维在 server/.env 配置"
                />
                <p class="mt-1.5 text-xs text-slate-600">
                  指纹：
                  <span class="font-mono text-slate-500">{{
                    botStatus?.secretRefFingerprint || '未配置'
                  }}</span>
                </p>
              </div>
              <div>
                <label class="mb-1.5 block text-xs font-medium text-slate-400">Bot Username</label>
                <UiInput
                  :model-value="botUsernameDisplay"
                  label="Bot Username"
                  :standalone-field="true"
                  disabled
                />
                <p v-if="botStatus?.lastErrorSummary" class="mt-1.5 text-xs text-amber-400/90">
                  {{ botStatus.lastErrorSummary }}
                </p>
              </div>
            </div>
            <p class="text-xs text-slate-600">
              身份数据来自 <code class="text-slate-500">GET /api/v1/admin/channels/telegram/bot</code>（getMe）。
              轮换 Token 须在服务器更新环境变量后重新注册 Webhook。
            </p>
          </template>
        </div>
      </section>

      <!-- 2. Webhook -->
      <section class="admin-panel overflow-hidden">
        <div class="border-b border-slate-800/80 px-4 py-3 sm:px-5">
          <h2 class="text-sm font-semibold text-white">2. Webhook</h2>
        </div>
        <div class="space-y-4 px-4 py-4 sm:px-5">
          <div>
            <p class="text-xs text-slate-500">回调状态</p>
            <p class="mt-1">
              <span
                class="inline-flex rounded-full border px-2.5 py-0.5 text-xs font-medium"
                :class="
                  webhookHealth === 'ok'
                    ? 'border-emerald-600/45 bg-emerald-950/35 text-emerald-300/95'
                    : webhookHealth === 'degraded'
                      ? 'border-amber-500/35 bg-amber-950/25 text-amber-200/90'
                      : 'border-slate-700 bg-slate-900/50 text-slate-500'
                "
              >
                {{ webhookHealthLabel }}
              </span>
            </p>
          </div>

          <div class="grid gap-4 max-w-2xl">
            <UiInput
              v-model="webhookUrlInput"
              label="Webhook URL"
              placeholder="https://…/webhook/telegram/…"
              autocomplete="off"
            />
            <UiInput
              v-model="webhookSecretInput"
              label="Webhook Secret"
              type="password"
              placeholder="可选 · 对应 X-Telegram-Bot-Api-Secret-Token"
              autocomplete="off"
            />
          </div>

          <dl
            v-if="webhookInfo"
            class="grid gap-2 rounded-[var(--radius-ui)] border border-slate-800/80 bg-slate-950/30 px-3 py-3 text-xs sm:grid-cols-2"
          >
            <div>
              <dt class="text-slate-500">待投递更新</dt>
              <dd class="font-mono text-slate-200">{{ webhookInfo.pendingUpdateCount }}</dd>
            </div>
            <div>
              <dt class="text-slate-500">自定义证书</dt>
              <dd class="text-slate-200">{{ webhookInfo.hasCustomCertificate ? '是' : '否' }}</dd>
            </div>
          </dl>

          <div
            v-if="webhookInfo?.lastErrorMessage"
            class="rounded-[var(--radius-ui)] border border-amber-500/25 bg-amber-950/20 px-3 py-2.5"
            role="status"
          >
            <p class="text-xs font-medium uppercase tracking-wide text-amber-400/90">
              Telegram 最近投递错误
            </p>
            <p v-if="lastErrorLabel" class="mt-1 font-mono text-xs text-amber-200/85">
              {{ lastErrorLabel }}
            </p>
            <p class="mt-1 break-words font-mono text-sm text-amber-100/90 whitespace-pre-wrap">
              {{ webhookInfo.lastErrorMessage }}
            </p>
            <ul
              v-if="deliveryHints.length"
              class="mt-3 space-y-2 border-t border-amber-500/15 pt-3 text-xs text-amber-200/85"
            >
              <li v-for="(hint, i) in deliveryHints" :key="i">– {{ hint }}</li>
            </ul>
          </div>

          <div class="flex flex-wrap gap-2">
            <UiButton type="button" :loading="setHook.loading.value" @click="saveWebhookParams">
              保存 Webhook 参数
            </UiButton>
            <UiButton
              type="button"
              variant="secondary"
              :loading="selfTestHook.loading.value"
              @click="runSelfTest"
            >
              测试连接
            </UiButton>
            <UiButton type="button" variant="secondary" :loading="setHook.loading.value" @click="applyDefaultWebhook">
              使用默认 URL 注册 / 更新
            </UiButton>
            <UiButton type="button" variant="danger" @click="confirmDeleteOpen = true">
              删除 Webhook
            </UiButton>
          </div>
        </div>
      </section>

      <!-- 3. 渠道能力 -->
      <section class="admin-panel overflow-hidden">
        <div class="border-b border-slate-800/80 px-4 py-3 sm:px-5">
          <h2 class="text-sm font-semibold text-white">3. 渠道能力</h2>
          <p class="mt-1 text-xs text-slate-600">
            写入
            <code class="text-slate-500">PATCH /api/v1/admin/channels/telegram/bot</code>
            之 <code class="text-slate-500">runtimeParams</code>（§3 键名待 keys.md 终裁；与 §4 一并提交）。
          </p>
        </div>
        <div class="space-y-4 px-4 py-4 sm:px-5">
          <label class="flex items-center justify-between gap-3 text-sm text-slate-300">
            <span>允许交易</span>
            <UiSwitch v-model="ux.tradeOk" size="sm" aria-label="允许交易" />
          </label>
          <label class="flex flex-wrap items-center justify-between gap-3 text-sm text-slate-300">
            <span class="min-w-0">
              自动执行
              <span class="ml-2 text-xs text-slate-600">与人工确认规则、运行场景协同</span>
            </span>
            <UiSwitch v-model="ux.autoExec" size="sm" aria-label="自动执行" />
          </label>
          <label class="flex items-center justify-between gap-3 text-sm text-slate-300">
            <span>语音输入</span>
            <UiSwitch v-model="ux.voiceOk" size="sm" aria-label="语音输入" />
          </label>
          <label class="flex items-center justify-between gap-3 text-sm text-slate-300">
            <span>文件上传</span>
            <UiSwitch v-model="ux.fileOk" size="sm" aria-label="文件上传" />
          </label>
          <UiButton type="button" :loading="configSaveLoading" @click="saveCapabilities">
            保存能力开关
          </UiButton>
        </div>
      </section>

      <!-- 4. 用户体验 -->
      <section class="admin-panel overflow-hidden">
        <div class="border-b border-slate-800/80 px-4 py-3 sm:px-5">
          <h2 class="text-sm font-semibold text-white">4. 用户体验</h2>
          <p class="mt-1 text-xs text-slate-600">
            映射 keys.md §4.2：
            <code class="text-slate-500">TELEGRAM_DEFAULT_LOCALE</code>、
            <code class="text-slate-500">TELEGRAM_HELP_H5_URL_TEMPLATE</code>、开通欢迎语
            <code class="text-slate-500">TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_*</code>。
            绑定页仍由环境变量
            <code class="text-slate-500">CHAINUP_AGENT_TELEGRAM_BIND_PAGE_URL</code> 托管。
          </p>
        </div>
        <div class="max-w-xl space-y-4 px-4 py-4 sm:px-5">
          <UiSelect v-model="ux.defaultLocale" label="默认语言" :options="localeOptions" />
          <p class="text-xs leading-relaxed text-slate-500">
            开通欢迎语在交易员<strong class="font-medium text-slate-400">首次 API 绑定成功</strong>后，由 Bot
            在 Telegram 私聊发送<strong class="font-medium text-slate-400">一条</strong>（每用户仅一次）。模板可使用占位符
            <code class="text-slate-400">{displayName}</code>（优先显示名，否则 @用户名，否则「用户」）。单条不超过 4096
            字符。
          </p>
          <div>
            <label class="mb-1.5 block text-xs font-medium text-slate-400">开通欢迎语 · 简体中文</label>
            <textarea
              v-model="ux.welcomeZhCn"
              rows="3"
              class="w-full rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600/60"
              placeholder="TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_CN"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-medium text-slate-400">开通欢迎语 · 繁体中文</label>
            <textarea
              v-model="ux.welcomeZhTw"
              rows="3"
              class="w-full rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600/60"
              placeholder="TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_ZH_TW"
            />
          </div>
          <div>
            <label class="mb-1.5 block text-xs font-medium text-slate-400">开通欢迎语 · English</label>
            <textarea
              v-model="ux.welcomeEn"
              rows="3"
              class="w-full rounded-[var(--radius-ui)] border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white outline-none focus:border-emerald-600 focus:ring-1 focus:ring-emerald-600/60"
              placeholder="TELEGRAM_AGENT_ACTIVATION_WELCOME_TEXT_EN"
            />
          </div>
          <UiInput
            v-model="ux.deepLinkTemplate"
            label="H5 / 帮助链接模板"
            placeholder="https://…（TELEGRAM_HELP_H5_URL_TEMPLATE）"
            autocomplete="off"
          />
          <UiButton type="button" :loading="configSaveLoading" @click="saveUx">保存体验配置</UiButton>
        </div>
      </section>
    </div>

    <p class="text-xs text-slate-600">
      执行异常协查见
      <RouterLink class="text-emerald-400/95 hover:underline" to="/observability">
        执行链路协查
      </RouterLink>
      ；实例绑定见
      <RouterLink class="text-emerald-400/95 hover:underline" to="/agents/instances">
        Agent 实例
      </RouterLink>
      。
    </p>

    <UiModal
      v-model:open="confirmDeleteOpen"
      title="删除 Webhook"
      :show-default-close="false"
      description="Telegram 将停止向当前服务投递 Update；恢复需重新注册。"
    >
      <p class="text-sm text-slate-400">若仅调整公网地址，通常「注册 / 更新」即可，无需删除。</p>
      <template #footer>
        <UiButton variant="ghost" type="button" @click="confirmDeleteOpen = false">取消</UiButton>
        <UiButton
          variant="danger"
          type="button"
          :loading="deleteHook.loading.value"
          @click="confirmedDeleteWebhook"
        >
          确认删除
        </UiButton>
      </template>
    </UiModal>
  </AdminPage>
</template>
