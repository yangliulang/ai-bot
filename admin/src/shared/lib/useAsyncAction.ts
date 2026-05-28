// 作者: 杨永的Agent
// 日期: 2026-05-11
// 修改功能: useAsyncAction — 异步请求进行中忽略重复触发（与 UiButton loading 配合；Toast 见 useAdminAction / admin-toast）

/**
 * 异步操作：进行中自动忽略重复触发（防连点），便于与 loading 态配合。
 * 需要更短间隔节流时可后续扩展 minInterval。
 */

import { ref } from 'vue'

export function useAsyncAction<A extends unknown[], R>(
  fn: (...args: A) => Promise<R>,
) {
  const loading = ref(false)

  async function run(...args: A): Promise<R | undefined> {
    if (loading.value) return undefined
    loading.value = true
    try {
      return await fn(...args)
    } finally {
      loading.value = false
    }
  }

  return { loading, run }
}
