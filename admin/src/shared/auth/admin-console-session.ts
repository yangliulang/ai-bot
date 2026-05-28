/**
 * 作者: Cursor Agent
 * 日期: 2026-05-12
 * 修改功能: Admin 控制台登录 token/user 的 localStorage 键与 Bearer 401 识别（与 `auth` / `http-client` 共用）
 */

export const ADMIN_CONSOLE_LS_TOKEN = 'tg_admin_access_token'
export const ADMIN_CONSOLE_LS_USER = 'tg_admin_username'

const ADMIN_AUTH_401_CODES = new Set([
  'ADMIN_CONSOLE_AUTH_REQUIRED',
  'ADMIN_CONSOLE_ACCESS_TOKEN_EXPIRED',
  'ADMIN_CONSOLE_ACCESS_TOKEN_INVALID',
])

export function readAdminConsoleAccessToken(): string | null {
  try {
    const t = localStorage.getItem(ADMIN_CONSOLE_LS_TOKEN)?.trim()
    return t || null
  } catch {
    return null
  }
}

export function clearAdminConsoleSessionStorage(): void {
  try {
    localStorage.removeItem(ADMIN_CONSOLE_LS_TOKEN)
    localStorage.removeItem(ADMIN_CONSOLE_LS_USER)
  } catch {
    /* ignore */
  }
}

export function adminApiPathname(path: string): boolean {
  return path.includes('/v1/admin/')
}

export function isAdminConsoleAuthLogout401(status: number, body: unknown): boolean {
  if (status !== 401) return false
  if (body === null || typeof body !== 'object') return false
  const code = 'code' in body && typeof (body as { code: unknown }).code === 'string'
    ? (body as { code: string }).code
    : ''
  return ADMIN_AUTH_401_CODES.has(code)
}
