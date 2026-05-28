/*
作者: 杨永的Agent
日期: 2026-05-11
修改功能: session 预填 + 当前 route.query 合成（供多页复用）
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { effectiveTelegramPrefill } from '@/shared/lib/onboarding'
import { useTelegramDeeplinkPrefillStore } from '@/shared/stores/telegramDeeplinkPrefill'

/** 合并 Pinia 会话存留的预填与 URL query（同名字段非空时 URL 优先）. */
export function useEffectiveTelegramDeeplinkPrefill() {
  const route = useRoute()
  const store = useTelegramDeeplinkPrefillStore()
  return computed(() =>
    effectiveTelegramPrefill(store.prefill, route.query as Record<string, unknown>),
  )
}
