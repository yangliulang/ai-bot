/**
 * Vue Router · 控制台路由（含登录与鉴权守卫）
 *
 * 作者: 杨永的Agent
 * 日期: 2026-05-19
 * 修改功能: 路由懒加载顶部进度条（按 route name 缓存已加载 chunk，再次进入不显示）
 * 日期: 2026-05-19
 * 修改功能: 移除运维联调路由（agent-runtime-probe · spot 闪兑/限价/委托撤单）；旧路径重定向执行记录
 * 日期: 2026-05-18
 * 修改功能: **`/prompts/editor/:promptPackId`**（`PromptPackEditorPage` · 与产品原型对齐）
 * 日期: 2026-05-13
 * 修改功能: 模型配置 `/ai-settings` 接入真实 `AiSettingsPage`（GET/PATCH /admin/ai/defaults）
 * 日期: 2026-05-13
 * 修改功能: 实例管理：/agents/instances 列表与 /agents/instances/:instanceId 详情（admin/agents API）
 * 日期: 2026-05-13
 * 修改功能: 移除 /system/telegram-trading-bindings（改由实例列表展示）；旧路径重定向至 /agents/instances
 */

import { createRouter, createWebHistory } from 'vue-router'
import type { RouteLocationNormalized, RouteLocationNormalizedLoaded } from 'vue-router'

import {
  abortRouteTopLoading,
  finishRouteTopLoading,
  markRouteChunkReady,
  routeLoadingKey,
  shouldShowRouteTopLoading,
  startRouteTopLoading,
} from '@/shared/lib/route-top-loading'
import AdminLayout from '@/shared/ui/AdminLayout.vue'
import { useAuthStore } from '@/stores/auth'

