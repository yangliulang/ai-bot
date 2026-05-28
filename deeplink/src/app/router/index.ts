/*
作者: 杨永的Agent
日期: 2026-05-12
修改功能: onboarding 拆为 /validate · /confirm · /success；/onboarding 重定向至校验页
日期: 2026-05-12
修改功能: 首页 + 助手开通 onboarding；遗留 /telegram/binding 重定向
日期: 2026-05-11
修改功能: 全局 beforeEach 捕获 tg_* query 写入 Telegram 预填 store（sessionStorage）
 */
import { createRouter, createWebHistory } from 'vue-router'

import { useTelegramDeeplinkPrefillStore } from '@/shared/stores/telegramDeeplinkPrefill'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/pages/HomePage.vue'),
      meta: { title: '首页' },
    },
    {
      path: '/onboarding/validate',
      name: 'onboarding-validate',
      component: () => import('@/pages/onboarding/AgentOnboardingValidatePage.vue'),
      meta: { title: '开启助手 · 校验密钥' },
    },
    {
      path: '/onboarding/confirm',
      name: 'onboarding-confirm',
      component: () => import('@/pages/onboarding/AgentOnboardingConfirmPage.vue'),
      meta: { title: '开启助手 · 确认绑定' },
    },
    {
      path: '/onboarding/success',
      name: 'onboarding-success',
      component: () => import('@/pages/onboarding/AgentOnboardingSuccessPage.vue'),
      meta: { title: '开启助手 · 完成' },
    },
    {
      path: '/onboarding',
      redirect: '/onboarding/validate',
    },
    {
      path: '/telegram/binding',
      redirect: '/onboarding/validate',
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/pages/NotFoundPage.vue'),
      meta: { title: '未找到' },
    },
  ],
})

router.beforeEach((to) => {
  const store = useTelegramDeeplinkPrefillStore()
  store.applyFromRouteQuery(to.query as Record<string, unknown>)
})

router.afterEach((to) => {
  const t = to.meta.title
  if (typeof t === 'string' && t.length > 0) {
    document.title = `${t} · Agent · Coolbit`
  }
})

export default router
