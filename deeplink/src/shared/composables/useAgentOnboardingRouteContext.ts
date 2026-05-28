/*
作者: 杨永的Agent
日期: 2026-05-12
修改功能: onboarding 多页共用：Telegram 卡展示、bdeeplink token、Bot 打开 URL（与路由 query / 预填 store 对齐）
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { useEffectiveTelegramDeeplinkPrefill } from '@/shared/composables/useEffectiveTelegramDeeplinkPrefill'
import {
  normalizeTelegramUsername,
  telegramBotOpenUrlFromSearch,
  telegramDisplayHandleFromPrefill,
} from '@/shared/lib/onboarding'

function firstQueryParam(raw: unknown): string {
  if (raw == null) return ''
  if (Array.isArray(raw)) return String(raw[0] ?? '').trim()
  return String(raw).trim()
}

export function pickAgentOnboardingDeeplinkToken(q: Record<string, unknown>): string | undefined {
  const keys = ['deeplink_token', 'bind_token', 'token', 'confirm_token'] as const
  for (const k of keys) {
    const v = firstQueryParam(q[k])
    if (v) return v
  }
  return undefined
}

export function useAgentOnboardingRouteContext() {
  const route = useRoute()
  const effectivePrefill = useEffectiveTelegramDeeplinkPrefill()

  const legacyTgUsernameNormalized = computed(() => {
    const fromQuery =
      firstQueryParam(route.query.tg_username) ||
      firstQueryParam(route.query.telegram_username) ||
      firstQueryParam(route.query.tg_user)
    return fromQuery ? normalizeTelegramUsername(fromQuery) : ''
  })

  const legacyUsernamePlain = computed(() => legacyTgUsernameNormalized.value.replace(/^@/, ''))

  const tgDisplayHandle = computed(() =>
    telegramDisplayHandleFromPrefill(effectivePrefill.value, legacyTgUsernameNormalized.value),
  )

  const tgCardPrimary = computed(() => {
    const h = tgDisplayHandle.value.trim()
    if (h) return h
    const p = effectivePrefill.value
    const name = [p.firstName, p.lastName].filter(Boolean).join(' ').trim()
    if (name) return name
    return ''
  })

  const hasTgIdentity = computed(() => Boolean(tgCardPrimary.value.trim()))

  const tgProfileSummary = computed(() => {
    const p = effectivePrefill.value
    const name = [p.firstName, p.lastName].filter(Boolean).join(' ').trim()
    if (name && p.languageCode) return `${name} · ${p.languageCode}`
    if (name) return name
    if (p.languageCode) return `语言 · ${p.languageCode}`
    return ''
  })

  const showTgProfileMeta = computed(() => {
    const summary = tgProfileSummary.value.trim()
    if (!summary) return false
    const primary = tgCardPrimary.value.trim()
    if (!primary) return true
    if (primary.startsWith('@') || primary.startsWith('TG id ')) return true
    return summary !== primary
  })

  const telegramBotOpenUrl = computed(() => {
    const sp = new URLSearchParams()
    const fromQ = firstQueryParam(route.query.tg_bot)
    if (fromQ) sp.set('tg_bot', fromQ)
    return telegramBotOpenUrlFromSearch(sp)
  })

  const deeplinkToken = computed(() => pickAgentOnboardingDeeplinkToken(route.query as Record<string, unknown>))

  return {
    route,
    effectivePrefill,
    legacyUsernamePlain,
    tgCardPrimary,
    hasTgIdentity,
    tgProfileSummary,
    showTgProfileMeta,
    telegramBotOpenUrl,
    deeplinkToken,
  }
}
