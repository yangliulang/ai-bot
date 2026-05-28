<!--
作者: 杨永的Agent
日期: 2026-05-19
修改功能: 登录/注册双模式；注册对接 POST /api/auth/register（database · 首张/开放注册）
-->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { z } from 'zod'

import { AppError } from '@/shared/api/errors'
import { useAuthStore } from '@/stores/auth'
import { useAsyncAction } from '@/shared/lib/useAsyncAction'
import UiButton from '@/shared/ui/UiButton.vue'
import UiInput from '@/shared/ui/UiInput.vue'

import LoginBackdrop from './LoginBackdrop.vue'

type AuthMode = 'login' | 'register'

const loginFormSchema = z.object({
  username: z.string().trim().min(1, '请输入账户名').max(128, '账户名不能超过 128 个字符'),
  password: z.string().min(1, '请输入密码').max(256, '密码不能超过 256 个字符'),
})

const registerFormSchema = z
  .object({
    username: z.string().trim().min(1, '请输入账户名').max(128, '账户名不能超过 128 个字符'),
    password: z
      .string()
      .min(8, '注册口令至少 8 位')
      .max(256, '密码不能超过 256 个字符'),
    confirmPassword: z.string().min(1, '请再次输入密码'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: '两次输入的密码不一致',
    path: ['confirmPassword'],
  })

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const mode = ref<AuthMode>('login')
const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMsg = ref<string | null>(null)
const usernameError = ref<string | null>(null)
const passwordError = ref<string | null>(null)
const confirmPasswordError = ref<string | null>(null)

const redirectTo = computed(() => {
  const r = route.query.redirect
  return typeof r === 'string' && r.startsWith('/') ? r : '/runtime/executions'
})

const isRegister = computed(() => mode.value === 'register')

const modeHint = computed(() => {
  if (mode.value === 'login') {
    return '使用控制台账户登录'
  }
  return 'database 模式：空库可创建首张管理员（口令 ≥8）；已有账号时需服务端开放注册'
})

const { loading, run: runAuthFlow } = useAsyncAction(
  async (fields: { username: string; password: string }, authMode: AuthMode) => {
    if (authMode === 'register') {
      await auth.register(fields.username, fields.password)
    } else {
      await auth.login(fields.username, fields.password)
    }
    await router.replace(redirectTo.value)
  },
)

watch(mode, () => {
  errorMsg.value = null
  usernameError.value = null
  passwordError.value = null
  confirmPasswordError.value = null
  confirmPassword.value = ''
})

watch(username, () => {
  usernameError.value = null
  errorMsg.value = null
})

watch(password, () => {
  passwordError.value = null
  errorMsg.value = null
})

watch(confirmPassword, () => {
  confirmPasswordError.value = null
  errorMsg.value = null
})

function setMode(next: AuthMode) {
  if (loading.value) return
  mode.value = next
}

function validateFields(): { username: string; password: string } | null {
  usernameError.value = null
  passwordError.value = null
  confirmPasswordError.value = null

  if (mode.value === 'login') {
    const parsed = loginFormSchema.safeParse({
      username: username.value,
      password: password.value,
    })
    if (parsed.success) {
      username.value = parsed.data.username
      return parsed.data
    }
    for (const issue of parsed.error.issues) {
      const key = issue.path[0]
      if (key === 'username') usernameError.value = issue.message
      if (key === 'password') passwordError.value = issue.message
    }
    return null
  }

  const parsed = registerFormSchema.safeParse({
    username: username.value,
    password: password.value,
    confirmPassword: confirmPassword.value,
  })
  if (parsed.success) {
    username.value = parsed.data.username
    return { username: parsed.data.username, password: parsed.data.password }
  }
  for (const issue of parsed.error.issues) {
    const key = issue.path[0]
    if (key === 'username') usernameError.value = issue.message
    if (key === 'password') passwordError.value = issue.message
    if (key === 'confirmPassword') confirmPasswordError.value = issue.message
  }
  return null
}

async function onSubmit() {
  errorMsg.value = null
  const fields = validateFields()
  if (!fields) return
  try {
    await runAuthFlow(fields, mode.value)
  } catch (e) {
    errorMsg.value = e instanceof AppError || e instanceof Error ? e.message : '操作失败'
  }
}
</script>

<template>
  <div class="relative min-h-[100dvh] overflow-x-hidden bg-zinc-950 text-slate-100 antialiased">
    <LoginBackdrop />
    <div
      class="pointer-events-none absolute inset-0 bg-gradient-to-br from-zinc-950/20 via-transparent to-black/65"
      aria-hidden="true"
    />

    <div
      class="relative z-10 mx-auto grid min-h-[100dvh] w-full max-w-[1120px] grid-cols-1 content-center gap-y-10 px-[max(1rem,env(safe-area-inset-left))] py-[clamp(2rem,calc(env(safe-area-inset-top)+2rem),3.5rem)] pb-[clamp(2.5rem,calc(env(safe-area-inset-bottom)+2rem),4rem)] md:grid-cols-2 md:items-center md:gap-x-10 md:gap-y-14 lg:gap-x-16 xl:max-w-[1200px] xl:px-10"
    >
      <aside class="relative hidden md:block md:justify-self-start md:self-center lg:max-w-xl">
        <div class="relative z-[1] pr-4">
          <p class="text-[11px] font-mono uppercase tracking-[0.28em] text-emerald-500/90">
            Telegram Ops · Trading Runtime
          </p>
          <h1 class="mt-5">
            <span
              class="block text-[clamp(2.25rem,5.2vw,3.85rem)] font-semibold leading-[0.92] tracking-[-0.045em] text-white"
            >
              AI
              <span class="text-emerald-400/95">Agent</span>
            </span>
            <span
              class="mt-4 block border-t border-white/[0.06] pt-4 text-[clamp(0.95rem,1.85vw,1.2rem)] font-medium leading-snug tracking-[0.06em] text-zinc-500"
            >
              管理控制台
            </span>
          </h1>
          <p class="mt-6 max-w-md text-[15px] leading-relaxed text-zinc-500">
            编排渠道、运行时与账务策略。登录后仅在授权边界内会话；交易写操作永远在确认链之后生效。
          </p>
          <dl
            class="mt-9 border-l border-emerald-500/25 pl-5 font-mono text-[11px] leading-relaxed text-zinc-500"
          >
            <div>
              <dt class="inline text-emerald-500/80">01</dt>
              <span class="text-zinc-600">&middot;</span> 网关验签与子账户就绪
            </div>
            <div class="mt-2">
              <dt class="inline text-emerald-500/80">02</dt>
              <span class="text-zinc-600">&middot;</span> 门禁快照与扣费链路
            </div>
          </dl>
        </div>
      </aside>

      <div class="relative flex w-full justify-center md:justify-center md:self-center">
        <div
          class="admin-login-card w-full max-w-[412px] rounded-[var(--radius-ui-lg)] border border-white/10 bg-zinc-900/72 p-8 shadow-[0_28px_80px_-42px_rgb(0_0_0_/_0.75),inset_0_1px_0_0_rgb(255_255_255_/_0.05)] backdrop-blur-xl"
        >
          <div class="mb-6 text-center md:text-left">
            <h2 class="text-lg font-semibold tracking-tight text-white md:hidden">
              AI Agent 管理后台
            </h2>
            <h2 class="hidden text-lg font-semibold tracking-tight text-white md:block">
              {{ isRegister ? '注册管理员' : '登录' }}
            </h2>
            <p class="mt-1 text-sm leading-relaxed text-slate-400">
              {{ modeHint }}
            </p>
          </div>

          <div
            class="mb-6 grid grid-cols-2 gap-1 rounded-[var(--radius-ui)] border border-white/[0.08] bg-zinc-950/50 p-1"
            role="tablist"
            aria-label="登录或注册"
          >
            <button
              type="button"
              role="tab"
              :aria-selected="mode === 'login'"
              class="rounded-[calc(var(--radius-ui)-2px)] px-3 py-2 text-sm font-medium transition-[transform,colors] duration-200 [transition-timing-function:var(--ease-ui)] active:scale-[0.98]"
              :class="
                mode === 'login'
                  ? 'bg-emerald-600/90 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]'
                  : 'text-zinc-400 hover:text-zinc-200'
              "
              :disabled="loading"
              @click="setMode('login')"
            >
              登录
            </button>
            <button
              type="button"
              role="tab"
              :aria-selected="mode === 'register'"
              class="rounded-[calc(var(--radius-ui)-2px)] px-3 py-2 text-sm font-medium transition-[transform,colors] duration-200 [transition-timing-function:var(--ease-ui)] active:scale-[0.98]"
              :class="
                mode === 'register'
                  ? 'bg-emerald-600/90 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.12)]'
                  : 'text-zinc-400 hover:text-zinc-200'
              "
              :disabled="loading"
              @click="setMode('register')"
            >
              注册
            </button>
          </div>

          <form class="space-y-5" @submit.prevent="onSubmit">
            <UiInput
              v-model="username"
              label="账户名"
              placeholder="请输入账户名"
              autocomplete="username"
              :disabled="loading"
              :error-message="usernameError ?? undefined"
            />
            <UiInput
              v-model="password"
              :label="isRegister ? '口令（至少 8 位）' : '密码'"
              type="password"
              :placeholder="isRegister ? '设置登录口令' : '请输入密码'"
              :autocomplete="isRegister ? 'new-password' : 'current-password'"
              :disabled="loading"
              :error-message="passwordError ?? undefined"
            />
            <UiInput
              v-if="isRegister"
              v-model="confirmPassword"
              label="确认口令"
              type="password"
              placeholder="再次输入口令"
              autocomplete="new-password"
              :disabled="loading"
              :error-message="confirmPasswordError ?? undefined"
            />

            <div
              v-if="errorMsg"
              class="rounded-[var(--radius-ui)] border border-rose-900/60 bg-rose-950/35 px-3 py-2 text-sm text-rose-100"
              role="alert"
            >
              {{ errorMsg }}
            </div>

            <UiButton type="submit" class="w-full" :disabled="loading" :loading="loading">
              {{
                loading
                  ? isRegister
                    ? '注册中…'
                    : '登录中…'
                  : isRegister
                    ? '创建并进入控制台'
                    : '登录'
              }}
            </UiButton>
          </form>

          <p class="mt-6 text-center text-xs leading-relaxed text-slate-600 md:text-left">
            <template v-if="mode === 'login'">
              开发环境凭据见服务端
              <code class="text-zinc-500">CHAINUP_AGENT_ADMIN_PANEL_*</code>
            </template>
            <template v-else>
              env 模式不支持注册；database 模式需已执行迁移。第二张账号需
              <code class="text-zinc-500">OPEN_REGISTRATION</code>
              或 seed CLI。
            </template>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
