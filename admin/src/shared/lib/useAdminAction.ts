// 作者: 杨永的Agent
// 日期: 2026-05-22
// 修改功能: 异步操作 + UiButton loading + 全局 Toast（与 useAsyncAction 配套）

import { ref, type Ref } from 'vue'

import {
  adminToastError,
  adminToastSuccess,
  resolveAdminActionErrorMessage,
} from '@/shared/lib/admin-toast'

export type AdminActionToastOptions<R> = {
  /** 成功后 Toast；省略则不提示 */
  successMessage?: string | ((result: R) => string)
  /** 失败后 Toast；省略则用 AppError / 操作失败 */
  errorMessage?: string | ((err: unknown) => string)
  /** 为 false 时不弹出失败 Toast（仍返回 undefined） */
  toastOnError?: boolean
}

/**
 * 包装异步操作：防连点 loading、可选成功/失败全局 Toast。
 * 与 `UiButton` 的 `:loading` 绑定 `loading` 即可。
 */
export function useAdminAction<A extends unknown[], R>(
  fn: (...args: A) => Promise<R>,
  options?: AdminActionToastOptions<R>,
) {
  const loading = ref(false)

  async function run(...args: A): Promise<R | undefined> {
    if (loading.value) return undefined
    loading.value = true
    try {
      const result = await fn(...args)
      if (options?.successMessage) {
        const msg =
          typeof options.successMessage === 'function'
            ? options.successMessage(result)
            : options.successMessage
        adminToastSuccess(msg)
      }
      return result
    } catch (err) {
      if (options?.toastOnError !== false) {
        const msg =
          typeof options?.errorMessage === 'function'
            ? options.errorMessage(err)
            : options?.errorMessage ?? resolveAdminActionErrorMessage(err)
        adminToastError(msg)
      }
      return undefined
    } finally {
      loading.value = false
    }
  }

  return { loading, run }
}

/** 已有 `loading` ref 时的一次性包装（如组合多个子请求） */
export async function runWithAdminToast<R>(
  loading: Ref<boolean>,
  fn: () => Promise<R>,
  options?: AdminActionToastOptions<R>,
): Promise<R | undefined> {
  if (loading.value) return undefined
  loading.value = true
  try {
    const result = await fn()
    if (options?.successMessage) {
      const msg =
        typeof options.successMessage === 'function'
          ? options.successMessage(result)
          : options.successMessage
      adminToastSuccess(msg)
    }
    return result
  } catch (err) {
    if (options?.toastOnError !== false) {
      const msg =
        typeof options?.errorMessage === 'function'
          ? options.errorMessage(err)
          : (options?.errorMessage ?? resolveAdminActionErrorMessage(err))
      adminToastError(msg)
    }
    return undefined
  } finally {
    loading.value = false
  }
}
