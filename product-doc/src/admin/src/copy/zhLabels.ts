/**
 * 界面展示统一中文（底层枚举仍可英文）。未知值回退为原样便于排查。
 */

const TASK_STATE: Record<string, string> = {
  BLOCKED: "已阻塞",
  PENDING: "待处理",
  RUNNING: "执行中",
};

const EXECUTION_OUTCOME: Record<string, string> = {
  PER_EXECUTION_FINAL: "执行完成",
  BILLING_BLOCKED: "计费受阻",
  UNKNOWN: "待核对",
  FAILED: "失败",
  RUNNING: "进行中",
};

const BILLING_STATUS: Record<string, string> = {
  SUCCESS: "成功",
  FAILED: "失败",
  PENDING: "处理中",
};

const TEMPLATE_STATUS: Record<string, string> = {
  PUBLISHED: "已发布",
  DRAFT: "草稿",
  DISABLED: "已停用",
};

const AGENT_STATE: Record<string, string> = {
  NORMAL: "正常",
  BILLING_BLOCKED: "计费受限",
  GLOBAL_OFF: "总闸关闭",
  OPS_SUSPENDED: "运营熔断",
  MEMBERSHIP_BLOCKED: "会员/准入受限",
  AGENT_SUBACCOUNT_BLOCKED: "子账户受阻",
};

const RUNTIME_STATE: Record<string, string> = {
  RUNNING: "运行中",
  PAUSED: "已暂停",
  STOPPED: "已停止",
  STARTING: "启动中",
  ERROR: "异常",
};

const SUB_ACCOUNT_LINK: Record<string, string> = {
  LINKED: "已关联",
  PENDING: "待关联",
  NONE: "未关联",
};

const DEP_HEALTH: Record<string, string> = {
  ok: "正常",
  warn: "注意",
  off: "未就绪",
};

/** 依赖健康（模板页） */
export function zhDepHealth(h: string): string {
  return DEP_HEALTH[h] ?? h;
}

export function zhTaskState(s: string): string {
  return TASK_STATE[s] ?? s;
}

export function zhExecutionOutcome(s: string): string {
  return EXECUTION_OUTCOME[s] ?? s;
}

export function zhBillingStatus(s: string): string {
  return BILLING_STATUS[s] ?? s;
}

export function zhTemplateStatus(s: string): string {
  return TEMPLATE_STATUS[s] ?? s;
}

/** 提示词包 · 列表/策略页「状态」列（与 prompt-management 生命周期同窗；未知回退原文） */
export function zhPromptPackLockState(s: string): string {
  const PROMPT_PACK_LOCK: Record<string, string> = {
    DRAFT: "草稿",
    PUBLISHED: "已发布",
    LOCKED: "已锁定",
    DISABLED: "已停用",
  };
  return PROMPT_PACK_LOCK[s] ?? s;
}

/** 提示词包类型（kind / promptPackType；治理列表、新建草稿、详情等与底层英文枚举对齐；未知回退原文） */
export function zhPromptPackKind(k: string): string {
  const PROMPT_PACK_KIND: Record<string, string> = {
    SYSTEM: "系统",
    TRADING: "交易",
    ANALYSIS: "分析",
    SAFETY: "安全防护",
  };
  return PROMPT_PACK_KIND[k] ?? k;
}

export function zhAgentState(s: string): string {
  return AGENT_STATE[s] ?? s;
}

export function zhRuntimeState(s: string): string {
  return RUNTIME_STATE[s] ?? s;
}

/** 实例列表/详情：子账户绑定阶段 */
export function zhSubAccountStatus(s: string): string {
  return SUB_ACCOUNT_LINK[s] ?? s;
}

const TOOL_INVOCATION: Record<string, string> = {
  SUCCEEDED: "成功",
  FAILED: "失败",
};

const CHARGE_STATUS: Record<string, string> = {
  SETTLED: "已结算",
  REJECTED: "已拒绝",
};

export function zhToolInvocation(s: string): string {
  return TOOL_INVOCATION[s] ?? s;
}

export function zhChargeStatus(s: string): string {
  return CHARGE_STATUS[s] ?? s;
}

const TOOL_MATRIX: Record<string, string> = {
  FROZEN: "已冻结",
  TBD: "待定",
  DEFERRED: "暂缓",
};

/** 工具注册表「矩阵」状态 */
export function zhToolMatrixStatus(s: string): string {
  return TOOL_MATRIX[s] ?? s;
}

/** 供应商健康（示意） */
const PROVIDER_HEALTH: Record<string, string> = {
  OK: "正常",
  DEGRADED: "降级",
  DOWN: "不可用",
};

export function zhProviderHealth(s: string): string {
  return PROVIDER_HEALTH[s] ?? s;
}

/**
 * 执行记录列表「运行态」：与 MockObsExecutionRow.status 对齐（CREATED / RUNNING / …）。
 */
const EXECUTION_RUNTIME_STATUS: Record<string, string> = {
  CREATED: "已创建",
  RUNNING: "执行中",
  COMPLETED: "已完成",
  UNKNOWN: "待核对",
  FAILED: "执行失败",
  BLOCKED: "已阻断",
};

export function zhExecutionRuntimeStatus(s: string): string {
  return EXECUTION_RUNTIME_STATUS[s] ?? s;
}

/** 编排当前阶段（列表 / 详情展示用；未知值回退原文） */
const EXECUTION_STAGE: Record<string, string> = {
  CREATED: "已创建",
  CONFIRM_PENDING: "待确认",
  RUNNING: "执行中",
  COMPLETED: "已完成",
  BILLING_GATE: "计费闸",
  RECONCILING: "对账中",
  RECOVERING: "恢复中",
  TOOL_FAILED: "工具失败",
};

export function zhExecutionStage(s: string): string {
  return EXECUTION_STAGE[s] ?? s;
}

/** 执行详情 · 运行事件类型（点分 eventType；未知回退原文） */
const RUNTIME_EVENT_TYPE: Record<string, string> = {
  "execution.created": "执行已创建",
  "confirm.pending": "待用户确认",
  "tool.started": "工具已开始",
  "tool.succeeded": "工具已成功",
  "tool.failed": "工具已失败",
  "llm.completed": "模型调用完成",
  "billing.preflight.failed": "计费预检失败",
  "reconciliation.completed": "对账已完成",
  "order.pending": "订单待处理",
  "retry.started": "重试已开始",
};

export function zhRuntimeEventType(s: string): string {
  return RUNTIME_EVENT_TYPE[s] ?? s;
}
