/*
作者: 杨永的Agent
日期: 2026-05-12
修改功能: C 端 ky 实例；前缀与后端联调对齐（Vite proxy /api）
日期: 2026-05-15
修改功能: 请求 ID 在非安全上下文（如局域网 HTTP）下 `randomUUID` 不可用时回退，避免 beforeRequest 抛错
*/
import ky from 'ky'

const prefixUrl = (import.meta.env.VITE_API_BASE_URL ?? '/api').replace(/\/$/, '')

function createRequestId(): string {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return crypto.randomUUID()
    }
  } catch {
    /* Secure context 不可用或实现异常 */
  }
  return `req-${Date.now()}-${Math.random().toString(36).slice(2, 12)}`
}

export const httpClient = ky.create({
  prefixUrl,
  timeout: 30_000,
  retry: { limit: 0 },
  hooks: {
    beforeRequest: [
      (request) => {
        request.headers.set('x-request-id', createRequestId())
      },
    ],
  },
})
