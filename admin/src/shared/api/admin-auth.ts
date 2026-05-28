/**
 * 运营控制台认证 API（`POST /api/auth/login` · `POST /api/auth/register`）
 *
 * 作者: 杨永的Agent
 * 日期: 2026-05-19
 * 修改功能: database 模式自助注册与登录；错误码映射为可读文案
 */

import { AppError } from '@/shared/api/errors'

/** 与 `server` AdminLoginResponse 一致 */
export interface AdminLoginResponse {
  access_token: string
  token_type: string
  username: string
}

interface AdminAuthErrorBody {
  message?: string
  code?: string
}

const REGISTER_ERROR_MESSAGES: Record<string, string> = {
  ADMIN_CONSOLE_REGISTRATION_REQUIRES_DATABASE_AUTH:
    '当前为环境变量登录模式，无法自助注册。请使用服务端配置的账号登录，或切换为 database 认证模式。',
  ADMIN_CONSOLE_REGISTRATION_DISABLED:
    '注册已关闭：库中已有管理员且未开启开放注册。可设置 CHAINUP_AGENT_ADMIN_CONSOLE_OPEN_REGISTRATION=true，或使用 chainup-agent-seed-admin。',
  ADMIN_CONSOLE_USERNAME_ALREADY_EXISTS: '该账户名已被占用，请换一个账户名。',
  VALIDATION_ERROR: '请检查账户名与密码格式（注册口令至少 8 位）。',
}

const LOGIN_ERROR_MESSAGES: Record<string, string> = {
  ADMIN_CONSOLE_AUTH_INVALID_CREDENTIALS: '账户名或密码不正确。',
  ADMIN_CONSOLE_AUTH_DISABLED: '控制台登录未启用，请检查服务端 ADMIN_PANEL 配置。',
  ADMIN_CONSOLE_AUTH_REQUIRED: '需要登录后再访问。',
}

async function postAdminAuth(
  path: '/api/auth/login' | '/api/auth/register',
  body: Record<string, string>,
): Promise<AdminLoginResponse> {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  const data = (await res.json().catch(() => null)) as AdminLoginResponse | AdminAuthErrorBody | null

  if (res.ok && data && typeof data === 'object' && 'access_token' in data && 'username' in data) {
    const token = (data as AdminLoginResponse).access_token
    const user = (data as AdminLoginResponse).username
    if (typeof token === 'string' && token.length > 0 && typeof user === 'string' && user.length > 0) {
      return data as AdminLoginResponse
    }
  }

  const errBody = data && typeof data === 'object' ? (data as AdminAuthErrorBody) : null
  const code = typeof errBody?.code === 'string' ? errBody.code : undefined
  const serverMsg = typeof errBody?.message === 'string' ? errBody.message : undefined
  const fallback = path === '/api/auth/register' ? '注册失败' : '登录失败'
  const mapped =
    code &&
    (path === '/api/auth/register'
      ? REGISTER_ERROR_MESSAGES[code]
      : LOGIN_ERROR_MESSAGES[code])
  const message = mapped ?? serverMsg ?? `${fallback} (${res.status})`

  throw new AppError(message, { code, status: res.status })
}

export async function adminAuthLogin(username: string, password: string): Promise<AdminLoginResponse> {
  return postAdminAuth('/api/auth/login', { username: username.trim(), password })
}

export async function adminAuthRegister(
  username: string,
  password: string,
): Promise<AdminLoginResponse> {
  return postAdminAuth('/api/auth/register', { username: username.trim(), password })
}
