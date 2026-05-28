/**
 * 控制台登录态：`POST /api/auth/login` · `POST /api/auth/register`
 *
 * 作者: 杨永的Agent
 * 日期: 2026-05-19
 * 修改功能: 注册入库账号；会话写入抽至 `admin-auth` API 模块
 */

import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { adminAuthLogin, adminAuthRegister } from '@/shared/api/admin-auth'
import {
  ADMIN_CONSOLE_LS_TOKEN,
  ADMIN_CONSOLE_LS_USER,
  clearAdminConsoleSessionStorage,
} from '@/shared/auth/admin-console-session'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>(localStorage.getItem(ADMIN_CONSOLE_LS_TOKEN))
  const username = ref<string | null>(localStorage.getItem(ADMIN_CONSOLE_LS_USER))

  const isAuthenticated = computed(() => Boolean(accessToken.value))

  function hydrateFromStorage() {
    accessToken.value = localStorage.getItem(ADMIN_CONSOLE_LS_TOKEN)
    username.value = localStorage.getItem(ADMIN_CONSOLE_LS_USER)
  }

  function setSession(token: string, user: string) {
    accessToken.value = token
    username.value = user
    localStorage.setItem(ADMIN_CONSOLE_LS_TOKEN, token)
    localStorage.setItem(ADMIN_CONSOLE_LS_USER, user)
  }

  function clearSession() {
    accessToken.value = null
    username.value = null
    clearAdminConsoleSessionStorage()
  }

  /**
   * @throws {import('@/shared/api/errors').AppError} 携带后端或网络错误信息
   */
  async function login(user: string, password: string) {
    const data = await adminAuthLogin(user, password)
    setSession(data.access_token, data.username)
  }

  /**
   * @throws {import('@/shared/api/errors').AppError} 携带后端或网络错误信息
   */
  async function register(user: string, password: string) {
    const data = await adminAuthRegister(user, password)
    setSession(data.access_token, data.username)
  }

  function logout() {
    clearSession()
  }

  return {
    accessToken,
    username,
    isAuthenticated,
    hydrateFromStorage,
    login,
    register,
    logout,
    clearSession,
  }
})
