import { adminMenuModuleLabels } from "../copy/adminNaming";

/**
 * 与 specs/requirements/admin-console/demo-routing.md、sitemap.md 同源。
 * 侧栏：**一级模块分组**（Menu `group`）+ 其下**扁平叶子**；路由与 PRD 功能域叙事解耦。
 */
export type AdminNavModule = keyof typeof adminMenuModuleLabels;

export interface AdminNavLeaf {
  path: string;
  label: string;
  pageId: string;
  module: AdminNavModule;
  /** 顶栏搜索：同义词 / 英文 / 缩写 */
  keywords: string[];
}

/** 模块分组顺序与 sitemap 一级导航一致 */
export const ADMIN_NAV_MODULE_ORDER: AdminNavModule[] = [
  "runtime",
  "aiGovernance",
  "userAccess",
  "billing",
  "observability",
  "systemConfig",
];

export const ADMIN_NAV_LEAVES: AdminNavLeaf[] = [
  {
    path: "/runtime/executions",
    label: "执行记录",
    pageId: "runtime.executions",
    module: "runtime",
    keywords: [
      "编排",
      "execution",
      "运行",
      "列表",
      "执行",
      "任务",
      "队列",
      "task",
      "queue",
      "事件",
      "event",
      "trace",
    ],
  },
  {
    path: "/agents/instances",
    label: "实例管理",
    pageId: "ai.agents-instances",
    module: "aiGovernance",
    keywords: ["实例", "实例管理", "instance", "agent", "I02", "Runtime", "生命周期"],
  },
  {
    path: "/prompts/strategy",
    label: "提示词治理",
    pageId: "ai.prompt-strategy",
    module: "aiGovernance",
    keywords: [
      "prompt",
      "提示",
      "提示词治理",
      "草稿",
      "编辑器",
      "Publish",
      "版本",
      "冻结",
      "system",
      "trading",
    ],
  },
  {
    path: "/ai/tool-registry",
    label: "技能与工具",
    pageId: "ai.tool-registry",
    module: "aiGovernance",
    keywords: [
      "技能",
      "工具",
      "skillId",
      "toolId",
      "registry",
      "登记",
      "FR-TS07",
      "FR-T11",
      "read_skill",
      "read_skill_operation_spec",
      "skill-specs",
      "操作规范",
      "contract-complete",
      "FR-T11",
      "trade-assistance",
      "模块三",
      "Tool Management",
    ],
  },
  {
    path: "/ai/runtime-orchestration",
    label: "运行场景",
    pageId: "ai.runtime-orchestration",
    module: "aiGovernance",
    keywords: [
      "运行场景",
      "场景目录",
      "scenario",
      "运行编排",
      "runtime",
      "orchestration",
      "scenarioId",
      "routing",
      "routing-engine",
      "执行策略",
      "AO",
      "策略",
    ],
  },
  {
    path: "/ai/confirmation-rules",
    label: "人工确认规则",
    pageId: "ai.confirmation-rules",
    module: "aiGovernance",
    keywords: ["确认", "人机", "confirmation", "HITL"],
  },
  {
    path: "/prompts/safety",
    label: "安全防护",
    pageId: "ai.prompt-safety",
    module: "aiGovernance",
    keywords: ["安全", "安全防护", "护栏", "safety", "合规"],
  },
  {
    path: "/access",
    label: "准入管理",
    pageId: "access.overview",
    module: "userAccess",
    keywords: ["白名单", "封禁", "VIP", "准入", "access", "资格", "I02", "eligibility", "AGENT_MIN_VIP_TIER", "G01", "总闸"],
  },
  {
    path: "/billing/overview",
    label: "计费总览",
    pageId: "billing.overview",
    module: "billing",
    keywords: ["计费", "账单", "billing", "健康", "MC501", "MC506", "Token", "总览"],
  },
  {
    path: "/billing/operations",
    label: "商业运营",
    pageId: "billing.operations",
    module: "billing",
    keywords: [
      "订阅",
      "套餐",
      "资源管理",
      "计费规则",
      "资源",
      "订单",
      "消耗",
      "Commerce",
      "Capability",
      "MC509",
      "MC510",
      "加购",
    ],
  },
  {
    path: "/billing/ledger",
    label: "执行核销追踪",
    pageId: "billing.ledger",
    module: "billing",
    keywords: ["核销", "executionId", "billingTraceId", "MC503", "MC504", "退款"],
  },
  {
    path: "/observability",
    label: "执行链路协查",
    pageId: "obs.traces-logs",
    module: "observability",
    keywords: [
      "日志",
      "trace",
      "可观测",
      "检索",
      "协查",
      "executionId",
      "sessionId",
      "健康",
      "SLI",
      "堆积",
      "失败率",
      "告警",
      "异常",
      "backlog",
    ],
  },
  {
    path: "/system/channels",
    label: "渠道管理",
    pageId: "sys.channels",
    module: "systemConfig",
    keywords: ["渠道", "Telegram", "Discord", "接入", "Agent", "交互", "IM", "bot"],
  },
  {
    path: "/ai-settings",
    label: "模型配置",
    pageId: "ai.settings",
    module: "systemConfig",
    keywords: ["模型", "厂商", "OpenAI", "Claude", "DeepSeek", "目录", "Runtime", "推理", "策略", "Token", "降级", "限流"],
  },
];

export function searchAdminNav(query: string): AdminNavLeaf[] {
  const q = query.trim().toLowerCase();
  if (!q) return ADMIN_NAV_LEAVES;
  return ADMIN_NAV_LEAVES.filter((leaf) => {
    if (leaf.label.toLowerCase().includes(q)) return true;
    if (leaf.pageId.toLowerCase().includes(q)) return true;
    if (leaf.path.toLowerCase().includes(q)) return true;
    return leaf.keywords.some((k) => k.toLowerCase().includes(q));
  });
}

export function navLeafModuleLabel(leaf: AdminNavLeaf): string {
  return adminMenuModuleLabels[leaf.module];
}
