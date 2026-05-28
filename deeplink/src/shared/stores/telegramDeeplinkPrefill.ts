/*
作者: 杨永的Agent
日期: 2026-05-11
修改功能: Telegram Phase1 预填 Pinia + sessionStorage（首页 / 任意路由带 tg_* 落库，供后续页面）
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'

import {
  emptyTelegramDeeplinkPrefill,
  mergeTelegramDeeplinkPrefill,
  telegramDeeplinkPrefillFromRouteQuery,
  type TelegramDeeplinkPrefill,
} from '@/shared/lib/onboarding'

const STORAGE_KEY = 'chainup-deeplink-tg-prefill-v1'

function readSession(): TelegramDeeplinkPrefill {
  const fallback = emptyTelegramDeeplinkPrefill()
  if (typeof sessionStorage === 'undefined') return fallback
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return fallback
    const o = JSON.parse(raw) as Record<string, unknown>
    return mergeTelegramDeeplinkPrefill(fallback, {
      tgId: typeof o.tgId === 'string' ? o.tgId : '',
      tgUsername: typeof o.tgUsername === 'string' ? o.tgUsername : '',
      firstName: typeof o.firstName === 'string' ? o.firstName : '',
      lastName: typeof o.lastName === 'string' ? o.lastName : '',
      languageCode: typeof o.languageCode === 'string' ? o.languageCode : '',
    })
  } catch {
    return fallback
  }
}

function persist(p: TelegramDeeplinkPrefill) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(p))
  } catch {
    // ignore quota / private mode
  }
}

function hasAnyField(p: TelegramDeeplinkPrefill): boolean {
  return Boolean(p.tgId || p.tgUsername || p.firstName || p.lastName || p.languageCode)
}

export const useTelegramDeeplinkPrefillStore = defineStore('telegramDeeplinkPrefill', () => {
  const prefill = ref<TelegramDeeplinkPrefill>(readSession())

  /** 从路由 query 合并进会话态并写 sessionStorage（至少一个 tg_* 非空时写入）. */
  function applyFromRouteQuery(query: Record<string, unknown>) {
    const patch = telegramDeeplinkPrefillFromRouteQuery(query)
    if (!hasAnyField(patch)) return
    prefill.value = mergeTelegramDeeplinkPrefill(prefill.value, patch)
    persist(prefill.value)
  }

  /** 联调或用户主动清除（一般不需要）. */
  function clear() {
    prefill.value = emptyTelegramDeeplinkPrefill()
    try {
      sessionStorage.removeItem(STORAGE_KEY)
    } catch {
      // ignore
    }
  }

  return { prefill, applyFromRouteQuery, clear }
})
