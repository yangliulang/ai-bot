/**
 * 路由懒加载顶部进度条：仅首次进入某命名路由时展示，chunk 就绪后缓存不再显示。
 *
 * 作者: 杨永的Agent
 * 日期: 2026-05-19
 * 修改功能: 全局 route top loading（按 route name 记忆已加载 chunk）
 */

import { ref } from 'vue'
import type { RouteLocationNormalized } from 'vue-router'

/** 0–100，供进度条 scaleX */
export const routeTopLoadingVisible = ref(false)
export const routeTopLoadingProgress = ref(0)

const readyRouteKeys = new Set<string | symbol>()

let trickleTimer: ReturnType<typeof setInterval> | null = null
let hideTimer: ReturnType<typeof setTimeout> | null = null

function clearTimers(): void {
  if (trickleTimer != null) {
    clearInterval(trickleTimer)
    trickleTimer = null
  }
  if (hideTimer != null) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

/** 以 `route.name` 为主键，未命名路由回退到 matched 叶子 path */
export function routeLoadingKey(to: RouteLocationNormalized): string | symbol | null {
  const name = to.name
  if (name != null && name !== '') return name
  const leaf = to.matched[to.matched.length - 1]
  return leaf?.path ?? null
}

export function isRouteChunkReady(key: string | symbol): boolean {
  return readyRouteKeys.has(key)
}

export function markRouteChunkReady(key: string | symbol | null): void {
  if (key != null) readyRouteKeys.add(key)
}

export function shouldShowRouteTopLoading(
  to: RouteLocationNormalized,
  from: RouteLocationNormalized,
): boolean {
  if (to.fullPath === from.fullPath) return false
  const key = routeLoadingKey(to)
  if (key == null) return false
  return !isRouteChunkReady(key)
}

export function startRouteTopLoading(): void {
  clearTimers()
  routeTopLoadingProgress.value = 0
  routeTopLoadingVisible.value = true
  requestAnimationFrame(() => {
    routeTopLoadingProgress.value = 14
  })
  trickleTimer = setInterval(() => {
    const current = routeTopLoadingProgress.value
    if (current >= 90) return
    const step = current < 45 ? 10 : current < 72 ? 5 : 2
    routeTopLoadingProgress.value = Math.min(90, current + step)
  }, 180)
}

export function finishRouteTopLoading(): void {
  if (trickleTimer != null) {
    clearInterval(trickleTimer)
    trickleTimer = null
  }
  if (!routeTopLoadingVisible.value) return
  routeTopLoadingProgress.value = 100
  hideTimer = setTimeout(() => {
    routeTopLoadingVisible.value = false
    routeTopLoadingProgress.value = 0
    hideTimer = null
  }, 260)
}

export function abortRouteTopLoading(): void {
  clearTimers()
  routeTopLoadingVisible.value = false
  routeTopLoadingProgress.value = 0
}
