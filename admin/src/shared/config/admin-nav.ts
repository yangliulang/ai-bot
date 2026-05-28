import type { AdminNavIconKey } from '@/assets/icons/admin-nav/keys'

export type AdminNavModule =
  | 'runtime'
  | 'aiGovernance'
  | 'userAccess'
  | 'billing'
  | 'observability'
  | 'systemConfig'

export const ADMIN_MENU_MODULE_LABELS: Record<AdminNavModule, string> = {
  runtime: 'Runtime 洞察',
  aiGovernance: 'AI 治理',
  userAccess: '用户与准入',
  billing: '计费与账务',
  observability: '日志与监控',
  systemConfig: '系统与配置',
}

export const ADMIN_NAV_MODULE_ORDER: AdminNavModule[] = [
  'runtime',
  'aiGovernance',
  'userAccess',
  'billing',
  'observability',
  'systemConfig',
]

export interface AdminNavLeaf {
  path: string
  label: string
  pageId: string
  module: AdminNavModule
  /** 对应 `src/assets/icons/admin-nav/<name>.svg` */
  iconKey: AdminNavIconKey
}

/** 与 product-doc `admin-console/demo-routing` 同构的侧栏叶子（TG-BOT-Admin）
日期: 2026-05-19 修改功能: 移除运维联调侧栏（运行时探针 · 现货闪兑/限价/委托撤单）
日期: 2026-05-13 修改功能: 移除「TG 交易绑定」侧栏项（并入实例管理） */
export const ADMIN_NAV_LEAVES: AdminNavLeaf[] = [
  {
    path: '/runtime/executions',
    label: '执行记录',
    pageId: 'runtime.executions',
    module: 'runtime',
    iconKey: 'executions',
  },
  {
    path: '/agents/instances',
    label: '实例管理',
    pageId: 'ai.agents-instances',
    module: 'aiGovernance',
    iconKey: 'instances',
  },
  {
    path: '/prompts/strategy',
    label: '提示词治理',
    pageId: 'ai.prompt-strategy',
    module: 'aiGovernance',
    iconKey: 'prompts',
  },
  {
    path: '/ai/tool-registry',
    label: '技能与工具',
    pageId: 'ai.tool-registry',
    module: 'aiGovernance',
    iconKey: 'tool-registry',
  },
  {
    path: '/ai/runtime-orchestration',
    label: '运行场景',
    pageId: 'ai.runtime-orchestration',
    module: 'aiGovernance',
    iconKey: 'orchestration',
  },
  {
    path: '/ai/confirmation-rules',
    label: '人工确认规则',
    pageId: 'ai.confirmation-rules',
    module: 'aiGovernance',
    iconKey: 'confirmation',
  },
  {
    path: '/prompts/safety',
    label: '安全防护',
    pageId: 'ai.prompt-safety',
    module: 'aiGovernance',
    iconKey: 'safety',
  },
  {
    path: '/access',
    label: '准入管理',
    pageId: 'access.overview',
    module: 'userAccess',
    iconKey: 'access',
  },
  {
    path: '/billing/overview',
    label: '计费总览',
    pageId: 'billing.overview',
    module: 'billing',
    iconKey: 'billing-overview',
  },
  {
    path: '/billing/pricing',
    label: '定价与策略',
    pageId: 'billing.pricing',
    module: 'billing',
    iconKey: 'billing-pricing',
  },
  {
    path: '/billing/ledger',
    label: '执行账单',
    pageId: 'billing.ledger',
    module: 'billing',
    iconKey: 'billing-ledger',
  },
  {
    path: '/observability',
    label: '执行链路协查',
    pageId: 'obs.traces-logs',
    module: 'observability',
    iconKey: 'observability',
  },
  {
    path: '/system/channels',
    label: '渠道管理',
    pageId: 'sys.channels',
    module: 'systemConfig',
    iconKey: 'channels',
  },
  {
    path: '/ai-settings',
    label: '模型配置',
    pageId: 'ai.settings',
    module: 'systemConfig',
    iconKey: 'settings',
  },
]

export function navLeavesByModule(mod: AdminNavModule): AdminNavLeaf[] {
  return ADMIN_NAV_LEAVES.filter((l) => l.module === mod)
}
