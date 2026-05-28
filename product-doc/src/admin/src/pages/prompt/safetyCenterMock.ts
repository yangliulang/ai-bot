/** 演示：安全拦截流水（非持久化） */

export type SafetyInterceptCategory = "runtime" | "prompt" | "tool" | "session";

export interface SafetyInterceptRow {
  id: string;
  timeLabel: string;
  category: SafetyInterceptCategory;
  /** 业务场景（运营可读） */
  scenarioLabel: string;
  kindLabel: string;
  reason: string;
  subject?: string;
}

export const MOCK_SAFETY_INTERCEPTS: SafetyInterceptRow[] = [
  {
    id: "int-1",
    timeLabel: "今日 12:01",
    category: "runtime",
    scenarioLabel: "合约交易 · 杠杆调整",
    kindLabel: "高杠杆",
    reason: "目标杠杆超过策略上限（20×）",
    subject: "UID ****821",
  },
  {
    id: "int-2",
    timeLabel: "今日 13:22",
    category: "prompt",
    scenarioLabel: "助手对话",
    kindLabel: "Prompt Injection",
    reason: "检测到越狱/注入模式，已阻断助手回复",
    subject: "会话 S-9f2a",
  },
  {
    id: "int-3",
    timeLabel: "今日 14:05",
    category: "tool",
    scenarioLabel: "提现 / 资金划出",
    kindLabel: "Tool 阻断",
    reason: "命中禁止类工具路径（提现链路未授权）",
    subject: "tool.withdraw.*",
  },
  {
    id: "int-4",
    timeLabel: "昨日 18:40",
    category: "session",
    scenarioLabel: "同会话多轮下单",
    kindLabel: "高频限制",
    reason: "同会话短窗口内重复高风险意图，已限速",
    subject: "会话 S-81cd",
  },
];

/** 工具管控：处置口径 + 生效模式（运营语义） */
export type ToolEnforcementMode = "default_deny" | "allowlist_only" | "approve_then_allow";

export interface ToolSafetyPolicyRow {
  key: string;
  toolPattern: string;
  /** 处置口径（摘要） */
  policy: "deny" | "allowlist" | "shadow";
  /** 生效模式：默认拒绝 / 仅白名单 / 审批后允许 */
  enforcementMode: ToolEnforcementMode;
  note: string;
}

export const TOOL_ENFORCEMENT_LABEL: Record<ToolEnforcementMode, string> = {
  default_deny: "默认拒绝",
  allowlist_only: "白名单",
  approve_then_allow: "审批后允许",
};

export const MOCK_TOOL_SAFETY_POLICIES: ToolSafetyPolicyRow[] = [
  {
    key: "t1",
    toolPattern: "exchange.withdraw* · 提现类",
    policy: "deny",
    enforcementMode: "default_deny",
    note: "未明确放行的一律拒绝；禁止智能体直连提现写操作",
  },
  {
    key: "t2",
    toolPattern: "exchange.order.* · 交易写",
    policy: "allowlist",
    enforcementMode: "allowlist_only",
    note: "仅名册内工具族可调用；其余默认拒绝",
  },
  {
    key: "t3",
    toolPattern: "http.fetch · 外网",
    policy: "shadow",
    enforcementMode: "approve_then_allow",
    note: "外网访问须过风险审批与预算闸；超额或异常降级为仅旁路审计",
  },
];

/** Runtime 安全：规则维度摘要（演示，对齐风险治理字段） */
export interface RuntimeSafetyGovernanceRow {
  key: string;
  name: string;
  riskLevelLabel: string;
  autoExecSummary: string;
  confirmSummary: string;
  breakerSummary: string;
  /** 链接目标由页面拼装 */
  hrefKind: "confirmation" | "policy" | "routing";
}

export const MOCK_RUNTIME_SAFETY_GOVERNANCE: RuntimeSafetyGovernanceRow[] = [
  {
    key: "r1",
    name: "高风险交易与资金动作",
    riskLevelLabel: "高",
    autoExecSummary: "高风险写路径默认关闭自动落单",
    confirmSummary: "须命中人工确认规则（强制确认/二次确认等）",
    breakerSummary: "连续失败则停编并排障提示",
    hrefKind: "confirmation",
  },
  {
    key: "r2",
    name: "越权与非法委托",
    riskLevelLabel: "高",
    autoExecSummary: "命中即拒答，不进入下单链路",
    confirmSummary: "不适用（已拦截）",
    breakerSummary: "同意图短窗重复请求合并告警",
    hrefKind: "routing",
  },
  {
    key: "r3",
    name: "杠杆与名义限额",
    riskLevelLabel: "高",
    autoExecSummary: "超限前须人工确认或拆分委托",
    confirmSummary: "超额/高杠杆走二次确认",
    breakerSummary: "超阈自动驳回并记拦截流水",
    hrefKind: "policy",
  },
  {
    key: "r4",
    name: "自动执行熔断",
    riskLevelLabel: "中",
    autoExecSummary: "按风险限制关闭部分自动执行",
    confirmSummary: "与上行规则联动",
    breakerSummary: "失败策略：停止并通知 / 转人工（可配置）",
    hrefKind: "policy",
  },
];
