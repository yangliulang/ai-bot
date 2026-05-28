/**
 * 作者: Cursor Agent
 * 日期: 2026-05-12
 * 修改功能: ky 全局客户端为 `/v1/admin/*` 附加 Bearer，Admin 控制台 JWT 401 清 session 并跳转登录
 */

import ky, { type KyInstance, HTTPError } from 'ky'

import router from '@/app/router'
import { AppError } from '@/shared/api/errors'
import {
  adminApiPathname,
  isAdminConsoleAuthLogout401,
  readAdminConsoleAccessToken,
} from '@/shared/auth/admin-console-session'
import { useAuthStore } from '@/stores/auth'

function parsePrefixUrl(): string {
  const raw = import.meta.env.VITE_API_BASE_URL as string | undefined
  if (raw === undefined || raw === '') {
    return '/api'
  }
  return raw.replace(/\/$/, '')
}

/** 防止并行 401 多次 replace */
let adminConsoleAuthRedirecting = false

/**
 * 全局 HTTP 客户端：超时、前缀在一处维护。
 * - **`/api/v1/admin/*`**（ky 相对路径含 **`v1/admin/`**）：若 localStorage 有 access_token，附加 **`Authorization: Bearer`**（JWT 模式由服务端 `ADMIN_CONSOLE_JWT_SECRET` 决定）。
 * - **401** 且 body.`code` 为 `ADMIN_CONSOLE_*`：清 session 并跳转登录（见 FE_HANDOFF）。
 * 业务侧请使用 try/catch + {@link toAppError}，勿依赖 ky 内部错误类型泄漏。
 */
export function createHttpClient(): KyInstance {
  return ky.create({
    prefixUrl: parsePrefixUrl(),
    timeout: 15_000,
    retry: { limit: 0 },
    hooks: {
      beforeRequest: [
        (request) => {
          let pathname = ''
          try {
            pathname = new URL(request.url).pathname
          } catch {
            return
          }
          if (!adminApiPathname(pathname)) return
          const token = readAdminConsoleAccessToken()
          if (token) request.headers.set('Authorization', `Bearer ${token}`)
        },
      ],
      afterResponse: [
        async (_request, _options, response) => {
          if (response.status !== 401) return response
          let pathname = ''
          try {
            pathname = new URL(response.url).pathname
          } catch {
            return response
          }
          if (!adminApiPathname(pathname)) return response

          const body: unknown = await response.clone().json().catch(() => null)
          if (!isAdminConsoleAuthLogout401(response.status, body)) return response

          useAuthStore().clearSession()

          if (adminConsoleAuthRedirecting) return response
          adminConsoleAuthRedirecting = true
          const name = router.currentRoute.value.name
          const redirect =
            name !== 'auth.login' && typeof router.currentRoute.value.fullPath === 'string'
              ? router.currentRoute.value.fullPath
              : '/runtime/executions'
          if (name !== 'auth.login') {
            void router.replace({ path: '/login', query: { redirect }, replace: true }).finally(() => {
              adminConsoleAuthRedirecting = false
            })
          } else {
            adminConsoleAuthRedirecting = false
          }
          return response
        },
      ],
    },
  })
}

/** 默认导出实例，便于 feature/api 层直接引用 */
export const httpClient = createHttpClient()

export async function toAppError(error: unknown): Promise<AppError> {
  if (error instanceof AppError) {
    return error
  }
  if (error instanceof HTTPError) {
    try {
      const text = await error.response.clone().text()
      const message =
        error.response.status >= 500
          ? '服务暂时不可用，请稍后重试'
          : text && text.length > 0 && text.length < 400
            ? text
            : error.response.statusText || '请求失败'
      return new AppError(message, {
        cause: error,
        status: error.response.status,
      })
    } catch {
      return new AppError(error.response.statusText, {
        cause: error,
        status: error.response.status,
      })
    }
  }
  if (error instanceof Error) {
    return new AppError(error.message, { cause: error })
  }
  return new AppError('未知错误', { cause: error })
}