let routeTopLoadingActive = false

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'auth.login',
      component: () => import('@/pages/auth/LoginPage.vue'),
      meta: { title: '登录', requiresAuth: false },
    },
    {
      path: '/',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/runtime/executions' },
        {
          path: 'runtime/executions',
          name: 'runtime.executions',
          component: () => import('@/pages/runtime/ExecutionListPage.vue'),
          meta: { title: '执行记录' },
        },
        {
          path: 'runtime/executions/:executionId',
          name: 'runtime.execution-detail',
          component: () => import('@/pages/runtime/ExecutionDetailPage.vue'),
          meta: { title: '执行详情' },
        },
        { path: 'runtime/tasks', redirect: '/runtime/executions' },
        { path: 'runtime/events', redirect: '/runtime/executions' },
        {
          path: 'agents/instances',
          name: 'agents.instances',
          component: () => import('@/pages/agents/AgentInstancesListPage.vue'),
          meta: {
            title: '实例管理',
            pageId: 'ai.agents-instances',
          },
        },
        {
          path: 'agents/instances/:instanceId',
          name: 'agents.instance-detail',
          component: () => import('@/pages/agents/AgentInstanceDetailPage.vue'),
          meta: { title: '实例详情', pageId: 'ai.agents-instance-detail' },
        },
        { path: 'agents/config', redirect: '/agents/instances' },
        { path: 'agents/config/:configId', redirect: '/agents/instances' },
        { path: 'agents/templates', redirect: '/agents/instances' },
        { path: 'agents/templates/:templateId', redirect: '/agents/instances' },
        {
          path: 'prompts/strategy',
          name: 'prompts.strategy',
          component: () => import('@/pages/prompts/PromptStrategyPage.vue'),
          meta: { title: '提示词治理', pageId: 'ai.prompt-strategy' },
        },
        {
          path: 'prompts/editor/:promptPackId',
          name: 'prompts.editor',
          component: () => import('@/pages/prompts/PromptPackEditorPage.vue'),
          meta: {
            title: 'Prompt Pack 编辑器',
            pageId: 'ai.prompt-pack-editor',
          },
        },
        { path: 'prompts', redirect: '/prompts/strategy' },
        { path: 'prompts/system', redirect: '/prompts/strategy' },
        { path: 'prompts/scenarios', redirect: '/prompts/strategy' },
        {
          path: 'prompts/safety',
          name: 'prompts.safety',
          component: () => import('@/pages/prompts/PromptSafetyPage.vue'),
          meta: { title: '安全防护', pageId: 'ai.prompt-safety' },
        },
        {
          path: 'ai/runtime-orchestration',
          component: () => import('@/pages/orchestration/RuntimeOrchestrationPage.vue'),
          meta: { title: '运行场景' },
        },
        {
          path: 'ai/tool-registry',
          name: 'ai.tool-registry',
          component: () => import('@/pages/ai/ToolRegistryPage.vue'),
          meta: { title: '技能与工具', pageId: 'ai.tool-registry' },
        },
        { path: 'ai/skill-specs', redirect: '/ai/tool-registry' },
        { path: 'tools/registry', redirect: '/ai/tool-registry' },
        { path: 'tools', redirect: '/ai/tool-registry' },
        { path: 'ai/tool-policies', redirect: '/ai/tool-registry' },
        {
          path: 'ai/confirmation-rules',
          name: 'ai.confirmation-rules',
          component: () => import('@/pages/confirmation/ConfirmationRulesPage.vue'),
          meta: { title: '人工确认规则', pageId: 'ai.confirmation-rules' },
        },
        {
          path: 'ai/confirmation-rules/new',
          name: 'ai.confirmation-rules.new',
          component: () => import('@/pages/confirmation/ConfirmationRuleEditorPage.vue'),
          meta: { title: '新建确认规则', pageId: 'ai.confirmation-rules.editor' },
        },
        {
          path: 'ai/confirmation-rules/edit/:ruleId',
          name: 'ai.confirmation-rules.edit',
          component: () => import('@/pages/confirmation/ConfirmationRuleEditorPage.vue'),
          meta: { title: '编辑确认规则', pageId: 'ai.confirmation-rules.editor' },
        },
        {
          path: 'access',
          component: () => import('@/pages/access/AccessPage.vue'),
          meta: { title: '准入管理' },
        },
        { path: 'access/eligibility', redirect: '/access' },
        { path: 'trading-config', redirect: '/access' },
        {
          path: 'billing',
          redirect: '/billing/overview',
        },
        {
          path: 'billing/overview',
          component: () => import('@/pages/ModulePlaceholderPage.vue'),
          meta: {
            title: '计费总览',
            pageId: 'billing.overview',
            hint: '第五阶段计费与 Runtime 用量大盘；待 billing-admin 联调。',
          },
        },
        {
          path: 'billing/pricing',
          component: () => import('@/pages/ModulePlaceholderPage.vue'),
          meta: { title: '定价与策略', pageId: 'billing.pricing' },
        },
        {
          path: 'billing/ledger',
          component: () => import('@/pages/ModulePlaceholderPage.vue'),
          meta: { title: '执行账单', pageId: 'billing.ledger' },
        },
        {
          path: 'observability/runtime-health',
          redirect: '/observability',
        },
        {
          path: 'observability/alerts',
          redirect: '/observability',
        },
        {
          path: 'observability',
          name: 'observability.overview',
          component: () => import('@/pages/observability/ObservabilityPage.vue'),
          meta: {
            title: '执行链路协查',
            pageId: 'obs.traces-logs',
          },
        },
        {
          path: 'integrations/telegram',
          redirect: '/system/channels/telegram',
        },
        {
          path: 'integrations/exchange-apis',
          redirect: '/system/channels',
        },
        {
          path: 'integrations/llm-providers',
          redirect: '/ai-settings',
        },
        { path: 'integrations', redirect: '/system/channels' },
        {
          path: 'system/channels',
          component: () => import('@/pages/system/ChannelsListPage.vue'),
          meta: { title: '渠道管理' },
        },
        {
          path: 'system/channels/telegram',
          component: () => import('@/pages/system/TelegramChannelDetailPage.vue'),
          meta: { title: 'Telegram · Bot 接入', pageId: 'sys.channels' },
        },
        {
          path: 'system/channels/:channelId',
          component: () => import('@/pages/system/ChannelDetailPage.vue'),
          meta: { title: '渠道详情' },
        },
        {
          path: 'system/telegram-trading-bindings',
          redirect: '/agents/instances',
        },
        {
          path: 'system/agent-runtime-probe',
          redirect: '/runtime/executions',
        },
        {
          path: 'system/spot-flash-convert',
          redirect: '/runtime/executions',
        },
        {
          path: 'system/spot-limit-order',
          redirect: '/runtime/executions',
        },
        {
          path: 'system/spot-open-orders',
          redirect: '/runtime/executions',
        },
        {
          path: 'system/ui-playground',
          component: () => import('@/pages/system/UiPlaygroundPage.vue'),
          meta: { title: 'UI 试跑' },
        },
        {
          path: 'system/feature-flags',
          redirect: '/runtime/executions',
        },
        {
          path: 'system/contract-closure',
          redirect: '/runtime/executions',
        },
        {
          path: 'system/global-gate',
          redirect: '/runtime/executions',
        },
        {
          path: 'ai-settings',
          component: () => import('@/pages/ai/AiSettingsPage.vue'),
          meta: {
            title: '模型配置',
            pageId: 'ai.settings',
          },
        },
      ],
    },
  ],
})

function armRouteTopLoadingIfNeeded(
  to: RouteLocationNormalized,
  from: RouteLocationNormalizedLoaded,
): void {
  routeTopLoadingActive = shouldShowRouteTopLoading(to, from)
  if (routeTopLoadingActive) startRouteTopLoading()
}

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  auth.hydrateFromStorage()

  const onLoginPage = to.name === 'auth.login'

  if (onLoginPage) {
    if (auth.isAuthenticated) {
      const redirect = typeof to.query.redirect === 'string' && to.query.redirect.startsWith('/')
        ? to.query.redirect
        : '/runtime/executions'
      next({ path: redirect, replace: true })
      return
    }
    armRouteTopLoadingIfNeeded(to, from)
    next()
    return
  }

  if (!auth.isAuthenticated) {
    next({ path: '/login', query: { redirect: to.fullPath }, replace: true })
    return
  }

  armRouteTopLoadingIfNeeded(to, from)
  next()
})

router.afterEach((to) => {
  markRouteChunkReady(routeLoadingKey(to))
  if (routeTopLoadingActive) {
    finishRouteTopLoading()
    routeTopLoadingActive = false
  }

  const title = typeof to.meta.title === 'string' ? to.meta.title : '控制台'
  document.title = `${title} · AI Agent`
})

router.onError(() => {
  abortRouteTopLoading()
  routeTopLoadingActive = false
})

export default router
